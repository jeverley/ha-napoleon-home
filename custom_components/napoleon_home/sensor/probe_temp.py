"""Probe temperature sensors for napoleon_home."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from custom_components.napoleon_home.entity import NapoleonHomeEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import UnitOfTemperature
from homeassistant.util.unit_conversion import TemperatureConverter

if TYPE_CHECKING:
    from custom_components.napoleon_home.coordinator import NapoleonHomeDataUpdateCoordinator
    from custom_components.napoleon_home.device_profiles import DeviceProfile


@dataclass(frozen=True, kw_only=True)
class NapoleonHomeProbeTempSensorEntityDescription(SensorEntityDescription):
    """
    Entity description for a Napoleon Home probe temperature sensor.

    Extends ``SensorEntityDescription`` with a ``probe_id`` field so that a
    single entity class can serve every probe channel a profile defines.

    Attributes:
        probe_id: Probe channel ID, matching a ``ProbeChannel.id`` on the
            active DeviceProfile.

    """

    probe_id: int = 0


def build_entity_descriptions(profile: DeviceProfile) -> tuple[NapoleonHomeProbeTempSensorEntityDescription, ...]:
    """Build one temperature sensor description per readable probe channel on ``profile``."""
    return tuple(
        NapoleonHomeProbeTempSensorEntityDescription(
            key="grill" if probe.is_grill_channel else f"probe_{probe.id}",
            translation_key="grill" if probe.is_grill_channel else f"probe_{probe.id}",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            probe_id=probe.id,
        )
        for probe in profile.probes
        if probe.temp is not None
    )


class NapoleonHomeProbeTempSensor(SensorEntity, NapoleonHomeEntity):
    """
    Temperature sensor for a single Napoleon Home probe.

    Reports the current probe temperature in the unit selected on the grill
    (Celsius or Fahrenheit per the ``TUNIT`` property). Returns ``None`` when
    the probe is not connected or has not yet been polled.

    """

    entity_description: NapoleonHomeProbeTempSensorEntityDescription

    def __init__(
        self,
        coordinator: NapoleonHomeDataUpdateCoordinator,
        entity_description: NapoleonHomeProbeTempSensorEntityDescription,
    ) -> None:
        """
        Initialise the probe temperature sensor.

        Args:
            coordinator: The BLE coordinator managing grill state.
            entity_description: The entity description, including the probe channel ID.

        """
        super().__init__(coordinator, entity_description)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the temperature unit matching the grill's current TUNIT setting."""
        return UnitOfTemperature.CELSIUS if self.coordinator.data.tunit == 0 else UnitOfTemperature.FAHRENHEIT

    @property
    def native_value(self) -> float | None:
        """Return the current probe temperature, or None if unavailable.

        The grill always reports probe temperatures in Celsius; convert to
        Fahrenheit when that's the grill's configured display unit.
        """
        temp_c = self.coordinator.data.probe_temp(self.entity_description.probe_id)
        if temp_c is None:
            return None
        if self.coordinator.data.tunit == 1:
            return TemperatureConverter.convert(temp_c, UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT)
        return temp_c

    @property
    def _always_available(self) -> bool:
        """Return True if this channel has no connected-state bit (e.g. the grill's own probe slot)."""
        channel = next(p for p in self.coordinator.profile.probes if p.id == self.entity_description.probe_id)
        return channel.connected_bit is None

    @property
    def available(self) -> bool:
        """Return availability for probe and always-on temperature channels.

        Removable probes are unavailable when physically unplugged. Channels
        with no connected-state bit (e.g. Prestige's probe slot 4, which
        reports the grill's own temperature) remain available whenever BLE
        is authenticated.

        """
        if self._always_available:
            return self.coordinator.authenticated
        return self.coordinator.authenticated and self.coordinator.data.probe_connected(
            self.entity_description.probe_id
        )

    @property
    def icon(self) -> str:
        """Return icon for probe and always-on temperature channels."""
        if self._always_available:
            return "mdi:thermometer"
        return "mdi:thermometer-probe" if self.available else "mdi:thermometer-probe-off"
