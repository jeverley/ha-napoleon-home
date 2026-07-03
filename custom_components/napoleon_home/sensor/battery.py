"""Battery sensor for napoleon_home."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.napoleon_home.entity import NapoleonHomeEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import PERCENTAGE, EntityCategory

if TYPE_CHECKING:
    from custom_components.napoleon_home.coordinator import NapoleonHomeDataUpdateCoordinator
    from custom_components.napoleon_home.device_profiles import DeviceProfile


def build_entity_descriptions(profile: DeviceProfile) -> tuple[SensorEntityDescription, ...]:
    """Build the battery sensor description, or none for models with no battery."""
    if not profile.capabilities.has_battery:
        return ()
    return (
        SensorEntityDescription(
            key="battery",
            translation_key="battery",
            device_class=SensorDeviceClass.BATTERY,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=PERCENTAGE,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    )


class NapoleonHomeBatterySensor(SensorEntity, NapoleonHomeEntity):
    """Sensor reporting current battery level."""

    def __init__(
        self,
        coordinator: NapoleonHomeDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialise the battery sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def native_value(self) -> int | None:
        """Return current battery level percentage."""
        return self.coordinator.data.battery_level
