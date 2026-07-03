"""Select platform for napoleon_home."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.napoleon_home.const import PARALLEL_UPDATES as PARALLEL_UPDATES

from .brightness import NapoleonHomeDisplayBrightnessSelect, build_entity_descriptions as build_brightness_descriptions
from .tank_unit import NapoleonHomeGasUnitSelect, build_entity_descriptions as build_gas_unit_descriptions
from .temperature_unit import ENTITY_DESCRIPTIONS as TEMP_UNIT_DESCRIPTIONS, NapoleonHomeTempUnitSelect

if TYPE_CHECKING:
    from custom_components.napoleon_home.data import NapoleonHomeConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NapoleonHomeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the select platform."""
    for coordinator in entry.runtime_data.values():
        profile = coordinator.profile
        async_add_entities(
            (
                NapoleonHomeTempUnitSelect(
                    coordinator=coordinator,
                    entity_description=entity_description,
                )
                for entity_description in TEMP_UNIT_DESCRIPTIONS
            ),
        )
        async_add_entities(
            (
                NapoleonHomeDisplayBrightnessSelect(
                    coordinator=coordinator,
                    entity_description=entity_description,
                )
                for entity_description in build_brightness_descriptions(profile)
            ),
        )
        async_add_entities(
            (
                NapoleonHomeGasUnitSelect(
                    coordinator=coordinator,
                    entity_description=entity_description,
                )
                for entity_description in build_gas_unit_descriptions(profile)
            ),
        )
