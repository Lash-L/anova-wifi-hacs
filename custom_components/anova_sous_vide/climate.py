# """Climate entities for Anova."""
# from typing import Any
# from anova_wifi import AnovaPrecisionCookerBinarySensor, AnovaPrecisionCookerSensor
# from homeassistant import config_entries
# from homeassistant.components.climate import (
#     ClimateEntity,
#     ClimateEntityFeature,
#     HVACAction,
#     HVACMode,
# )
# from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
# from homeassistant.core import HomeAssistant
# from homeassistant.helpers import entity_platform
# from .const import DOMAIN
# from .coordinator import AnovaCoordinator
# from .entity import AnovaEntity
# from .models import AnovaData
# async def async_setup_entry(
#     hass: HomeAssistant,
#     entry: config_entries.ConfigEntry,
#     async_add_entities: entity_platform.AddEntitiesCallback,
# ) -> None:
#     """Set up Anova device."""
#     anova_data: AnovaData = hass.data[DOMAIN][entry.entry_id]
#     async_add_entities(
#         AnovaSousVideClimateDevice(coordinator)
#         for coordinator in anova_data.coordinators
#     )
# class AnovaSousVideClimateDevice(AnovaEntity, ClimateEntity):
#     """Controls setting the temperature of a Anoav sous vide."""
#     # Important to note - while the device supports displaying both celsius and farenheit, it always responds to the api in celsius
#     _attr_temperature_unit = UnitOfTemperature.CELSIUS
#     _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
#     _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
#     _attr_min_temp = 0.0  # celsius
#     _attr_max_temp = 63.33  # celsius
#     def __init__(self, coordinator: AnovaCoordinator) -> None:
#         """Set up sous vide climate entity."""
#         super().__init__(coordinator)
#         self._attr_unique_id = f"{coordinator._device_unique_id}_climate"
#     @property
#     def current_temperature(self) -> float | None:
#         """Get current temperature of the water in the sous vide."""
#         return float(
#             self.coordinator.data["sensors"][
#                 AnovaPrecisionCookerSensor.WATER_TEMPERATURE
#             ]
#         )
#     @property
#     def target_temperature(self) -> float | None:
#         """Get current target temperature of the sous vide."""
#         return float(
#             self.coordinator.data["sensors"][
#                 AnovaPrecisionCookerSensor.TARGET_TEMPERATURE
#             ]
#         )
#     @property
#     def hvac_mode(self) -> HVACMode:
#         """Get the current hvac mode of the sous vide."""
#         return (
#             HVACMode.HEAT
#             if self.coordinator.data["binary_sensors"][
#                 AnovaPrecisionCookerBinarySensor.COOKING
#             ]
#             or self.coordinator.data["binary_sensors"][
#                 AnovaPrecisionCookerBinarySensor.PREHEATING
#             ]
#             or self.coordinator.data["binary_sensors"][
#                 AnovaPrecisionCookerBinarySensor.MAINTAINING
#             ]
#             else HVACMode.OFF
#         )
#     @property
#     def hvac_action(self) -> HVACAction | None:
#         """Get the current heating action of the sous vide."""
#         if self.coordinator.data["binary_sensors"][
#             AnovaPrecisionCookerBinarySensor.PREHEATING
#         ]:
#             return HVACAction.HEATING
#         if self.coordinator.data["binary_sensors"][
#             AnovaPrecisionCookerBinarySensor.COOKING
#         ]:
#             return HVACAction.HEATING
#         if self.coordinator.data["binary_sensors"][
#             AnovaPrecisionCookerBinarySensor.MAINTAINING
#         ]:
#             return HVACAction.IDLE
#         return HVACAction.OFF
#     async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
#         """Set the hvac mode of the sous vide."""
#         if hvac_mode == HVACMode.OFF:
#             await self.device.set_mode("IDLE")
#         elif hvac_mode == HVACMode.HEAT:
#             await self.device.set_mode("COOK")
#         else:
#             raise NotImplementedError
#     async def async_set_temperature(self, **kwargs: Any) -> None:
#         """Set the target temperature of the sous vide."""
#         await self.device.set_target_temperature(kwargs[ATTR_TEMPERATURE])
#     async def async_turn_on(self) -> None:
#         """Start a sous vide cook."""
#         await self.device.set_mode("COOK")
#     async def async_turn_off(self) -> None:
#         """Stop a sous vide cook."""
#         await self.device.set_mode("IDLE")
