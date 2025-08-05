"""Tests for Varta Pulse Coordinator."""

import pytest

from homeassistant.components.varta_pulse.coordinator import VartaPulseCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


@pytest.mark.asyncio
async def test_async_update_data_types(
    hass: HomeAssistant, varta_config_entry: ConfigEntry, varta_http_mocks
) -> None:
    """Test coordinator _async_update_data returns correct types."""
    coordinator = VartaPulseCoordinator(hass, varta_config_entry)
    data = await coordinator._async_update_data()
    assert isinstance(data["param"].data, dict)
    assert isinstance(data["ems_data"].wr_data, dict)
    assert isinstance(data["ems_data"].emeter_data, dict)
    assert isinstance(data["ems_data"].charger_data, dict)
    assert isinstance(data["ems_data"].modules_data, list)
    assert isinstance(data["error"].error_list, list)
    assert isinstance(data["error"].na_error_list, list)
    assert "OnlineStatus" in data["ems_data"].wr_data
    assert "PSoll" in data["ems_data"].wr_data
    assert "I EMeter L3" in data["ems_data"].emeter_data
    assert "BattData" in data["ems_data"].charger_data
