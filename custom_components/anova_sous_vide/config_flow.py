"""Config flow for Anova."""
from __future__ import annotations

import voluptuous as vol
from anova_wifi import AnovaApi
from anova_wifi import AnovaOffline
from anova_wifi import InvalidLogin
from anova_wifi import NoDevicesFound
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.const import CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN


class AnovaConfligFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Sets up a config flow for Anova."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""
        errors: dict[str, str] = {}
        if user_input is not None:
            api = AnovaApi(
                aiohttp_client.async_get_clientsession(self.hass),
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )
            await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
            self._abort_if_unique_id_configured()
            try:
                await api.authenticate()
            except AnovaOffline:
                errors["base"] = "cannot_connect"
            except InvalidLogin:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "unknown"
            else:
                try:
                    devices = await api.get_devices()
                    device_list = [
                        (device.device_key, device.type) for device in devices
                    ]
                    return self.async_create_entry(
                        title="Anova Sous Vide",
                        data={"jwt": api.jwt, "devices": device_list},
                    )

                except NoDevicesFound:
                    errors["base"] = "no_devices_found"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
            ),
            errors=errors,
        )
