"""Electric Grill device profile for napoleon_home.

UNVERIFIED — property names and type codes below have not been confirmed
against real Electric Grill hardware. As with Prestige Pro, BLE local-control
support is likely but hardware-unverified — see ``verified_ble_local_control``
below.

This model uses an entirely different ``lower_snake_case`` property-naming
convention with units embedded in key names, has only 2 probes and no gas
tank (it's electric, not propane), and has oven/smoke/self-clean sub-modes
and two independently-controllable knobs that Prestige/Prestige Pro lack.
Only the properties needed to represent probes and the headline modes are
captured here — building entities for oven mode, smoke mode, self-clean, and
grease-fire notifications is out of scope until hardware access confirms BLE
support (see the multi-model framework plan).
"""

from __future__ import annotations

from custom_components.napoleon_home.const import PROP_TYPE_BOOL, PROP_TYPE_DECIMAL, PROP_TYPE_INT, PROP_TYPE_STRING
from custom_components.napoleon_home.device_profiles.models import (
    DeviceCapabilities,
    DeviceProfile,
    ProbeChannel,
    PropertySpec,
)

ELECTRIC_GRILL_PROFILE = DeviceProfile(
    key="electric_grill",
    display_name="Electric Grill",
    oem_models=frozenset({"R365EQ-Field", "R365EQ-eu", "REQ365-field-us", "REQ365-field-eu"}),
    ble_name_prefixes=("R365EQ",),
    verified_ble_local_control=False,
    probes=(
        # No stat/connected bitmask was found for this model — both channels
        # are treated as always available whenever BLE is authenticated.
        ProbeChannel(
            id=1,
            label="Probe 1",
            temp=PropertySpec(name="current_probe_one_f", type_code=PROP_TYPE_DECIMAL),
            target=PropertySpec(name="set_probe_one_f", type_code=PROP_TYPE_DECIMAL),
            connected_bit=None,
            stat_property=None,
        ),
        ProbeChannel(
            id=2,
            label="Probe 2",
            temp=PropertySpec(name="current_probe_two_f", type_code=PROP_TYPE_DECIMAL),
            target=PropertySpec(name="set_probe_two_f", type_code=PROP_TYPE_DECIMAL),
            connected_bit=None,
            stat_property=None,
        ),
    ),
    capabilities=DeviceCapabilities(
        has_gas_tank=False,
        has_knob_backlight=False,
        has_display_brightness=False,
        has_auto_shutoff=False,
        has_battery=False,
        knob_count=2,
        has_oven_mode=True,
    ),
    properties={
        "temperature_unit": PropertySpec(name="temp_unit_change", type_code=PROP_TYPE_INT),
        "power": PropertySpec(name="power_on_off", type_code=PROP_TYPE_BOOL),
        "grill_mode": PropertySpec(name="grill_mode_on_off", type_code=PROP_TYPE_BOOL),
        "grill_temp": PropertySpec(name="current_grill_temp_f", type_code=PROP_TYPE_DECIMAL),
        "oven_mode": PropertySpec(name="oven_mode_on_off", type_code=PROP_TYPE_BOOL),
        "oven_target_temp": PropertySpec(name="oven_mode_set_temp_f", type_code=PROP_TYPE_DECIMAL),
        "smoke_mode": PropertySpec(name="smoke_mode_on_off", type_code=PROP_TYPE_BOOL),
        "smoke_level": PropertySpec(name="smoke_mode_set_level", type_code=PROP_TYPE_INT),
        "smoke_target_temp": PropertySpec(name="smoke_mode_set_temp_f", type_code=PROP_TYPE_DECIMAL),
        "clean_mode": PropertySpec(name="clean_mode_on_off", type_code=PROP_TYPE_BOOL),
        "clean_minutes": PropertySpec(name="clean_mode_set_minute", type_code=PROP_TYPE_INT),
        "timer_enabled": PropertySpec(name="set_timer_on_off", type_code=PROP_TYPE_BOOL),
        "timer_seconds": PropertySpec(name="set_time_second", type_code=PROP_TYPE_INT),
        "notification_to_app": PropertySpec(name="notification_to_app", type_code=PROP_TYPE_STRING),
        "firmware_version": PropertySpec(name="version", type_code=PROP_TYPE_STRING),
    },
)
