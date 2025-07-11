from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

DEFAULT_TOPIC = "home/rebuli_rf/received"
DEFAULT_TIMEOUT = 2

class RebuliRFBridgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            allowed_ids = [s.strip().upper() for s in user_input["allowed_ids"].split(",") if s.strip()]
            return self.async_create_entry(title="Rebuli RF Bridge", data={}, options={
                "mqtt_topic": user_input["mqtt_topic"],
                "auto_off_timeout": user_input["auto_off_timeout"],
                "allowed_ids": allowed_ids,
            })

        schema = vol.Schema({
            vol.Optional("mqtt_topic", default=DEFAULT_TOPIC): str,
            vol.Optional("auto_off_timeout", default=DEFAULT_TIMEOUT): int,
            vol.Optional("allowed_ids", default=""): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    def async_get_options_flow(config_entry):
        return RebuliRFBridgeOptionsFlowHandler(config_entry)

class RebuliRFBridgeOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        current = self.config_entry.options

        schema = vol.Schema({
            vol.Optional("mqtt_topic", default=current.get("mqtt_topic", DEFAULT_TOPIC)): str,
            vol.Optional("auto_off_timeout", default=current.get("auto_off_timeout", DEFAULT_TIMEOUT)): int,
            vol.Optional("allowed_ids", default=", ".join(current.get("allowed_ids", []))): str,
        })

        if user_input is not None:
            allowed_ids = [s.strip().upper() for s in user_input["allowed_ids"].split(",") if s.strip()]
            return self.async_create_entry(title="", data={
                "mqtt_topic": user_input["mqtt_topic"],
                "auto_off_timeout": user_input["auto_off_timeout"],
                "allowed_ids": allowed_ids,
            })

        return self.async_show_form(step_id="init", data_schema=schema)
