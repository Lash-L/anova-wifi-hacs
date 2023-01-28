"""The Anova integration."""
from __future__ import annotations

from anova_wifi import AnovaOffline, AnovaPrecisionCooker, AnovaPrecisionCookerSensor

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import ANOVA_CLIENT, ANOVA_FIRMWARE_VERSION, DOMAIN

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Anova from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    apc = AnovaPrecisionCooker()
    try:
        update = await apc.update(entry.data["device_id"])
    except (AnovaOffline) as ex:
        raise ConfigEntryNotReady("Can not connect to the sous vide") from ex
    hass.data[DOMAIN][entry.entry_id] = {
        ANOVA_CLIENT: AnovaPrecisionCooker(),
        ANOVA_FIRMWARE_VERSION: update["sensors"][
            AnovaPrecisionCookerSensor.FIRMWARE_VERSION
        ],
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
