"""Config flow for Modbus integration."""

from typing import Any

from pymodbus.exceptions import ModbusException
from pymodbus.framer import FramerType
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import (
    CONF_DELAY,
    CONF_HOST,
    CONF_METHOD,
    CONF_NAME,
    CONF_PORT,
    CONF_TIMEOUT,
    CONF_TYPE,
)
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_BAUDRATE,
    CONF_BYTESIZE,
    CONF_MSG_WAIT,
    CONF_PARITY,
    CONF_STOPBITS,
    DOMAIN,
    RTUOVERTCP,
    SERIAL,
    TCP,
)
from .modbus import AsyncModbusSerialClient, AsyncModbusTcpClient, AsyncModbusUdpClient


def _schema_for_connection(connection_type: str) -> vol.Schema:
    """Return the schema for a connection type."""
    fields: dict[Any, Any] = {
        vol.Required(CONF_TIMEOUT, default=3): cv.socket_timeout,
        vol.Optional(CONF_DELAY, default=0): cv.positive_int,
        vol.Optional(CONF_MSG_WAIT): cv.positive_int,
    }
    if connection_type == SERIAL:
        fields |= {
            vol.Required(CONF_PORT): cv.string,
            vol.Required(CONF_BAUDRATE): cv.positive_int,
            vol.Required(CONF_BYTESIZE): vol.Any(5, 6, 7, 8),
            vol.Required(CONF_METHOD): vol.Any("rtu", "ascii"),
            vol.Required(CONF_PARITY): vol.Any("E", "O", "N"),
            vol.Required(CONF_STOPBITS): vol.Any(1, 2),
        }
    else:
        fields |= {
            vol.Required(CONF_HOST): cv.string,
            vol.Required(CONF_PORT): cv.port,
        }
    return vol.Schema(fields)


async def _async_validate_connection(data: dict[str, Any]) -> bool:
    """Validate a Modbus connection."""
    client: (
        AsyncModbusSerialClient | AsyncModbusTcpClient | AsyncModbusUdpClient | None
    ) = None
    params: dict[str, Any] = {
        "port": data[CONF_PORT],
        "timeout": data[CONF_TIMEOUT],
        "retries": 3,
    }
    if data[CONF_TYPE] == SERIAL:
        params["framer"] = (
            FramerType.ASCII if data[CONF_METHOD] == "ascii" else FramerType.RTU
        )
        params.update(
            {
                "baudrate": data[CONF_BAUDRATE],
                "stopbits": data[CONF_STOPBITS],
                "bytesize": data[CONF_BYTESIZE],
                "parity": data[CONF_PARITY],
            }
        )
        client = AsyncModbusSerialClient(**params)
    else:
        params["host"] = data[CONF_HOST]
        params["framer"] = (
            FramerType.RTU if data[CONF_TYPE] == RTUOVERTCP else FramerType.SOCKET
        )
        if data[CONF_TYPE] in (TCP, RTUOVERTCP):
            client = AsyncModbusTcpClient(**params)
        else:
            client = AsyncModbusUdpClient(**params)

    try:
        return await client.connect()
    except ModbusException:
        return False
    finally:
        if client is not None:
            client.close()


class ModbusConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Modbus."""

    VERSION = 1

    async def async_step_import(self, import_data: dict) -> ConfigFlowResult:
        """Handle import from YAML."""
        hub_name = import_data[CONF_NAME]
        await self.async_set_unique_id(hub_name)
        self._abort_if_unique_id_configured(updates=import_data)
        return self.async_create_entry(title=hub_name, data=import_data)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration flow for a Modbus hub."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()
        connection_type = reconfigure_entry.data[CONF_TYPE]
        if user_input is not None:
            updated_data = dict(reconfigure_entry.data) | user_input
            if await _async_validate_connection(updated_data):
                return self.async_update_reload_and_abort(
                    reconfigure_entry,
                    data=updated_data,
                )
            errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                _schema_for_connection(connection_type),
                dict(reconfigure_entry.data) | (user_input or {}),
            ),
            description_placeholders={"name": reconfigure_entry.title},
            errors=errors,
        )
