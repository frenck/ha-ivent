"""Config flow for i-Vent integration."""
import logging
import voluptuous as vol
import aiohttp
import async_timeout

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_API_KEY, CONF_LOCATION_ID, API_BASE_URL

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default="i-Vent"): str,
        vol.Required(CONF_API_KEY): str,
        vol.Required(CONF_LOCATION_ID): int,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, any]) -> dict[str, any]:
    """Validate the user input allows us to connect."""
    
    api_key = data[CONF_API_KEY]
    location_id = data[CONF_LOCATION_ID]
    
    url = f"{API_BASE_URL}/live/{location_id}/info"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with async_timeout.timeout(10):
                async with session.get(url, headers=headers) as response:
                    if response.status == 404:
                        raise InvalidLocation
                    elif response.status == 401:
                        raise InvalidAuth
                    elif response.status != 200:
                        raise CannotConnect
                    
                    result = await response.json()
                    return {"title": data[CONF_NAME], "groups": result.get("groups", [])}
        except asyncio.TimeoutError:
            raise CannotConnect
        except aiohttp.ClientError:
            raise CannotConnect

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for i-Vent."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except InvalidLocation:
            errors["base"] = "invalid_location"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

class InvalidLocation(HomeAssistantError):
    """Error to indicate invalid location."""