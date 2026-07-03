"""Tank calibration number entities for napoleon_home."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from custom_components.napoleon_home.entity import NapoleonHomeEntity
from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import EntityCategory, UnitOfMass
from homeassistant.util.unit_conversion import MassConverter

if TYPE_CHECKING:
    from custom_components.napoleon_home.coordinator import NapoleonHomeDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class NapoleonHomeTankCalibrationNumberEntityDescription(NumberEntityDescription):
    """Entity description for tank calibration numbers.

    Attributes:
        concept: The profile concept key backing this entity (``"empty_tank_weight"``
            or ``"full_tank_weight"``) — see the active DeviceProfile's
            ``properties`` map.

    """

    concept: str = ""


def build_entity_descriptions() -> tuple[NapoleonHomeTankCalibrationNumberEntityDescription, ...]:
    """Build the empty/full tank calibration number descriptions.

    Only ever called once a grill resolves to a portable propane tank — see
    ``NapoleonHomeDataUpdateCoordinator.async_add_gas_tank_listener``.
    """
    return (
        NapoleonHomeTankCalibrationNumberEntityDescription(
            key="empty_tank_weight",
            translation_key="empty_tank_weight",
            icon="mdi:propane-tank-outline",
            entity_category=EntityCategory.CONFIG,
            mode=NumberMode.BOX,
            native_step=0.1,
            concept="empty_tank_weight",
        ),
        NapoleonHomeTankCalibrationNumberEntityDescription(
            key="full_tank_weight",
            translation_key="full_tank_weight",
            icon="mdi:propane-tank",
            entity_category=EntityCategory.CONFIG,
            mode=NumberMode.BOX,
            native_step=0.1,
            concept="full_tank_weight",
        ),
    )


class NapoleonHomeTankCalibrationNumber(NumberEntity, NapoleonHomeEntity):
    """Number entities for empty/full tank calibration values.

    The grill always reports/accepts these in grams (EMTY_TNK_W, F_TNKWT);
    values are stored canonically in kilograms on NapoleonHomeGrillState and
    converted to/from lbs here for display and input when GS_UNT selects
    pounds.
    """

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
    def native_min_value(self) -> float:
        """Return the minimum calibration value in the current unit (0-200 kg range)."""
        if self.coordinator.data.gs_unt == 1:
            return MassConverter.convert(200, UnitOfMass.KILOGRAMS, UnitOfMass.POUNDS)
        return 0

    @property
    def native_max_value(self) -> float:
        """Return the maximum calibration value in the current unit (0-200 kg range)."""
        if self.coordinator.data.gs_unt == 1:
            return MassConverter.convert(200, UnitOfMass.KILOGRAMS, UnitOfMass.POUNDS)
        return 200

    @property
    def _value_kg(self) -> float | None:
        """Return the canonical (kilogram) calibration value for this entity's concept."""
        if self.entity_description.concept == "empty_tank_weight":
            return self.coordinator.data.empty_tank_weight
        return self.coordinator.data.full_tank_weight

    @property
    def native_value(self) -> float | None:
        """Return current calibration value, converted to lbs if that's the grill's configured unit."""
        value_kg = self._value_kg
        if value_kg is None:
            return None
        if self.coordinator.data.gs_unt == 1:
            return round(MassConverter.convert(value_kg, UnitOfMass.KILOGRAMS, UnitOfMass.POUNDS), 1)
        return value_kg

    async def async_set_native_value(self, value: float) -> None:
        """Set calibration value on the grill.

        ``value`` arrives in the currently displayed unit (kg or lbs per
        GS_UNT); convert to kilograms canonically, then to grams for the wire.
        """
        if self.coordinator.data.gs_unt == 1:
            value_kg = MassConverter.convert(value, UnitOfMass.POUNDS, UnitOfMass.KILOGRAMS)
        else:
            value_kg = value
        grams = round(MassConverter.convert(value_kg, UnitOfMass.KILOGRAMS, UnitOfMass.GRAMS))
        await self.coordinator.async_set_property_by_concept(self.entity_description.concept, grams)
        if self.entity_description.concept == "empty_tank_weight":
            self.coordinator.data.empty_tank_weight = value_kg
        else:
            self.coordinator.data.full_tank_weight = value_kg
        self.coordinator.async_set_updated_data(self.coordinator.data)
