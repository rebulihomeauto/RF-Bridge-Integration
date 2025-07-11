import logging
import json
import asyncio
from homeassistant.components import mqtt
from homeassistant.helpers.device_registry import async_get as get_dev_reg
from homeassistant.helpers.entity_platform import async_get_platforms
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from .parsers import decode_32bit_sensor
from .const import DOMAIN, MANUFACTURER, MODEL

_LOGGER = logging.getLogger(__name__)

ENTITIES = {}

async def wait_for_platform(hass, domain, retries=5, delay=0.5):
    for _ in range(retries):
        platforms = async_get_platforms(hass, domain)
        if platforms:
            return platforms[0]
        await asyncio.sleep(delay)
    return None

async def setup_mqtt(hass, config_entry):
    topic = hass.data[DOMAIN].get("mqtt_topic", "home/rebuli_rf/received")
    allowed_ids = hass.data[DOMAIN].get("allowed_ids", [])

    _LOGGER.debug(f"Subscribing to MQTT topic {topic} with allowed IDs: {allowed_ids}")

    async def message_received(msg):
        _LOGGER.debug(f"MQTT message received: {msg.payload}")
        try:
            data = json.loads(msg.payload)
            code = int(data["code"])
        except Exception as e:
            _LOGGER.warning(f"Invalid MQTT message format: {e}")
            return

        parsed = decode_32bit_sensor(code)
        _LOGGER.debug(f"Decoded RF data: {parsed}")

        if parsed is None:
            _LOGGER.warning(f"Unknown or unrecognized RF code: {code}")
            hass.bus.async_fire("rebuli_rf_bridge.unknown_code", {"code": code})
            return

        device_id = parsed["device_id"]
        sensor_type = parsed["sensor_type"]
        entity_id = f"{sensor_type}_{device_id:04X}"
        state = parsed["value"]
        auto_off = parsed.get("auto_off", False)

        allowed_ids = hass.data[DOMAIN].get("allowed_ids", [])
        if allowed_ids and f"{device_id:04X}" not in allowed_ids:
            _LOGGER.warning(f"Ignoring RF device {device_id:04X} (not in allowed list)")
            return

        if entity_id not in ENTITIES:
            platform = await wait_for_platform(hass, DOMAIN)
            if platform is None:
                _LOGGER.error("Failed to get entity platform after retries.")
                return

            if sensor_type == "binary":
                ENTITIES[entity_id] = RebuliBinarySensor(device_id, sensor_type, state, auto_off, hass)
            else:
                ENTITIES[entity_id] = RebuliSensor(device_id, sensor_type, state)

            await platform.async_add_entities([ENTITIES[entity_id]])
        else:
            ENTITIES[entity_id].update_state(state)

    await mqtt.async_subscribe(hass, topic, message_received)


class RebuliSensor(SensorEntity):
    def __init__(self, device_id, sensor_type, value):
        self._device_id = device_id
        self._sensor_type = sensor_type
        self._state = value
        self._attr_name = f"{sensor_type.capitalize()} {device_id:04X}"
        self._attr_unique_id = f"{sensor_type}_{device_id:04X}"
        self._attr_device_class = sensor_type
        self._attr_native_unit_of_measurement = _unit(sensor_type)
        self.entity_id = f"sensor.{sensor_type}_{device_id:04X}"

    @property
    def native_value(self):
        return self._state

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, f"device_{self._device_id:04X}")},
            "name": f"Rebuli RF Device {self._device_id:04X}",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    def update_state(self, value):
        self._state = value
        self.async_write_ha_state()


class RebuliBinarySensor(BinarySensorEntity):
    def __init__(self, device_id, sensor_type, value, auto_off, hass):
        self._device_id = device_id
        self._sensor_type = sensor_type
        self._state = value
        self._auto_off = auto_off
        self._hass = hass
        self._attr_name = f"{sensor_type.capitalize()} {device_id:04X}"
        self._attr_unique_id = f"{sensor_type}_{device_id:04X}"
        self._attr_device_class = sensor_type
        self.entity_id = f"binary_sensor.{sensor_type}_{device_id:04X}"

        self._auto_off_task = None  # tarefa para auto desligar

    @property
    def is_on(self):
        return self._state

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, f"device_{self._device_id:04X}")},
            "name": f"Rebuli RF Device {self._device_id:04X}",
            "manufacturer": "Rebuli",
            "model": "RF Bridge",
        }

    def update_state(self, value):
        self._state = value
        self.async_write_ha_state()

        if self._auto_off:
            # Cancela timer anterior, se existir
            if self._auto_off_task is not None:
                self._auto_off_task.cancel()
                self._auto_off_task = None

            # Se estado for ON, inicia novo timer para desligar depois
            if value:
                self._auto_off_task = asyncio.create_task(self._auto_reset())

    async def _auto_reset(self):
        timeout = self._hass.data[DOMAIN].get("auto_off_timeout", 2)
        try:
            await asyncio.sleep(timeout)
            self._state = False
            self.async_write_ha_state()
        except asyncio.CancelledError:
            # Timer cancelado, nada a fazer
            pass

def _unit(sensor_type):
    return {
        "temperature": "°C",
        "humidity": "%",
        "distance": "cm",
        "power": "W",
        "voltage": "V",
        "current": "A",
        "battery": "%"
    }.get(sensor_type)