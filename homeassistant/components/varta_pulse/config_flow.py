"""Config flow for Varta Pulse integration."""

from __future__ import annotations

import re

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, ENDPOINT_INFO

VERSION = 1
MINOR_VERSION = 1


class CannotConnect(Exception):
    """Raised when connection to Varta Pulse fails."""


async def validate_input(hass: HomeAssistant, host: str, port: int) -> str:
    """Test connection to Varta Pulse and return info.js or raise CannotConnect."""
    session = async_get_clientsession(hass)
    url = f"http://{host}:{port}{ENDPOINT_INFO}"
    async with session.get(url, timeout=5) as resp:
        if resp.status != 200:
            raise CannotConnect
        return await resp.text()


class VartaPulseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Varta Pulse."""

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle the user step of the config flow.

        Tests the connection to the Varta Pulse device and creates the entry.
        """
        errors = {}
        if user_input is not None:
            host = user_input.get(CONF_HOST)
            port = user_input.get(CONF_PORT, 80)
            try:
                info = await validate_input(self.hass, host, port)
                match = re.search(r'Battery_Serial\s*=\s*"([^"]+)";', info)
                serial = match.group(1) if match else host
                await self.async_set_unique_id(serial)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Varta Pulse {serial}",
                    data={CONF_HOST: host, CONF_PORT: port},
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema(),
            errors=errors,
        )

    def _get_schema(self):
        """Return the config flow schema for user input."""
        return vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=80): int,
            }
        )
