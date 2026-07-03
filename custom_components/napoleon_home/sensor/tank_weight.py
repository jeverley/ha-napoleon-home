"""Tank weight sensor for napoleon_home."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from custom_components.napoleon_home.entity import NapoleonHomeEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import EntityCategory, UnitOfMass
from homeassistant.util.unit_conversion import MassConverter

if TYPE_CHECKING:
    from custom_components.napoleon_home.coordinator import NapoleonHomeDataUpdateCoordinator
    from custom_components.napoleon_home.data import NapoleonHomeGrillState
    from homeassistant.helpers.typing import StateType


def build_entity_descriptions() -> tuple[SensorEntityDescription, ...]:
    """Build the tank weight sensor description.

    Only ever called once a grill resolves to a portable propane tank — see
    ``NapoleonHomeDataUpdateCoordinator.async_add_gas_tank_listener``.
    """
    return (
        SensorEntityDescription(
            key="tank_weight",
            translation_key="tank_weight",
            device_class=SensorDeviceClass.WEIGHT,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:propane-tank",
        ),
    )


@dataclass(frozen=True, kw_only=True)
class NapoleonHomeTankDebugSensorEntityDescription(SensorEntityDescription):
    """Entity description for debug tank metadata sensors."""

    value_fn: Callable[[NapoleonHomeGrillState], StateType] = lambda _: None


def build_debug_entity_descriptions() -> tuple[NapoleonHomeTankDebugSensorEntityDescription, ...]:
    """Build region/country debug metadata sensor descriptions (always present)."""
    return (
        NapoleonHomeTankDebugSensorEntityDescription(
            key="region",
            translation_key="region",
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            icon="mdi:earth",
            value_fn=lambda s: s.region,
        ),
        NapoleonHomeTankDebugSensorEntityDescription(
            key="country",
            translation_key="country",
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            icon="mdi:flag",
            value_fn=lambda s: s.country,
        ),
    )


def build_gas_tank_name_entity_descriptions() -> tuple[NapoleonHomeTankDebugSensorEntityDescription, ...]:
    """Build the gas tank name debug sensor description.

    Only ever called once a grill resolves to a portable propane tank — see
    ``NapoleonHomeDataUpdateCoordinator.async_add_gas_tank_listener``.
    """
    return (
        NapoleonHomeTankDebugSensorEntityDescription(
            key="gas_tank_name",
            translation_key="gas_tank_name",
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            icon="mdi:propane-tank",
            value_fn=lambda s: s.gas_tank_name,
        ),
    )


class NapoleonHomeTankWeightSensor(SensorEntity, NapoleonHomeEntity):
    """Sensor reporting current tank weight."""

    def __init__(
        self,
        coordinator: NapoleonHomeDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialise the tank weight sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return tank weight unit based on grill setting."""
        return UnitOfMass.POUNDS if self.coordinator.data.gs_unt == 1 else UnitOfMass.KILOGRAMS

    @property
    def native_value(self) -> float | None:
        """Return current tank weight, converted to lbs if that's the grill's configured unit."""
        weight = self.coordinator.data.tank_weight
        if weight is None:
            return None
        if self.coordinator.data.gs_unt == 1:
            return round(MassConverter.convert(weight, UnitOfMass.KILOGRAMS, UnitOfMass.POUNDS), 1)
        return weight


class NapoleonHomeTankDebugSensor(SensorEntity, NapoleonHomeEntity):
    """Debug sensor for tank metadata fields."""

    entity_description: NapoleonHomeTankDebugSensorEntityDescription

    def __init__(
        self,
        coordinator: NapoleonHomeDataUpdateCoordinator,
        entity_description: NapoleonHomeTankDebugSensorEntityDescription,
    ) -> None:
        """Initialise the debug tank metadata sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def native_value(self) -> StateType:
        """Return current debug metadata value."""
        return self.entity_description.value_fn(self.coordinator.data)
