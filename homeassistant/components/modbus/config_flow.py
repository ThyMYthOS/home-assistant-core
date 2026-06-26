"""Config flow for Modbus integration."""

from typing import Any, override

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_TYPE

from .const import DOMAIN, SERIAL


class ModbusConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a Modbus config flow."""

    VERSION = 1

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a user-initiated flow."""
        return self.async_abort(reason="not_supported")

    async def async_step_import(self, user_input: dict[str, Any]) -> ConfigFlowResult:
        """Handle import from configuration.yaml.

        The unique ID is derived from the physical connection endpoint so that
        renaming a hub in YAML does not create a duplicate entry.  Re-importing
        an existing hub replaces its connection data and reloads it, applying
        configuration.yaml edits on restart and reload.
        """
        if user_input[CONF_TYPE] == SERIAL:
            unique_id = user_input[CONF_PORT]
        else:
            # Modbus TCP/UDP has no hardware identifier; host:port is the best
            # stable physical address available.
            unique_id = f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"

        # pylint: disable-next=home-assistant-unique-id-ip-based
        await self.async_set_unique_id(unique_id)
        if entry := self.hass.config_entries.async_entry_for_domain_unique_id(
            self.handler, unique_id
        ):
            if self.hass.config_entries.async_update_entry(entry, data=user_input):
                self.hass.config_entries.async_schedule_reload(entry.entry_id)
            return self.async_abort(reason="already_configured")
        return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)
