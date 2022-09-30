"""Config flow for AerisWeather integration."""
from __future__ import annotations

from aerisweather.aerisweather import AerisWeather
from aerisweather.requests.RequestLocation import RequestLocation

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_LOCATION

import urllib.error

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    api = AerisWeather(data[CONF_CLIENT_ID], data[CONF_CLIENT_SECRET])

    try:
        await hass.async_add_executor_job(api.forecasts, RequestLocation(postal_code=data[CONF_LOCATION]))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise InvalidAuth
        else:
            raise e
    except Exception as e:
        raise e


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AerisWeather."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        schema = vol.Schema(
            {
                vol.Required(CONF_CLIENT_ID): str,
                vol.Required(CONF_CLIENT_SECRET): str,
                vol.Optional(CONF_LOCATION, default=f"{self.hass.config.latitude},{self.hass.config.longitude}"): str,
            }
        )

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=schema
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title="AerisWeather", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
