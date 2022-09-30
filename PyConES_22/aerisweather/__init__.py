"""The AerisWeather integration."""
from __future__ import annotations

from aerisweather.aerisweather import AerisWeather
from aerisweather.requests.RequestLocation import RequestLocation

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_LOCATION
from homeassistant.core import HomeAssistant

from .const import DOMAIN, ENTRY_API, ENTRY_LOCATION

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.WEATHER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AerisWeather as config entry."""
    api = AerisWeather(entry.data[CONF_CLIENT_ID], entry.data[CONF_CLIENT_SECRET])

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        ENTRY_API: api,
        ENTRY_LOCATION: RequestLocation(postal_code=entry.data[CONF_LOCATION]),
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
