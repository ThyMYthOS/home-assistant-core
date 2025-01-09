"""The component for STIEBEL ELTRON heat pumps with ISGWeb Modbus module."""

from datetime import timedelta
import logging

from pymodbus.client import ModbusTcpClient
from pystiebeleltron import pystiebeleltron
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, DEVICE_DEFAULT_NAME, Platform
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle

from .const import CONF_HUB, DEFAULT_HUB, DOMAIN, MODBUS_DOMAIN

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_NAME, default=DEVICE_DEFAULT_NAME): cv.string,
                vol.Optional(CONF_HUB, default=DEFAULT_HUB): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up STIEBEL ELTRON from a config entry."""
    name = entry.data[CONF_NAME]
    modbus_client = hass.data[MODBUS_DOMAIN][entry.data[CONF_HUB]]

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = StiebelEltronData(
        name, modbus_client
    )

    await hass.config_entries.async_forward_entry_setup(entry, Platform.CLIMATE)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_forward_entry_unload(
        entry, Platform.CLIMATE
    ):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class StiebelEltronData:
    """Get the latest data and update the states."""

    def __init__(self, name, modbus_client: ModbusTcpClient) -> None:
        """Init the STIEBEL ELTRON data object."""

        self._name = name
        self.api = pystiebeleltron.StiebelEltronAPI(modbus_client, 1)

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self._name

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self) -> None:
        """Update unit data."""
        if not self.api.update():
            _LOGGER.warning("Modbus read failed")
        else:
            _LOGGER.debug("Data updated successfully")
