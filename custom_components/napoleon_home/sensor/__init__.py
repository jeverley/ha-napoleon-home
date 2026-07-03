"""Sensor platform for napoleon_home."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.napoleon_home.const import PARALLEL_UPDATES as PARALLEL_UPDATES

from .battery import NapoleonHomeBatterySensor, build_entity_descriptions as build_battery_descriptions
from .firmware import ENTITY_DESCRIPTIONS as FIRMWARE_DESCRIPTIONS, NapoleonHomeFirmwareVersionSensor
from .probe_temp import NapoleonHomeProbeTempSensor, build_entity_descriptions as build_probe_temp_descriptions
from .tank_weight import (
    NapoleonHomeTankDebugSensor,
    NapoleonHomeTankWeightSensor,
    build_debug_entity_descriptions,
    build_entity_descriptions as build_tank_weight_descriptions,
)

if TYPE_CHECKING:
    from custom_components.napoleon_home.data import NapoleonHomeConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NapoleonHomeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    for coordinator in entry.runtime_data.values():
        profile = coordinator.profile
        async_add_entities(
            (
                NapoleonHomeProbeTempSensor(
                    coordinator=coordinator,
                    entity_description=entity_description,
                )
                for entity_description in build_probe_temp_descriptions(profile)
            ),
        )
        async_add_entities(
            (
                NapoleonHomeBatterySensor(
                    coordinator=coordinator,
                    entity_description=entity_description,
                )
                for entity_description in build_battery_descriptions(profile)
            ),
        )
        async_add_entities(
            (
                NapoleonHomeFirmwareVersionSensor(
                    coordinator=coordinator,
                    entity_description=entity_description,
                )
                for entity_description in FIRMWARE_DESCRIPTIONS
            ),
        )
        async_add_entities(
            (
                NapoleonHomeTankWeightSensor(
                    coordinator=coordinator,
                    entity_description=entity_description,
                )
                for entity_description in build_tank_weight_descriptions(profile)
            ),
        )
        async_add_entities(
            (
                NapoleonHomeTankDebugSensor(
                    coordinator=coordinator,
                    entity_description=entity_description,
                )
                for entity_description in build_debug_entity_descriptions(profile)
            ),
        )
