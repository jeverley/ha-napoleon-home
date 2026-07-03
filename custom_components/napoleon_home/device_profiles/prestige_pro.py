"""Prestige Pro grill device profile for napoleon_home.

UNVERIFIED — property names and type codes below have not been confirmed
against real Prestige Pro hardware. Ayla Local Control v2 BLE support is
likely (the same generic Ayla local-control transport that Prestige uses is
not tied to a specific grill model) but is not hardware-verified for this
model — see ``verified_ble_local_control`` below.

Only the 4 wired probes and 2 ambient/lid sensors are modeled here. Prestige
Pro also has 2 wireless meat probes (with split battery properties
``BTR_LVL_PB_1``/``BTR_LVL_PB_2``), but their exact temperature/target
property names are not yet confirmed, so they are intentionally omitted
rather than guessed. Likewise, the smoker box (``SMKR_*``), RGB knob
(``KNOB_*``), dual light zones (``CBNT_L``/``HOOD_L``), and motion-sensor
lighting (``ID_MTN_SNSR``/``MTN_SNSR_TIME``) are flagged via
``DeviceCapabilities`` but have no property/entity wiring yet — building
those out is explicitly out of scope until hardware access confirms BLE
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

_STAT = PropertySpec(name="PRB_STAT", type_code=PROP_TYPE_INT)

PRESTIGE_PRO_PROFILE = DeviceProfile(
    key="prestige_pro",
    display_name="Prestige Pro",
    oem_models=frozenset({"provx-field-us", "provx-field-eu"}),
    ble_name_prefixes=("ProVX", "Pro"),
    verified_ble_local_control=False,
    probes=(
        ProbeChannel(
            id=1,
            label="Probe 1",
            temp=PropertySpec(name="PRB_TMP_ONE", type_code=PROP_TYPE_DECIMAL),
            target=PropertySpec(name="TRGT_TMP_ONE", type_code=PROP_TYPE_DECIMAL),
            connected_bit=0,
            stat_property=_STAT,
        ),
        ProbeChannel(
            id=2,
            label="Probe 2",
            temp=PropertySpec(name="PRB_TMP_TWO", type_code=PROP_TYPE_DECIMAL),
            target=PropertySpec(name="TRGT_TMP_TWO", type_code=PROP_TYPE_DECIMAL),
            connected_bit=1,
            stat_property=_STAT,
        ),
        ProbeChannel(
            id=3,
            label="Probe 3",
            temp=PropertySpec(name="PRB_TMP_THREE", type_code=PROP_TYPE_DECIMAL),
            target=PropertySpec(name="TRGT_TMP_THREE", type_code=PROP_TYPE_DECIMAL),
            connected_bit=2,
            stat_property=_STAT,
        ),
        ProbeChannel(
            id=4,
            label="Probe 4",
            temp=PropertySpec(name="PRB_TMP_FOUR", type_code=PROP_TYPE_DECIMAL),
            target=PropertySpec(name="TRGT_TMP_FOUR", type_code=PROP_TYPE_DECIMAL),
            connected_bit=3,
            stat_property=_STAT,
        ),
        # Ambient/lid sensors — separate from the removable-probe bitmask.
        ProbeChannel(
            id=5,
            label="Ambient 1",
            temp=PropertySpec(name="AMBNT_TMP_ONE", type_code=PROP_TYPE_DECIMAL),
            target=PropertySpec(name="TRGT_AMBNT_ONE", type_code=PROP_TYPE_DECIMAL),
            connected_bit=None,
            stat_property=None,
        ),
        ProbeChannel(
            id=6,
            label="Ambient 2",
            temp=PropertySpec(name="AMBNT_TMP_TWO", type_code=PROP_TYPE_DECIMAL),
            target=PropertySpec(name="TRGT_AMBNT_TWO", type_code=PROP_TYPE_DECIMAL),
            connected_bit=None,
            stat_property=None,
        ),
    ),
    capabilities=DeviceCapabilities(
        has_gas_tank=True,
        has_knob_backlight=False,
        has_display_brightness=False,
        has_auto_shutoff=True,
        has_battery=False,
        knob_count=1,
        has_smoker=True,
        has_knob_rgb=True,
        has_motion_sensor_lighting=True,
        ambient_zone_count=2,
        light_zone_count=2,
    ),
    properties={
        "temperature_unit": PropertySpec(name="T_UNIT", type_code=PROP_TYPE_INT),
        "battery_saver_mode": PropertySpec(name="BSMODE", type_code=PROP_TYPE_BOOL),
        "auto_shutoff": PropertySpec(name="AUTO_T_OUT", type_code=PROP_TYPE_INT),
        "power_off": PropertySpec(name="PWR_CNTRL", type_code=PROP_TYPE_BOOL, pollable=False),
        "gas_unit": PropertySpec(name="WEIGHT_UNIT", type_code=PROP_TYPE_INT),
        "region": PropertySpec(name="REGN", type_code=PROP_TYPE_STRING),
        "country": PropertySpec(name="CNTRY", type_code=PROP_TYPE_STRING),
        "gas_tank_name": PropertySpec(name="GS_TNK_NAME", type_code=PROP_TYPE_STRING),
        "empty_tank_weight": PropertySpec(name="EMTY_TNK_WT", type_code=PROP_TYPE_INT),
        "full_tank_weight": PropertySpec(name="F_TNK_WT", type_code=PROP_TYPE_INT),
        "tank_weight": PropertySpec(name="TNK_WGHT", type_code=PROP_TYPE_DECIMAL),
        "firmware_version": PropertySpec(name="version", type_code=PROP_TYPE_STRING),
    },
)
