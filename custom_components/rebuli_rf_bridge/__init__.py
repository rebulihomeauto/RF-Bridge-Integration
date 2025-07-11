import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .mqtt_handler import setup_mqtt

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["allowed_ids"] = entry.options.get("allowed_ids", [])
    hass.data[DOMAIN]["mqtt_topic"] = entry.options.get("mqtt_topic", "home/rebuli_rf/received")
    hass.data[DOMAIN]["auto_off_timeout"] = entry.options.get("auto_off_timeout", 2)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])
    hass.async_create_task(setup_mqtt(hass, entry))
    return True