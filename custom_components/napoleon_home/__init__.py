"""Custom integration to integrate napoleon_home with Home Assistant."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from homeassistant.components.bluetooth import async_rediscover_address
from homeassistant.const import CONF_REGION, Platform
import homeassistant.helpers.config_validation as cv

from .const import (
    AYLA_OEM_MODEL_PRESTIGE,
    AYLA_OEM_MODEL_PRESTIGE_EU,
    AYLA_REGION_US,
    CONF_BT_MAC,
    CONF_DEVICES,
    CONF_MODEL,
    CONF_OEM_MODEL,
    DOMAIN,
    LOGGER,
)
from .coordinator import NapoleonHomeDataUpdateCoordinator
from .device_profiles import PRESTIGE_PROFILE

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceEntry

    from .data import NapoleonHomeConfigEntry, NapoleonHomeCoordinators

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_migrate_entry(
    hass: HomeAssistant,
    entry: NapoleonHomeConfigEntry,
) -> bool:
    """
    Migrate a config entry to the current schema version.

    1.1 -> 1.2: adds CONF_MODEL/CONF_OEM_MODEL to each device dict, needed to
    resolve a DeviceProfile now that the integration supports more than one
    grill model. Every device configured before this version was necessarily
    a Prestige grill (the Ayla cloud API only ever returned Prestige devices
    before this change), so backfilling is deterministic and lossless.
    """
    if entry.version > 1 or (entry.version == 1 and entry.minor_version > 2):
        LOGGER.error(
            "Napoleon Home: cannot downgrade config entry from version %s.%s",
            entry.version,
            entry.minor_version,
        )
        return False

    if entry.minor_version < 2:
        is_us = entry.data.get(CONF_REGION) == AYLA_REGION_US
        oem_model = AYLA_OEM_MODEL_PRESTIGE if is_us else AYLA_OEM_MODEL_PRESTIGE_EU
        updated_devices = {
            dsn: (
                device
                if CONF_MODEL in device
                else {**device, CONF_MODEL: PRESTIGE_PROFILE.key, CONF_OEM_MODEL: oem_model}
            )
            for dsn, device in entry.data.get(CONF_DEVICES, {}).items()
        }
        hass.config_entries.async_update_entry(
            entry,
            data={**entry.data, CONF_DEVICES: updated_devices},
            minor_version=2,
        )
        LOGGER.debug("Napoleon Home: migrated config entry %s to minor_version=2", entry.entry_id)

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NapoleonHomeConfigEntry,
) -> bool:
    """Set up Napoleon Home from a config entry."""
    coordinators: NapoleonHomeCoordinators = {
        dsn: NapoleonHomeDataUpdateCoordinator(hass, entry, dsn) for dsn in entry.data.get(CONF_DEVICES, {})
    }
    entry.runtime_data = coordinators
    await asyncio.gather(*(c.async_config_entry_first_refresh() for c in coordinators.values()))
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: NapoleonHomeConfigEntry,
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    for coordinator in entry.runtime_data.values():
        await coordinator.async_shutdown()
    return unload_ok


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    entry: NapoleonHomeConfigEntry,
    device_entry: DeviceEntry,
) -> bool:
    """Remove a grill device and its data when deleted from the UI."""
    dsn = next(
        (identifier for domain, identifier in device_entry.identifiers if domain == DOMAIN),
        None,
    )
    if dsn is None:
        return False
    devices = entry.data.get(CONF_DEVICES, {})
    if dsn not in devices:
        return True
    coordinator = entry.runtime_data.pop(dsn, None)
    mac = devices[dsn].get(CONF_BT_MAC)
    if coordinator is not None:
        await coordinator.async_shutdown()
    hass.config_entries.async_update_entry(
        entry,
        data={**entry.data, CONF_DEVICES: {d: v for d, v in devices.items() if d != dsn}},
    )
    if mac:
        async_rediscover_address(hass, mac)
    return True


async def async_reload_entry(
    hass: HomeAssistant,
    entry: NapoleonHomeConfigEntry,
) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
