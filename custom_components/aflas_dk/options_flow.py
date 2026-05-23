import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
import asyncio

from .api import AflasAPI
from . import DOMAIN


class AflasOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Aflas.dk."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            # Validate credentials
            valid = await self._async_validate(user_input)

            if valid is True:
                return self.async_create_entry(title="", data=user_input)
            else:
                errors["base"] = valid

        data = self.config_entry.data

        schema = vol.Schema({
            vol.Required("username", default=data.get("username")): str,
            vol.Required("password", default=data.get("password")): str,
            vol.Required("vaerknummer", default=data.get("vaerknummer")): str,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors
        )

    async def _async_validate(self, data):
        """Validate login credentials asynchronously."""

