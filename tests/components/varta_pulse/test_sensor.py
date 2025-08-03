"""Tests for Varta Pulse sensors."""

import pytest

from homeassistant.components.varta_pulse.sensor import SENSORS, VartaPulseSensor
from homeassistant.core import HomeAssistant

EXAMPLE_EMS_CONF = {
    "WR_Conf": [
        "EMS UG",
        "EMS OG",
        "EMS Timer",
        "PSoll",
        "U Verbund",
        "U WR",
        "I Wirk",
        "I Blind",
        "TempAmb",
        "TempHB",
        "TempEMS",
        "FNetz",
        "U N->PE",
        "OnlineStatus",
        "System State",
        "SK",
        "RB_IP",
        "RCMU",
        "IDrift",
        "UZwk",
        "Luefter Soll",
        "Luefter Ist",
        "WR Ctrl",
        "ENS Ctrl",
        "EMS Ctrl",
        "EMS Mode",
        "BetrFlags1",
        "BetrFlags2",
        "PMB",
        "EMB",
        "PAvailDCAC",
        "PAvailACDC",
        "MaxSchieflastACDC",
        "MaxSchieflastDCAC",
        "CountryID",
        "IO_Box",
        "SC OV_Val S1",
        "SC OV_Time S1",
        "SC UV_Val S1",
        "SC UV_Time S1",
        "SC OF_Val S1",
        "SC OF_Time S1",
        "SC UF_Val S1",
        "SC UF_Time S1",
        "SC OV_Val S2",
        "SC OV_Time S2",
        "SC UV_Val S2",
        "SC UV_Time S2",
        "SC OF_Val S2",
        "SC OF_Time S2",
        "SC UF_Val S2",
        "SC UF_Time S2",
        "General State",
    ],
    "EMETER_Conf": [
        "U EMeter",
        "I EMeter L1",
        "I EMeter L2",
        "I EMeter L3",
        "F EMeter",
        "SensorState",
        "Iw PV L1",
        "Iw PV L2",
        "Iw PV L3",
        "Ib PV L1",
        "Ib PV L2",
        "Ib PV L3",
        "Is Verb L1",
        "Is Verb L2",
        "Is Verb L3",
        "Ib Verb L1",
        "Ib Verb L2",
        "Ib Verb L3",
    ],
    "Charger_Conf": [
        "Index",
        "Enabled",
        "SOC_GS",
        "State",
        "U",
        "I",
        "UOut",
        "UVcc",
        "THT",
        "TTr",
        "TBoard",
        "PSoll",
        "SOHCmax",
        "SOHCuxtime",
        "SOHDmax",
        "SOHDuxtime",
        "ErrorFlags",
        "UNetz",
        "FNetz",
        "PAvailChrg",
        "PAvailDisc",
        "SOCMin",
        "SOCMax",
        "DABWinkel",
        "HelperFlags",
        "BetrFlags",
        "SteuerFlags",
        "BattState",
        "SVDFflags",
        "RSOCmin",
        "RSOCmax",
        "SOCcut",
        "DSOC_Thr1",
        "DSOC_Thr2",
        "SVDFtime",
        "SVDFcnt1s",
        "BattData",
    ],
}

EXAMPLE_EMS_DATA = {
    "zeit": "03.08.2025 21:35:15",
    "wr_data": {"OnlineStatus": 1, "PSoll": 2500},
    "emeter_data": {"I EMeter L3": -441},
    "charger_data": {
        "BattData": [
            [
                0,
                1,
                89,
                104,
                5599,
                -2045,
                4001,
                120,
                39,
                39,
                35,
                -1223,
                0,
                0,
                0,
                0,
                0,
                2367,
                5001,
                2500,
                2500,
                0,
                100,
                -10689,
                18627616,
                32843,
                327,
                6931,
                21,
                86,
                95,
                75,
                20,
                5,
                1860,
                1860,
                [
                    4004,
                    4003,
                    4006,
                    4006,
                    4009,
                    4009,
                    4009,
                    4007,
                    4006,
                    3995,
                    3996,
                    3997,
                    4002,
                    3996,
                ],
            ]
        ]
    },
}


@pytest.mark.asyncio
async def test_sensor_values(hass: HomeAssistant) -> None:
    """Test Varta Pulse sensor values and attributes."""
    # Simuliere Coordinator-Daten
    coordinator_data = {
        "ems_data": EXAMPLE_EMS_DATA,
        "ems_conf": EXAMPLE_EMS_CONF,
    }

    entities = [VartaPulseSensor(None, "test", desc) for desc in SENSORS]
    for entity in entities:
        entity.coordinator = type(
            "DummyCoordinator",
            (),
            {"data": coordinator_data, "last_update_success": True},
        )()
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
    assert attrs["cell_voltage_14"] == 3996
