"""Base entity for Varta Pulse integration."""

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import VartaPulseCoordinator


class VartaPulseEntity(CoordinatorEntity[VartaPulseCoordinator]):
    """Base entity for Varta Pulse integration."""

    _attr_has_entity_name = True
    _attr_manufacturer = MANUFACTURER
    _attr_model = MODEL
    _attr_device_info = None

    def __init__(
        self, coordinator: VartaPulseCoordinator, unique_id: str, name: str
    ) -> None:
        """Initialize a Varta Pulse entity.

        Args:
            coordinator: The update coordinator instance.
            unique_id: Unique identifier for the entity.
            name: Entity name.
        """
        super().__init__(coordinator)
        self._attr_unique_id = unique_id
        self._attr_name = name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, unique_id)},
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }
