"""Tests for the Varta Pulse integration."""

import pytest

from homeassistant.config_entries import ConfigEntry


@pytest.fixture
def varta_config_entry() -> ConfigEntry:
    """Return a default mocked Varta Pulse ConfigEntry."""
    return ConfigEntry(
        version=1,
        minor_version=1,
        domain="varta_pulse",
        title="Varta Pulse",
        data={"host": "1.2.3.4", "port": 80},
        options={},
        entry_id="testid",
        source="user",
    )
