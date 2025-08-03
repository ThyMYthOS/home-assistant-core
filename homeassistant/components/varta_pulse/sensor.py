"""Sensor platform for Varta Pulse integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.varta_pulse.coordinator import VartaPulseCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import VartaPulseEntity

SENSORS = [
    SensorEntityDescription(
        key="battery_soc",
        name="Battery state of charge",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:battery",
        value_fn=lambda data: data["ems_data"].charger_data.get("SOC_GS")
        if "ems_data" in data and "charger_data" in data["ems_data"]
        else None,
    ),
    SensorEntityDescription(
        key="battery_power",
        name="Battery power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:flash",
        value_fn=lambda data: data["ems_data"].wr_data.get("PSoll")
        if "ems_data" in data and "wr_data" in data["ems_data"]
        else None,
    ),
    SensorEntityDescription(
        key="grid_power",
        name="Grid power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:transmission-tower",
        value_fn=lambda data: data["ems_data"].emeter_data.get("I EMeter L3")
        if "ems_data" in data and "emeter_data" in data["ems_data"]
        else None,
    ),
    SensorEntityDescription(
        key="module_voltage",
        name="Module voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:car-battery",
        value_fn=lambda data: data["ems_data"].charger_data.get("BattData", [None])[0][
            8
        ]
        if "ems_data" in data
        and "charger_data" in data["ems_data"]
        and "BattData" in data["ems_data"].charger_data
        and data["ems_data"].charger_data["BattData"]
        and len(data["ems_data"].charger_data["BattData"][0]) > 8
        else None,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Varta Pulse sensor entities from a config entry."""
    coordinator = entry.runtime_data
    entities = [VartaPulseSensor(coordinator, entry.entry_id, desc) for desc in SENSORS]
    async_add_entities(entities)


class VartaPulseSensor(VartaPulseEntity, SensorEntity):
    """Varta Pulse sensor entity."""

    def __init__(
        self,
        coordinator: VartaPulseCoordinator,
        unique_id: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize Varta Pulse sensor entity."""
        super().__init__(
            coordinator, f"{unique_id}-{description.key}", description.name
        )
        self.entity_description: SensorEntityDescription = description
        self._attr_entity_category: EntityCategory | None = description.entity_category
        self._attr_device_class: SensorDeviceClass | None = description.device_class
        self._attr_icon: str | None = description.icon
        self._attr_state_class: SensorStateClass | None = description.state_class
        self._attr_translation_key: str = description.key

    @property
    def native_value(self) -> SensorEntity.StateType:
        """Return the native value of the sensor."""
        data = self.coordinator.data if self.coordinator.data else {}
        return self.entity_description.value_fn(data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return cell voltages as extra attributes for module voltage sensor."""
        if self.entity_description.key != "module_voltage":
            return None
        data = self.coordinator.data if self.coordinator.data else {}

        batt_data = data["ems_data"].charger_data.get("BattData", [None])[0]
        if batt_data:
            # Cell voltages are at indexes 29-42 in Modul_Conf
            cell_voltages = batt_data[29:43]
            return {f"cell_voltage_{i + 1}": v for i, v in enumerate(cell_voltages)}

        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
