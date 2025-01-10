"""Config flow for STIEBEL ELTRON integration."""

from pymodbus.client import ModbusTcpClient
from pystiebeleltron.pystiebeleltron import StiebelEltronAPI
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT

from .const import DEFAULT_DEVICE_NAME, DEFAULT_PORT, DOMAIN


def validate_input(data: dict) -> bool:
    """Validate the user input."""
    modbus_client = ModbusTcpClient(data[CONF_HOST])
    api = StiebelEltronAPI(modbus_client, 1)
    success = api.update()
    modbus_client.close()
    return success


class StiebelEltronConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for STIEBEL ELTRON."""

    VERSION = 1

    async def async_step_import(self, user_input=None) -> ConfigFlowResult:
        """Handle import from YAML configuration."""
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            if await self.hass.async_add_executor_job(validate_input, user_input):
                # Make sure we're not configuring the same device
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()

                # Create entry for modbus component
                modbus_entry = {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: DEFAULT_PORT,
                }
                self.hass.async_create_task(
                    self.hass.config_entries.flow.async_init(
                        "modbus", context={"source": "import"}, data=modbus_entry
                    )
                )

                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )
            errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_DEVICE_NAME): str,
                vol.Required(CONF_HOST): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
