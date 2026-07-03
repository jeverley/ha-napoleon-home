"""Tank calibration number entities for napoleon_home."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from custom_components.napoleon_home.entity import NapoleonHomeEntity
from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import EntityCategory, UnitOfMass

if TYPE_CHECKING:
    from custom_components.napoleon_home.coordinator import NapoleonHomeDataUpdateCoordinator
    from custom_components.napoleon_home.device_profiles import DeviceProfile


@dataclass(frozen=True, kw_only=True)
class NapoleonHomeTankCalibrationNumberEntityDescription(NumberEntityDescription):
    """Entity description for tank calibration numbers.

    Attributes:
        concept: The profile concept key backing this entity (``"empty_tank_weight"``
            or ``"full_tank_weight"``) — see the active DeviceProfile's
            ``properties`` map.

    """

    concept: str = ""


def build_entity_descriptions(
    profile: DeviceProfile,
) -> tuple[NapoleonHomeTankCalibrationNumberEntityDescription, ...]:
    """Build tank calibration number descriptions, or none for models with no gas tank."""
    if not profile.capabilities.has_gas_tank:
        return ()
    return (
        NapoleonHomeTankCalibrationNumberEntityDescription(
            key="empty_tank_weight",
            translation_key="empty_tank_weight",
            icon="mdi:propane-tank-outline",
            entity_category=EntityCategory.CONFIG,
            mode=NumberMode.BOX,
            native_min_value=0,
            native_max_value=200,
            native_step=1,
            concept="empty_tank_weight",
        ),
        NapoleonHomeTankCalibrationNumberEntityDescription(
            key="full_tank_weight",
            translation_key="full_tank_weight",
            icon="mdi:propane-tank",
            entity_category=EntityCategory.CONFIG,
            mode=NumberMode.BOX,
            native_min_value=0,
            native_max_value=200,
            native_step=1,
            concept="full_tank_weight",
        ),
    )


class NapoleonHomeTankCalibrationNumber(NumberEntity, NapoleonHomeEntity):
    """Number entities for empty/full tank calibration values."""

    entity_description: NapoleonHomeTankCalibrationNumberEntityDescription

    def __init__(
        self,
        coordinator: NapoleonHomeDataUpdateCoordinator,
        entity_description: NapoleonHomeTankCalibrationNumberEntityDescription,
    ) -> None:
        """Initialise the tank calibration number."""
        super().__init__(coordinator, entity_description)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return mass unit following the grill tank unit setting."""
        return UnitOfMass.POUNDS if self.coordinator.data.gs_unt == 1 else UnitOfMass.KILOGRAMS

    @property
    def native_value(self) -> float | None:
        """Return current calibration value."""
        if self.entity_description.concept == "empty_tank_weight":
            return self.coordinator.data.empty_tank_weight
        return self.coordinator.data.full_tank_weight

    async def async_set_native_value(self, value: float) -> None:
        """Set calibration value on the grill."""
        int_value = int(value)
        await self.coordinator.async_set_property_by_concept(self.entity_description.concept, int_value)
        if self.entity_description.concept == "empty_tank_weight":
            self.coordinator.data.empty_tank_weight = float(int_value)
        else:
            self.coordinator.data.full_tank_weight = float(int_value)
        self.coordinator.async_set_updated_data(self.coordinator.data)
