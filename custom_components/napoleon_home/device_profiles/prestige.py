"""Prestige grill device profile for napoleon_home.

Hardware-confirmed baseline profile — Ayla Local Control v2 BLE support was
verified against real hardware (see AGENTS.md's HMAC/GATT notes). Every wire
property name below is sourced from the existing ``const.py`` constants that
already drive this integration's working Prestige implementation, so this
profile is behaviorally identical to the pre-refactor static ``POLL_PROPS``
and entity descriptions.
"""

from __future__ import annotations

from custom_components.napoleon_home.const import (
    AYLA_OEM_MODEL_PRESTIGE,
    AYLA_OEM_MODEL_PRESTIGE_EU,
    PROP_AUTO_T_OUT,
    PROP_BATTERY_LOW_ALERT,
    PROP_BRT_LVL,
    PROP_BSMODE,
    PROP_BT_LVL,
    PROP_CNTRY,
    PROP_EMTY_TNK_W,
    PROP_F_TNKWT,
    PROP_GS_TNK_NAME,
    PROP_GS_UNT,
    PROP_LCD_OFF,
    PROP_PRB_STAT,
    PROP_PRB_TEMPS,
    PROP_REGN,
    PROP_TGT_TEMPS,
    PROP_TNK_WT,
    PROP_TOFF,
    PROP_TUNIT,
    PROP_TYPE_BOOL,
    PROP_TYPE_DECIMAL,
    PROP_TYPE_INT,
    PROP_TYPE_STRING,
    PROP_VERSION,
)
from custom_components.napoleon_home.device_profiles.models import (
    DeviceCapabilities,
    DeviceProfile,
    ProbeChannel,
    PropertySpec,
)

_STAT = PropertySpec(name=PROP_PRB_STAT, type_code=PROP_TYPE_INT)

PRESTIGE_PROFILE = DeviceProfile(
    key="prestige",
    display_name="Prestige",
    oem_models=frozenset({AYLA_OEM_MODEL_PRESTIGE, AYLA_OEM_MODEL_PRESTIGE_EU}),
    ble_name_prefixes=("Prestige",),
    verified_ble_local_control=True,
    probes=(
        ProbeChannel(
            id=1,
            label="Probe 1",
            temp=PropertySpec(name=PROP_PRB_TEMPS[0], type_code=PROP_TYPE_DECIMAL),
            target=PropertySpec(name=PROP_TGT_TEMPS[0], type_code=PROP_TYPE_DECIMAL),
            connected_bit=0,
            stat_property=_STAT,
        ),
        ProbeChannel(
            id=2,
            label="Probe 2",
            temp=PropertySpec(name=PROP_PRB_TEMPS[1], type_code=PROP_TYPE_DECIMAL),
            target=PropertySpec(name=PROP_TGT_TEMPS[1], type_code=PROP_TYPE_DECIMAL),
            connected_bit=1,
            stat_property=_STAT,
        ),
        ProbeChannel(
            id=3,
            label="Probe 3",
            temp=PropertySpec(name=PROP_PRB_TEMPS[2], type_code=PROP_TYPE_DECIMAL),
            target=PropertySpec(name=PROP_TGT_TEMPS[2], type_code=PROP_TYPE_DECIMAL),
            connected_bit=2,
            stat_property=_STAT,
        ),
        # Probe slot 4 reports the grill's own temperature (not a removable
        # probe) and is always available whenever BLE is authenticated.
        ProbeChannel(
            id=4,
            label="Grill",
            temp=PropertySpec(name=PROP_PRB_TEMPS[3], type_code=PROP_TYPE_DECIMAL),
            target=PropertySpec(name=PROP_TGT_TEMPS[3], type_code=PROP_TYPE_DECIMAL),
            connected_bit=None,
            stat_property=None,
            is_grill_channel=True,
        ),
    ),
    capabilities=DeviceCapabilities(
        has_gas_tank=True,
        has_knob_backlight=True,
        has_display_brightness=True,
        has_auto_shutoff=True,
        has_battery=True,
        knob_count=1,
    ),
    properties={
        "temperature_unit": PropertySpec(name=PROP_TUNIT, type_code=PROP_TYPE_INT),
        "battery_saver_mode": PropertySpec(name=PROP_BSMODE, type_code=PROP_TYPE_BOOL),
        "knob_backlight": PropertySpec(name=PROP_LCD_OFF, type_code=PROP_TYPE_BOOL),
        "display_brightness": PropertySpec(name=PROP_BRT_LVL, type_code=PROP_TYPE_INT),
        "auto_shutoff": PropertySpec(name=PROP_AUTO_T_OUT, type_code=PROP_TYPE_INT),
        "power_off": PropertySpec(name=PROP_TOFF, type_code=PROP_TYPE_BOOL, pollable=False),
        "gas_unit": PropertySpec(name=PROP_GS_UNT, type_code=PROP_TYPE_INT),
        "region": PropertySpec(name=PROP_REGN, type_code=PROP_TYPE_STRING),
        "country": PropertySpec(name=PROP_CNTRY, type_code=PROP_TYPE_STRING),
        "gas_tank_name": PropertySpec(name=PROP_GS_TNK_NAME, type_code=PROP_TYPE_STRING),
        "empty_tank_weight": PropertySpec(name=PROP_EMTY_TNK_W, type_code=PROP_TYPE_INT),
        "full_tank_weight": PropertySpec(name=PROP_F_TNKWT, type_code=PROP_TYPE_INT),
        "battery_level": PropertySpec(name=PROP_BT_LVL, type_code=PROP_TYPE_INT),
        "battery_low_alert": PropertySpec(name=PROP_BATTERY_LOW_ALERT, type_code=PROP_TYPE_BOOL),
        "tank_weight": PropertySpec(name=PROP_TNK_WT, type_code=PROP_TYPE_DECIMAL),
        "firmware_version": PropertySpec(name=PROP_VERSION, type_code=PROP_TYPE_STRING),
    },
)
