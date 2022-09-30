"""Support for the AerisWeather service."""
from datetime import timedelta

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_PRECIPITATION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    WeatherEntity,
    Forecast
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    LENGTH_MILLIMETERS,
    PRESSURE_MBAR,
    SPEED_KILOMETERS_PER_HOUR,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTRIBUTION, ENTRY_API, ENTRY_LOCATION


SCAN_INTERVAL = timedelta(minutes=30)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AerisWeather weather entity based on a config entry."""
    domain_data = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([AerisWeather(config_entry.unique_id, domain_data[ENTRY_API], domain_data[ENTRY_LOCATION])], True)


class AerisWeather(WeatherEntity):
    """Implementation of an AerisWeather sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_native_precipitation_unit = LENGTH_MILLIMETERS
    _attr_native_pressure_unit = PRESSURE_MBAR
    _attr_native_temperature_unit = TEMP_CELSIUS
    _attr_native_wind_speed_unit = SPEED_KILOMETERS_PER_HOUR

    def __init__(
        self,
        unique_id,
        api,
        location
    ):
        """Initialize the sensor."""
        self._attr_name = unique_id
        self._attr_unique_id = unique_id

        self._api = api
        self._location = location
        self._data = None

    async def async_update(self):
        self._data = await self._get_weather()

    async def _get_weather(self):
        """Poll weather data from AerisWeather."""
        weather = await self.hass.async_add_executor_job(self._api.forecasts, self._location)
        return weather

    @property
    def condition(self):
        """Return the current condition."""
        return self._data and self._data[0].periods[0].weather

    @property
    def forecast(self):
        """Return the forecast array."""
        if not self._data:
            return []
        return [
            Forecast(
                datetime=p.dateTimeISO,
                native_temperature=p.maxTempC,
                condition=p.weather,
                native_templow=p.minTempC,
                native_pressure=p.pressureMB,
            ) for p in self._data[0].periods
        ]

    @property
    def humidity(self):
        """Return the humidity."""
        return self._data and self._data[0].periods[0].humidity

    @property
    def native_pressure(self):
        """Return the pressure."""
        return self._data and self._data[0].periods[0].pressureMB

    @property
    def native_temperature(self):
        """Return the temperature."""
        return self._data and self._data[0].periods[0].tempC
