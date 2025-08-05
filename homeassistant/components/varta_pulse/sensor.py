"""Sensor platform for Varta Pulse integration."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import VartaPulseCoordinator
from .entity import VartaPulseEntity


class VartaPulseSensorEntityDescription(SensorEntityDescription):
    """Custom sensor entity description for Varta Pulse with value_fn und attributes_fn."""

    def __init__(
        self,
        key: str,
        name: str,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        entity_category: EntityCategory | None = None,
        icon: str | None = None,
        value_fn: Callable[[dict], Any] | None = None,
        attributes_fn: Callable[[dict], dict[str, Any] | None] | None = None,
    ) -> None:
        """Initialize VartaPulseSensorEntityDescription."""
        super().__init__(
            key=key,
            name=name,
            device_class=device_class,
            state_class=state_class,
            entity_category=entity_category,
            icon=icon,
        )
        self.value_fn = value_fn
        self.attributes_fn = attributes_fn


VARTA_PULSE_SENSORS = [
    VartaPulseSensorEntityDescription(
        key="battery_soc",
        name="Battery state of charge",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:battery",
        value_fn=lambda data: data["ems_data"].charger_data.get("SOC_GS"),
    ),
    VartaPulseSensorEntityDescription(
        key="battery_power",
        name="Battery power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:flash",
        value_fn=lambda data: data["ems_data"].wr_data.get("PSoll"),
    ),
    VartaPulseSensorEntityDescription(
        key="grid_power",
        name="Grid power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:transmission-tower",
        value_fn=lambda data: data["ems_data"].emeter_data.get("I EMeter L3"),
    ),
    VartaPulseSensorEntityDescription(
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
        attributes_fn=lambda data: (
            None
            if "ems_data" not in data
            or "charger_data" not in data["ems_data"]
            or "BattData" not in data["ems_data"].charger_data
            or not data["ems_data"].charger_data["BattData"]
            else {
                f"cell_voltage_{i + 1}": v
                for i, v in enumerate(
                    data["ems_data"].charger_data["BattData"][0][29:43]
                )
            }
        ),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Varta Pulse sensor entities from a config entry."""
    coordinator = entry.runtime_data
    entities = [
        VartaPulseSensor(coordinator, entry.entry_id, desc)
        for desc in VARTA_PULSE_SENSORS
    ]
    async_add_entities(entities)


class VartaPulseSensor(VartaPulseEntity, SensorEntity):
    """Varta Pulse sensor entity."""

    def __init__(
        self,
        coordinator: VartaPulseCoordinator,
        unique_id: str,
        description: VartaPulseSensorEntityDescription,
    ) -> None:
        """Initialize Varta Pulse sensor entity."""
        super().__init__(
            coordinator, f"{unique_id}-{description.key}", description.name
        )
        self.entity_description: VartaPulseSensorEntityDescription = description
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
        """Return extra state attributes for the sensor (z. B. Zellspannungen)."""
        if self.entity_description.attributes_fn:
            data = self.coordinator.data if self.coordinator.data else {}
            return self.entity_description.attributes_fn(data)
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
