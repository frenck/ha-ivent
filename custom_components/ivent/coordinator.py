"""DataUpdateCoordinator for i-Vent."""
import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, API_BASE_URL, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class IVentDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching i-Vent data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_key: str,
        location_id: int,
    ) -> None:
        """Initialize."""
        self.api_key = api_key
        self.location_id = location_id
        self.session = aiohttp.ClientSession()

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            async with async_timeout.timeout(10):
                return await self._get_data()
        except asyncio.TimeoutError as exception:
            raise UpdateFailed(f"Timeout communicating with API: {exception}")
        except (aiohttp.ClientError, Exception) as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}")

    async def _get_data(self) -> dict[str, Any]:
        """Get data from the API."""
        url = f"{API_BASE_URL}/live/{self.location_id}/info"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with self.session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"API returned status {response.status}")
            return await response.json()

    async def async_modify_group(self, group_id: int, remote_work_mode: dict) -> bool:
        """Modify a group via the API."""
        url = f"{API_BASE_URL}/live/{self.location_id}/modify_group"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "group_id": group_id,
            "remote_work_mode": remote_work_mode
        }

        try:
            async with async_timeout.timeout(10):
                async with self.session.post(url, headers=headers, json=data) as response:
                    return response.status == 200
        except (asyncio.TimeoutError, aiohttp.ClientError):
            return False

    async def async_shutdown(self) -> None:
        """Close the aiohttp session."""
        await self.session.close()