"""Tests for Varta Pulse sensors."""

import pytest

from homeassistant.components.varta_pulse.sensor import SENSORS, VartaPulseSensor
from homeassistant.core import HomeAssistant


@pytest.fixture
def coordinator():
    """Fixture that liefert einen DummyCoordinator mit Beispieldaten für die Sensor-Tests."""

    class DummyCoordinator:
        data = {
            "ems_data": type(
                "EmsData",
                (),
                {
                    "charger_data": {
                        "SOC_GS": 1,
                        "BattData": [
                            [
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                39,
                                *([None] * 20),
                                *[4004 + i for i in range(14)],
                            ]
                        ],
                    },
                    "wr_data": {"PSoll": 2500},
                    "emeter_data": {"I EMeter L3": -441},
                },
            )(),
        }
        last_update_success = True

    return DummyCoordinator()


@pytest.mark.asyncio
async def test_sensor_values(hass: HomeAssistant, coordinator) -> None:
    """Test Varta Pulse sensor values and attributes."""
    entities = [VartaPulseSensor(coordinator, "test", desc) for desc in SENSORS]
    # Battery SoC
    soc = entities[0].native_value
    assert soc == 1
    # Battery Power
    power = entities[1].native_value
    assert power == 2500
    # Grid Power
    grid = entities[2].native_value
    assert grid == -441
    # Module Voltage
    module_voltage = entities[3].native_value
    assert module_voltage == 39
    # Zellspannungen als Attribute
    attrs = entities[3].extra_state_attributes
    assert attrs["cell_voltage_1"] == 4004
    assert attrs["cell_voltage_14"] == 4017
