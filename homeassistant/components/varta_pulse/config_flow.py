"""Config flow for Varta Pulse integration."""

from __future__ import annotations

import re

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import DOMAIN

VERSION = 1
MINOR_VERSION = 1


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

            class CannotConnect(Exception):
                """Raised when connection to Varta Pulse fails."""

            try:
                async with aiohttp.ClientSession() as session:
                    url = f"http://{host}:{port}/cgi/param"
                    async with session.get(url, timeout=5) as resp:
                        if resp.status != 200:
                            raise CannotConnect
                        param_text = await resp.text()
                # Parse BATT_SER from param_text
                match = re.search(r'BATT_SER\s*=\s*"([^"]+)";', param_text)
                serial = match.group(1) if match else host
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(serial)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Varta Pulse {serial}",
                    data={CONF_HOST: host, CONF_PORT: port},
                )
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
