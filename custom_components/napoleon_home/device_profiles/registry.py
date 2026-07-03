"""Device profile registry for napoleon_home.

Central lookup from a detected Ayla ``oem_model`` (or, as a last resort, an
advertised BLE name prefix) to the matching ``DeviceProfile``. Adding support
for a new grill model is a matter of building its profile module and
registering it in ``_PROFILES`` below — nothing else in this module changes.
"""

from __future__ import annotations

from custom_components.napoleon_home.const import LOGGER
from custom_components.napoleon_home.device_profiles.electric_grill import ELECTRIC_GRILL_PROFILE
from custom_components.napoleon_home.device_profiles.models import DeviceProfile
from custom_components.napoleon_home.device_profiles.prestige import PRESTIGE_PROFILE
from custom_components.napoleon_home.device_profiles.prestige_pro import PRESTIGE_PRO_PROFILE

_PROFILES: tuple[DeviceProfile, ...] = (PRESTIGE_PROFILE, PRESTIGE_PRO_PROFILE, ELECTRIC_GRILL_PROFILE)

_BY_KEY: dict[str, DeviceProfile] = {profile.key: profile for profile in _PROFILES}
_BY_OEM_MODEL: dict[str, DeviceProfile] = {
    oem_model: profile for profile in _PROFILES for oem_model in profile.oem_models
}

SUPPORTED_OEM_MODELS: frozenset[str] = frozenset(_BY_OEM_MODEL)

# Advertised BLE local-name prefixes across all registered (grill) profiles —
# a narrower subset of const.NAPOLEON_NAME_PREFIXES, which also matches
# non-grill Napoleon devices (fireplaces, thermostats, accessories) this
# integration doesn't support yet.
DEVICE_BLE_NAME_PREFIXES: tuple[str, ...] = tuple(
    prefix for profile in _PROFILES for prefix in profile.ble_name_prefixes
)


def get_profile_by_key(key: str) -> DeviceProfile:
    """Return the profile registered under ``key``.

    Raises:
        KeyError: If no profile is registered under that key.

    """
    return _BY_KEY[key]


def resolve_profile(oem_model: str | None, ble_name: str | None = None) -> DeviceProfile:
    """Resolve a ``DeviceProfile`` from a detected ``oem_model`` or BLE name.

    ``oem_model`` is an exact-match lookup and is authoritative regardless of
    whether it came from the BLE ``GATT_CHAR_OEM_MODEL`` (``00000003-fe28``)
    read at probe time or the Ayla cloud API at key-retrieval time — both are
    the same value space. ``ble_name`` (the freeform advertised local name) is
    only consulted as a last-resort fallback, prefix-matched against each
    profile's ``ble_name_prefixes``, for the rare case the GATT read fails.

    Never raises — detection must never block setup. Falls back to
    ``PRESTIGE_PROFILE`` with a warning if neither input resolves.
    """
    if oem_model is not None and oem_model in _BY_OEM_MODEL:
        return _BY_OEM_MODEL[oem_model]
    if ble_name:
        for profile in _PROFILES:
            if ble_name.startswith(profile.ble_name_prefixes):
                return profile
    LOGGER.warning(
        "Napoleon Home: could not resolve a device profile for oem_model=%r ble_name=%r — defaulting to Prestige",
        oem_model,
        ble_name,
    )
    return PRESTIGE_PROFILE
