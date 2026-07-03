"""Device profiles for napoleon_home.

Public surface for per-grill-model support: a ``DeviceProfile`` describes the
Ayla properties, probes, and capabilities for one grill line, and the
registry resolves a detected ``oem_model``/BLE name to the matching profile.
Other packages should import from here, not from the individual profile
modules.
"""

from __future__ import annotations

from custom_components.napoleon_home.device_profiles.electric_grill import ELECTRIC_GRILL_PROFILE
from custom_components.napoleon_home.device_profiles.models import (
    DeviceCapabilities,
    DeviceProfile,
    ProbeChannel,
    PropertySpec,
)
from custom_components.napoleon_home.device_profiles.prestige import PRESTIGE_PROFILE
from custom_components.napoleon_home.device_profiles.prestige_pro import PRESTIGE_PRO_PROFILE
from custom_components.napoleon_home.device_profiles.registry import (
    DEVICE_BLE_NAME_PREFIXES,
    SUPPORTED_OEM_MODELS,
    get_profile_by_key,
    resolve_profile,
)

__all__ = [
    "DEVICE_BLE_NAME_PREFIXES",
    "ELECTRIC_GRILL_PROFILE",
    "PRESTIGE_PROFILE",
    "PRESTIGE_PRO_PROFILE",
    "SUPPORTED_OEM_MODELS",
    "DeviceCapabilities",
    "DeviceProfile",
    "ProbeChannel",
    "PropertySpec",
    "get_profile_by_key",
    "resolve_profile",
]
