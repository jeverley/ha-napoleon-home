"""Fuel type sensor for napoleon_home."""

from __future__ import annotations

from typing import TYPE_CHECKING

# NOTE: FuelType is Prestige-specific (DTYPE encoding). This entity is
# nominally profile-generic (gated on has_gas_tank), but only Prestige is
# wired end-to-end so far — revisit this import if another profile grows a
# fuel-type concept with a different DTYPE-like encoding.
from custom_components.napoleon_home.device_profiles.prestige import FuelType
from custom_components.napoleon_home.entity import NapoleonHomeEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.const import EntityCategory

if TYPE_CHECKING:
    from custom_components.napoleon_home.coordinator import NapoleonHomeDataUpdateCoordinator
    from custom_components.napoleon_home.device_profiles import DeviceProfile

_OPTIONS: list[str] = ["propane", "natural_gas"]


def build_entity_descriptions(profile: DeviceProfile) -> tuple[SensorEntityDescription, ...]:
    """Build the fuel type sensor description, or none for models with no fuel-type concept."""
    if not profile.capabilities.has_gas_tank:
        return ()
    return (
        SensorEntityDescription(
            key="fuel_type",
            translation_key="fuel_type",
            device_class=SensorDeviceClass.ENUM,
            options=_OPTIONS,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:gas-cylinder",
        ),
    )


class NapoleonHomeFuelTypeSensor(SensorEntity, NapoleonHomeEntity):
    """Sensor reporting whether the grill is factory-set for propane or natural gas.

    Fuel type is set at the factory to match the physical hardware and is
    never user-adjustable — see select.device_model for the one legitimately
    adjustable half of DTYPE.
    """

    def __init__(
        self,
        coordinator: NapoleonHomeDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialise the fuel type sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def native_value(self) -> str | None:
        """Return "propane" or "natural_gas", or None if DTYPE hasn't been polled or is unrecognized."""
        dtype = self.coordinator.data.dtype
        if dtype is None:
            return None
        try:
            return "propane" if FuelType(dtype).is_propane else "natural_gas"
        except ValueError:
            return None
