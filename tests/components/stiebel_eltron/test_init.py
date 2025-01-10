"""Test the STIEBEL ELTRON init file."""

from unittest.mock import patch

from homeassistant.components.stiebel_eltron.const import (
    CONF_HUB,
    CONF_NAME,
    DOMAIN,
    MODBUS_DOMAIN,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry


async def test_async_setup_entry(hass: HomeAssistant) -> None:
    """Test setting up entry."""

    modbus_entry = MockConfigEntry(
        title="Stiebel Eltron Modbus",
        domain=MODBUS_DOMAIN,
        data={"name": "modbus_hub", "type": "tcp", "host": "modbus.local", "port": 502},
        state=ConfigEntryState.LOADED,
    )
    modbus_entry.add_to_hass(hass)

    entry = MockConfigEntry(
        title="Stiebel Eltron",
        domain=DOMAIN,
        data={CONF_NAME: "Test", CONF_HUB: "modbus_hub"},
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert entry.entry_id in hass.data[DOMAIN]


async def test_async_unload_entry(hass: HomeAssistant) -> None:
    """Test unloading STIEBEL ELTRON."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_NAME: "Test", CONF_HUB: "modbus_hub"},
        unique_id="modbus_hub",
        state=ConfigEntryState.LOADED,
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.NOT_LOADED
    assert entry.entry_id not in hass.data[DOMAIN]
