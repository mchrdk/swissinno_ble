import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Schema för användarinmatning vid installation
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required("device_name", default="SWISSINNO BLE"): cv.string,
        vol.Required("track_all_devices", default=True): cv.boolean,
    }
)

class SwissinnoBLEConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Swissinno BLE."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        # Förhindrar att integrationen installeras flera gånger
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            return self.async_create_entry(title=user_input["device_name"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return SwissinnoBLEOptionsFlowHandler(config_entry)


class SwissinnoBLEOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Swissinno BLE."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Hämta befintliga inställningar
        options = self.config_entry.options

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("track_all_devices", default=options.get("track_all_devices", True)): cv.boolean,
                }
            ),
        )
