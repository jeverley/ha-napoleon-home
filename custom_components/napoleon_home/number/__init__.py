"""Number platform for napoleon_home."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from custom_components.napoleon_home.const import PARALLEL_UPDATES as PARALLEL_UPDATES

from .automatic_shutoff import (
    NapoleonHomeAutoShutoffNumber,
    build_entity_descriptions as build_auto_shutoff_descriptions,
)
from .tank_calibration import (
    NapoleonHomeTankCalibrationNumber,
    build_entity_descriptions as build_tank_calibration_descriptions,
)
from .target_temp import NapoleonHomeTargetTempNumber, build_entity_descriptions as build_target_temp_descriptions

if TYPE_CHECKING:
    from custom_components.napoleon_home.coordinator import NapoleonHomeDataUpdateCoordinator
    from custom_components.napoleon_home.data import NapoleonHomeConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NapoleonHomeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the number platform."""
    for coordinator in entry.runtime_data.values():
        profile = coordinator.profile
        async_add_entities(
            (
                NapoleonHomeAutoShutoffNumber(
                    coordinator=coordinator,
                    entity_description=entity_description,
                )
                for entity_description in build_auto_shutoff_descriptions(profile)
            ),
        )
        async_add_entities(
            (
                NapoleonHomeTargetTempNumber(
                    coordinator=coordinator,
                    entity_description=entity_description,
                )
                for entity_description in build_target_temp_descriptions(profile)
            ),
        )
        coordinator.async_add_gas_tank_listener(
            _make_gas_tank_number_adder(coordinator, async_add_entities),
        )


def _make_gas_tank_number_adder(
    coordinator: NapoleonHomeDataUpdateCoordinator,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> Callable[[], None]:
    """Return a callback that adds the empty/full tank calibration numbers."""

    def _add_entities() -> None:
        async_add_entities(
            NapoleonHomeTankCalibrationNumber(coordinator=coordinator, entity_description=entity_description)
            for entity_description in build_tank_calibration_descriptions()
        )

    return _add_entities
