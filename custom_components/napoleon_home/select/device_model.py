"""Device model size select for napoleon_home."""

from __future__ import annotations

from typing import TYPE_CHECKING

# NOTE: FuelType is Prestige-specific (DTYPE encoding). This entity is
# nominally profile-generic (gated on has_gas_tank), but only Prestige is
# wired end-to-end so far — revisit this import if another profile grows a
# fuel-type concept with a different DTYPE-like encoding.
from custom_components.napoleon_home.device_profiles.prestige import FuelType
from custom_components.napoleon_home.entity import NapoleonHomeEntity
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory

if TYPE_CHECKING:
    from custom_components.napoleon_home.coordinator import NapoleonHomeDataUpdateCoordinator
    from custom_components.napoleon_home.device_profiles import DeviceProfile

_OPTIONS: list[str] = ["500", "665"]

# Maps (current fuel type, selected model size) -> new FuelType, preserving
# fuel type and only toggling model size. Fuel type is factory-set to match
# the physical hardware and must never change via this select.
_NEW_FUEL_TYPE: dict[tuple[FuelType, str], FuelType] = {
    (FuelType.PROPANE_500, "665"): FuelType.PROPANE_665,
    (FuelType.PROPANE_665, "500"): FuelType.PROPANE_500,
    (FuelType.NATURAL_GAS_500, "665"): FuelType.NATURAL_GAS_665,
    (FuelType.NATURAL_GAS_665, "500"): FuelType.NATURAL_GAS_500,
}


def build_entity_descriptions(profile: DeviceProfile) -> tuple[SelectEntityDescription, ...]:
    """Build the device model select description, or none for models with no fuel-type concept."""
    if not profile.capabilities.has_gas_tank:
        return ()
    return (
        SelectEntityDescription(
            key="device_model",
            translation_key="device_model",
            icon="mdi:grill",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    )


class NapoleonHomeDeviceModelSelect(SelectEntity, NapoleonHomeEntity):
    """Select controlling the device model size (500/665) half of DTYPE.

    Fuel type (propane vs natural gas) is factory-set to match the physical
    hardware and must never change — writes here only ever toggle model
    size, resolved via _NEW_FUEL_TYPE so the fuel-type half of DTYPE is
    always preserved exactly.
    """

    _attr_options = _OPTIONS

    def __init__(
        self,
        coordinator: NapoleonHomeDataUpdateCoordinator,
        entity_description: SelectEntityDescription,
    ) -> None:
        """Initialise the device model select."""
        super().__init__(coordinator, entity_description)

    @property
    def _current_fuel_type(self) -> FuelType | None:
        """Return the current FuelType, or None if not yet polled or unrecognized."""
        dtype = self.coordinator.data.dtype
        if dtype is None:
            return None
        try:
            return FuelType(dtype)
        except ValueError:
            return None

    @property
    def current_option(self) -> str | None:
        """Return the current device model size, or None if not yet polled or unrecognized."""
        fuel_type = self._current_fuel_type
        return str(fuel_type.model_size) if fuel_type is not None else None

    async def async_select_option(self, option: str) -> None:
        """Set the device model size on the grill, preserving the current fuel type."""
        current = self._current_fuel_type
        if current is None:
            return
        new_fuel_type = _NEW_FUEL_TYPE.get((current, option))
        if new_fuel_type is None:
            return
        await self.coordinator.async_set_property_by_concept("fuel_type", new_fuel_type.value)
        self.coordinator.data.dtype = new_fuel_type.value
        self.coordinator.async_set_updated_data(self.coordinator.data)
