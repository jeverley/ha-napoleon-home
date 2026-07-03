"""
Device profile data model for napoleon_home.

Pure-data definitions describing what Ayla properties, probes, and features
each supported grill model exposes. No Home Assistant imports here — keeps
this module trivially testable and free of import-order concerns.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class PropertySpec:
    """An Ayla property's wire name and type code.

    Attributes:
        name: The Ayla property name as sent/received over BLE (e.g. ``"TUNIT"``,
            ``"current_probe_one_f"``). Naming convention varies by grill model.
        type_code: The Ayla type code for this property (``PROP_TYPE_*`` from
            ``const.py``), required for ``Opr`` writes.
        pollable: Whether this property should be included in the ``Gpr`` poll
            cycle. False for momentary command properties (e.g. a power-off
            trigger) that have no meaningful "current value" to read back.

    """

    name: str
    type_code: int
    pollable: bool = True


@dataclass(frozen=True, kw_only=True)
class ProbeChannel:
    """A single probe/zone temperature channel on a grill.

    Generalizes the previous fixed ``range(1, 5)`` probe loop so profiles with
    a different probe count or connectivity model (e.g. always-on channels,
    wireless probes with per-pair battery levels) can be represented.

    Attributes:
        id: Stable 1-based channel index, used in entity unique IDs/keys.
        label: Fallback display label for this channel.
        temp: Current-temperature property, or None if this channel has no
            readable temperature (unlikely, but keeps the field honest).
        target: Target-temperature property, or None if not settable.
        connected_bit: Bit index into the channel's ``stat_property`` bitmask
            indicating whether this channel is physically connected. None means
            the channel is always considered available (no bitmask gates it —
            true both for a grill's own temperature channel and, on some
            models, for meat probes that simply have no connected-state bit).
        stat_property: The bitmask property backing ``connected_bit``. Usually
            shared across all probes on a model, but kept per-channel to
            support models with separate bitmasks per probe group.
        is_grill_channel: Whether this channel reports the grill body's own
            temperature rather than a removable probe (e.g. Prestige's probe
            slot 4). Distinct from ``connected_bit is None`` — a model can
            have multiple always-available channels that are still ordinary
            probes, not the grill itself. Drives the "grill"/"grill_target"
            entity key instead of a numbered probe key.

    """

    id: int
    label: str
    temp: PropertySpec | None = None
    target: PropertySpec | None = None
    connected_bit: int | None = None
    stat_property: PropertySpec | None = None
    is_grill_channel: bool = False


@dataclass(frozen=True, kw_only=True)
class DeviceCapabilities:
    """Feature flags gating which entities a profile creates.

    Defaults are all "off"/minimal so a new profile that only sets a few
    flags doesn't need to enumerate every field.

    Attributes:
        has_gas_tank: Whether the grill has a propane tank weight sensor.
        has_knob_backlight: Whether the control knob has an on/off backlight.
        has_display_brightness: Whether the display has adjustable brightness.
        has_auto_shutoff: Whether an auto-shutoff timeout is configurable.
        has_battery: Whether the grill reports a battery level.
        knob_count: Number of independently-controllable knobs.
        has_smoker: Whether an integrated smoker box is present (Prestige Pro).
        has_knob_rgb: Whether the knob has RGB illumination (Prestige Pro).
        has_oven_mode: Whether a separate oven heating zone exists (Electric Grill).
        has_motion_sensor_lighting: Whether motion-sensor-triggered lighting exists.
        ambient_zone_count: Number of ambient/lid temperature sensors, if any.
        light_zone_count: Number of independently-controllable light zones.

    """

    has_gas_tank: bool = False
    has_knob_backlight: bool = False
    has_display_brightness: bool = False
    has_auto_shutoff: bool = False
    has_battery: bool = False
    knob_count: int = 1

    # Placeholders for documented-but-unbuilt follow-up features. No platform
    # code reads these yet — see the multi-model framework plan for scope.
    has_smoker: bool = False
    has_knob_rgb: bool = False
    has_oven_mode: bool = False
    has_motion_sensor_lighting: bool = False
    ambient_zone_count: int = 0
    light_zone_count: int = 1


@dataclass(frozen=True, kw_only=True)
class DeviceProfile:
    """Everything the coordinator/entity layer needs to support one grill model.

    Attributes:
        key: Stable profile identifier persisted in config entry data (e.g.
            ``"prestige"``). Never derived from a display string.
        display_name: Human-readable model name shown as ``DeviceInfo.model``.
        oem_models: Ayla cloud/GATT ``oem_model`` strings that resolve to this
            profile (e.g. ``{"thermometer-mqtt-eu", "thermometer-mqtt-us"}``).
        ble_name_prefixes: Advertised BLE local-name prefixes for this model,
            used only as a last-resort fallback when the ``oem_model`` GATT
            characteristic can't be read.
        verified_ble_local_control: Whether Ayla Local Control v2 BLE support
            has been confirmed on real hardware for this model. False means
            the property data below is unconfirmed — see the profile module's
            docstring for detail.
        probes: Probe/zone temperature channels for this model.
        capabilities: Feature flags gating optional entity families.
        properties: Concept name -> ``PropertySpec`` for every non-probe
            property this model exposes. Keying by a stable concept name
            (rather than the raw wire name) is what lets entity code stay
            model-agnostic across completely different naming conventions.

    """

    key: str
    display_name: str
    oem_models: frozenset[str]
    ble_name_prefixes: tuple[str, ...]
    verified_ble_local_control: bool
    probes: tuple[ProbeChannel, ...]
    capabilities: DeviceCapabilities
    properties: Mapping[str, PropertySpec]

    @property
    def poll_properties(self) -> list[str]:
        """Return the flattened list of wire property names to ``Gpr``-poll every cycle."""
        names: list[str] = [spec.name for spec in self.properties.values() if spec.pollable]
        for probe in self.probes:
            for spec in (probe.temp, probe.target, probe.stat_property):
                if spec is not None and spec.name not in names:
                    names.append(spec.name)
        return names
