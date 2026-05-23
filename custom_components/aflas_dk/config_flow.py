from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .api import AflasAPI
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AflasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial configuration flow for Aflas.dk."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle user input for initial setup."""
        errors = {}

        if user_input is not None:
            username = user_input["username"]
            password = user_input["password"]
            vaerknummer = user_input["vaerknummer"]

            api = AflasAPI(username, password, vaerknummer)

            result = await self.hass.async_add_executor_job(api.validate_login)

            if result is True:
                return self.async_create_entry(
                    title=f"Aflas.dk ({vaerknummer})",
                    data=user_input,
                    options={"update_interval": 60},  # default 60 minutes
                )

            if result == "invalid_auth":
                errors["base"] = "invalid_auth"
            else:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Required("vaerknummer"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AflasOptionsFlowHandler(config_entry)


class AflasOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Aflas.dk options (update interval)."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "update_interval",
                        default=options.get("update_interval", 60),
                    ): vol.In([5, 10, 30, 60, 120]),
                }
            ),
        )

