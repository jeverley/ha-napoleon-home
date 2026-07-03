"""Tank calibrated binary sensor for napoleon_home."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.napoleon_home.entity import NapoleonHomeEntity
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.const import EntityCategory

if TYPE_CHECKING:
    from custom_components.napoleon_home.coordinator import NapoleonHomeDataUpdateCoordinator


def build_entity_descriptions() -> tuple[BinarySensorEntityDescription, ...]:
    """Build the tank calibrated binary sensor description.

    Only ever called once a grill resolves to a portable propane tank — see
    ``NapoleonHomeDataUpdateCoordinator.async_add_gas_tank_listener``.
    """
    return (
        BinarySensorEntityDescription(
            key="tank_calibrated",
            translation_key="tank_calibrated",
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:propane-tank-outline",
        ),
    )


class NapoleonHomeTankCalibratedBinarySensor(BinarySensorEntity, NapoleonHomeEntity):
    """Binary sensor indicating whether the tank weight reading is calibrated.

    Reflects the same confirmed criterion the grill itself uses (TNK_WT >= 0)
    — see NapoleonHomeGrillState.tank_weight.
    """

    def __init__(
        self,
        coordinator: NapoleonHomeDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialise the tank calibrated binary sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def is_on(self) -> bool:
        """Return True when the grill reports a valid (calibrated) tank weight."""
        return self.coordinator.data.tank_weight is not None
