"""Gas unit select for napoleon_home."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.napoleon_home.entity import NapoleonHomeEntity
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory

if TYPE_CHECKING:
    from custom_components.napoleon_home.coordinator import NapoleonHomeDataUpdateCoordinator
    from custom_components.napoleon_home.device_profiles import DeviceProfile

_OPTIONS: dict[int, str] = {0: "kg", 1: "lbs"}
_OPTIONS_INV: dict[str, int] = {v: k for k, v in _OPTIONS.items()}


def build_entity_descriptions(profile: DeviceProfile) -> tuple[SelectEntityDescription, ...]:
    """Build the gas unit select description, or none for models with no gas tank."""
    if not profile.capabilities.has_gas_tank:
        return ()
    return (
        SelectEntityDescription(
            key="tank_unit",
            translation_key="tank_unit",
            icon="mdi:propane-tank",
            entity_category=EntityCategory.CONFIG,
        ),
    )


class NapoleonHomeGasUnitSelect(SelectEntity, NapoleonHomeEntity):
    """Select controlling the gas tank weight unit (kg / lbs)."""

    _attr_options = list(_OPTIONS.values())

    def __init__(
        self,
        coordinator: NapoleonHomeDataUpdateCoordinator,
        entity_description: SelectEntityDescription,
    ) -> None:
        """Initialise the gas unit select."""
        super().__init__(coordinator, entity_description)

    @property
    def current_option(self) -> str | None:
        """Return the current gas unit option."""
        return _OPTIONS.get(self.coordinator.data.gs_unt)

    async def async_select_option(self, option: str) -> None:
        """Set the gas tank weight unit on the grill."""
        value = _OPTIONS_INV[option]
        await self.coordinator.async_set_property_by_concept("gas_unit", value)
        self.coordinator.data.gs_unt = value
        self.coordinator.async_set_updated_data(self.coordinator.data)
