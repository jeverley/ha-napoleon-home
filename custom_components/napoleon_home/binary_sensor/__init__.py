"""Binary sensor platform for napoleon_home."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from custom_components.napoleon_home.const import PARALLEL_UPDATES as PARALLEL_UPDATES

from .battery_saver_mode import (
    ENTITY_DESCRIPTIONS as DISPLAY_POWER_SAVE_DESCRIPTIONS,
    NapoleonHomeDisplayPowerSaveBinarySensor,
)
from .status import ENTITY_DESCRIPTIONS as STATUS_DESCRIPTIONS, NapoleonHomeStatusBinarySensor
from .tank_calibrated import (
    NapoleonHomeTankCalibratedBinarySensor,
    build_entity_descriptions as build_tank_calibrated_descriptions,
)

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
    """Set up the binary_sensor platform."""
    for coordinator in entry.runtime_data.values():
        async_add_entities(
            tuple(
                NapoleonHomeStatusBinarySensor(
                    coordinator=coordinator,
                    entity_description=entity_description,
                )
                for entity_description in STATUS_DESCRIPTIONS
            )
            + tuple(
                NapoleonHomeDisplayPowerSaveBinarySensor(
                    coordinator=coordinator,
                    entity_description=entity_description,
                )
                for entity_description in DISPLAY_POWER_SAVE_DESCRIPTIONS
            ),
        )
        coordinator.async_add_gas_tank_listener(
            _make_gas_tank_binary_sensor_adder(coordinator, async_add_entities),
        )


def _make_gas_tank_binary_sensor_adder(
    coordinator: NapoleonHomeDataUpdateCoordinator,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> Callable[[], None]:
    """Return a callback that adds the tank calibrated binary sensor."""

    def _add_entities() -> None:
        async_add_entities(
            NapoleonHomeTankCalibratedBinarySensor(coordinator=coordinator, entity_description=entity_description)
            for entity_description in build_tank_calibrated_descriptions()
        )

    return _add_entities
