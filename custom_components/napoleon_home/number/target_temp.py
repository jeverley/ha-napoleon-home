"""Target temperature number entities for napoleon_home."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from custom_components.napoleon_home.entity import NapoleonHomeEntity
from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import UnitOfTemperature

if TYPE_CHECKING:
    from custom_components.napoleon_home.coordinator import NapoleonHomeDataUpdateCoordinator
    from custom_components.napoleon_home.device_profiles import DeviceProfile


@dataclass(frozen=True, kw_only=True)
class NapoleonHomeTargetTempNumberEntityDescription(NumberEntityDescription):
    """Entity description for a Napoleon Home target temperature number.

    Attributes:
        probe_id: Probe channel ID, matching a ``ProbeChannel.id`` on the
            active DeviceProfile.

    """

    probe_id: int = 0


def build_entity_descriptions(profile: DeviceProfile) -> tuple[NapoleonHomeTargetTempNumberEntityDescription, ...]:
    """Build one target-temperature number description per settable probe channel on ``profile``."""
    return tuple(
        NapoleonHomeTargetTempNumberEntityDescription(
            key="grill_target" if probe.is_grill_channel else f"probe_{probe.id}_target",
            translation_key="grill_target" if probe.is_grill_channel else f"probe_{probe.id}_target",
            mode=NumberMode.BOX,
            native_step=1.0,
            probe_id=probe.id,
        )
        for probe in profile.probes
        if probe.target is not None
    )


class NapoleonHomeTargetTempNumber(NumberEntity, NapoleonHomeEntity):
    """Number entity for setting a target temperature on a Napoleon Home probe.

    The native unit and min/max range adjust dynamically to match the grill's
    current temperature unit setting (TUNIT: 0 = Celsius, 1 = Fahrenheit).

    """

    entity_description: NapoleonHomeTargetTempNumberEntityDescription

    def __init__(
        self,
        coordinator: NapoleonHomeDataUpdateCoordinator,
        entity_description: NapoleonHomeTargetTempNumberEntityDescription,
    ) -> None:
        """Initialise the target temperature number."""
        super().__init__(coordinator, entity_description)

    @property
    def _channel_always_available(self) -> bool:
        """Return True if this channel has no connected-state bit (e.g. the grill's own probe slot)."""
        channel = next(p for p in self.coordinator.profile.probes if p.id == self.entity_description.probe_id)
        return channel.connected_bit is None

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the temperature unit matching the grill's current TUNIT setting."""
        return UnitOfTemperature.CELSIUS if self.coordinator.data.tunit == 0 else UnitOfTemperature.FAHRENHEIT

    @property
    def native_min_value(self) -> float:
        """Return the minimum settable temperature in the current unit."""
        return 40.0 if self.coordinator.data.tunit == 0 else 100.0

    @property
    def native_max_value(self) -> float:
        """Return the maximum settable temperature in the current unit."""
        return 380.0 if self.coordinator.data.tunit == 0 else 720.0

    @property
    def native_value(self) -> float | None:
        """Return the current target temperature, or None if not yet received."""
        return self.coordinator.data.target_temps.get(self.entity_description.probe_id)

    @property
    def available(self) -> bool:
        """Return availability for probe targets and always-on target channels.

        Removable probe targets are unavailable when physically unplugged.
        Channels with no connected-state bit (e.g. Prestige's probe slot 4)
        remain available whenever BLE is authenticated.

        """
        if self._channel_always_available:
            return self.coordinator.authenticated
        return self.coordinator.authenticated and self.coordinator.data.probe_connected(
            self.entity_description.probe_id
        )

    @property
    def icon(self) -> str:
        """Return icon for probe and always-on target channels."""
        if self._channel_always_available:
            return "mdi:thermometer"
        return "mdi:thermometer-probe" if self.available else "mdi:thermometer-probe-off"

    async def async_set_native_value(self, value: float) -> None:
        """Set the target temperature for this probe on the grill."""
        channel = next(p for p in self.coordinator.profile.probes if p.id == self.entity_description.probe_id)
        spec = channel.target
        if spec is None:
            return
        await self.coordinator.async_set_property(spec.name, spec.type_code, value)
