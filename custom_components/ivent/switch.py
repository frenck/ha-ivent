"""Switch platform for i-Vent."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import IVentDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the i-Vent switch platform."""
    coordinator: IVentDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    
    if coordinator.data and "groups" in coordinator.data:
        for group in coordinator.data["groups"]:
            entities.append(IVentGroupSwitch(coordinator, group["id"], group["name"]))
    
    async_add_entities(entities)

class IVentGroupSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of an i-Vent group switch."""

    def __init__(self, coordinator: IVentDataUpdateCoordinator, group_id: int, group_name: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.group_id = group_id
        self._attr_name = f"{group_name} i-Vent"
        self._attr_unique_id = f"{coordinator.location_id}_group_{group_id}"

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        if self.coordinator.data and "groups" in self.coordinator.data:
            for group in self.coordinator.data["groups"]:
                if group["id"] == self.group_id:
                    return group["remote"]["work_mode"] != "IVentWorkOff"
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        remote_work_mode = {
            "work_mode": "IVentOn",
            "special_mode": "IVentSpecialOff",
            "remote_control_work_mode": "Normal",
            "remote_control_speed": 2,
            "bypass_rotation": "BypassForward"
        }
        
        await self.coordinator.async_modify_group(self.group_id, remote_work_mode)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        remote_work_mode = {
            "work_mode": "IVentWorkOff",
            "special_mode": "IVentSpecialOff", 
            "remote_control_work_mode": "Normal",
            "remote_control_speed": 1,
            "bypass_rotation": "BypassForward"
        }
        
        await self.coordinator.async_modify_group(self.group_id, remote_work_mode)
        await self.coordinator.async_request_refresh()