"""Support for Anova Coordinators."""
import logging
from datetime import timedelta

import async_timeout
from anova_wifi import AnovaOffline
from anova_wifi import AnovaPrecisionCooker
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AnovaCoordinator(DataUpdateCoordinator):
    """Anova custom coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        anova_device: AnovaPrecisionCooker,
    ) -> None:
        """Set up Anova Coordinator."""
        super().__init__(
            hass,
            name="Anova Precision Cooker",
            logger=_LOGGER,
            update_interval=timedelta(seconds=30),
        )
        assert self.config_entry is not None
        self._device_unique_id = anova_device.device_key
        self.anova_device = anova_device
        self.device_info: DeviceInfo | None = None

    @callback
    def async_setup(self, firmware_version: str) -> None:
        """Set the firmware version info."""
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_unique_id)},
            name="Anova Precision Cooker",
            manufacturer="Anova",
            model="Precision Cooker",
            sw_version=firmware_version,
        )

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(5):
                return await self.anova_device.update()
        except AnovaOffline as err:
            raise UpdateFailed(err) from err
