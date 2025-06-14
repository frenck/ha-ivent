"""The i-Vent integration."""
import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_LOCATION_ID,
    SERVICE_SET_WORK_MODE,
    SERVICE_SET_SPECIAL_MODE,
    SERVICE_SET_SPEED,
    WORK_MODES,
    SPECIAL_MODES,
)
from .coordinator import IVentDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SWITCH,
    Platform.SENSOR,
    Platform.SELECT,
    Platform.NUMBER,
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up i-Vent from a config entry."""
    api_key = entry.data[CONF_API_KEY]
    location_id = entry.data[CONF_LOCATION_ID]

    coordinator = IVentDataUpdateCoordinator(hass, api_key, location_id)

    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_set_work_mode(call: ServiceCall) -> None:
        """Handle the set work mode service call."""
        group_id = call.data.get("group_id")
        work_mode = call.data.get("work_mode")
        speed = call.data.get("speed", 2)
        
        remote_work_mode = {
            "work_mode": work_mode,
            "special_mode": "IVentSpecialOff",
            "remote_control_work_mode": "Normal",
            "remote_control_speed": speed,
            "bypass_rotation": "BypassForward"
        }
        
        await coordinator.async_modify_group(group_id, remote_work_mode)
        await coordinator.async_request_refresh()

    async def handle_set_special_mode(call: ServiceCall) -> None:
        """Handle the set special mode service call."""
        group_id = call.data.get("group_id")
        special_mode = call.data.get("special_mode")
        speed = call.data.get("speed", 2)
        
        remote_work_mode = {
            "work_mode": "IVentOn",
            "special_mode": special_mode,
            "remote_control_work_mode": "Normal", 
            "remote_control_speed": speed,
            "bypass_rotation": "BypassForward"
        }
        
        await coordinator.async_modify_group(group_id, remote_work_mode)
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, SERVICE_SET_WORK_MODE, handle_set_work_mode)
    hass.services.async_register(DOMAIN, SERVICE_SET_SPECIAL_MODE, handle_set_special_mode)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: IVentDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.async_shutdown()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok