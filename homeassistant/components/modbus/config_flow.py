"""Config flow for Modbus integration."""

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN


class ModbusConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Modbus."""

    VERSION = 1

    async def async_step_import(self, import_data: dict) -> ConfigFlowResult:
        """Handle import from YAML."""
        hub_name = import_data["name"]
        await self.async_set_unique_id(hub_name)
        self._abort_if_unique_id_configured(updates=import_data)
        return self.async_create_entry(title=hub_name, data=import_data)
