from anova_wifi import AnovaPrecisionCookerSensor, AnovaPrecisionCookerBinarySensor
from homeassistant import config_entries
from .coordinator import AnovaCoordinator
from .entity import AnovaEntity
from homeassistant.components.climate import (
    ClimateEntity,
)
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import (
    TEMP_CELSIUS,
    ATTR_TEMPERATURE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.util.temperature import convert as convert_temperature


from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: entity_platform.AddEntitiesCallback,
) -> None:
    """Set up Anova device."""
    coordinators = hass.data[DOMAIN][entry.entry_id]
    for coordinator in coordinators.values():
        await coordinator.async_config_entry_first_refresh()
        climate = [AnovaSousVideClimateDevice(coordinator)]
        async_add_entities(climate)


class AnovaSousVideClimateDevice(AnovaEntity, ClimateEntity):
    def __init__(self, coordinator: AnovaCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._device_unique_id}_climate".lower()

    @property
    def current_temperature(self) -> float | None:
        return self.coordinator.data["sensors"][
            AnovaPrecisionCookerSensor.WATER_TEMPERATURE
        ]

    @property
    def target_temperature(self) -> float | None:
        return self.coordinator.data["sensors"][
            AnovaPrecisionCookerSensor.TARGET_TEMPERATURE
        ]

    @property
    def temperature_unit(self) -> str:
        return UnitOfTemperature.CELSIUS

    @property
    def hvac_modes(self) -> list[HVACMode]:
        return [HVACMode.OFF, HVACMode.HEAT]

    @property
    def hvac_mode(self) -> HVACMode:
        return (
            HVACMode.HEAT
            if self.coordinator.data["binary_sensors"][
                AnovaPrecisionCookerBinarySensor.COOKING
            ]
            or self.coordinator.data["binary_sensors"][
                AnovaPrecisionCookerBinarySensor.PREHEATING
            ]
            or self.coordinator.data["binary_sensors"][
                AnovaPrecisionCookerBinarySensor.MAINTAINING
            ]
            else HVACMode.OFF
        )

    @property
    def hvac_action(self) -> HVACAction | None:
        if self.coordinator.data["binary_sensors"][
            AnovaPrecisionCookerBinarySensor.PREHEATING
        ]:
            return HVACAction.HEATING
        elif self.coordinator.data["binary_sensors"][
            AnovaPrecisionCookerBinarySensor.COOKING
        ]:
            return HVACAction.HEATING
        elif self.coordinator.data["binary_sensors"][
            AnovaPrecisionCookerBinarySensor.MAINTAINING
        ]:
            return HVACAction.IDLE
        else:
            return HVACAction.OFF

    @property
    def supported_features(self) -> ClimateEntityFeature:
        return ClimateEntityFeature.TARGET_TEMPERATURE

    @property
    def min_temp(self) -> float:
        return convert_temperature(0, TEMP_CELSIUS, self.temperature_unit)

    @property
    def max_temp(self) -> float:
        return convert_temperature(100, TEMP_CELSIUS, self.temperature_unit)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if HVACMode.OFF == hvac_mode:
            await self.device.set_mode("IDLE")
        elif HVACMode.HEAT == hvac_mode:
            await self.device.set_mode("COOK")
        else:
            raise NotImplementedError

        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs) -> None:
        await self.device.set_target_temperature(kwargs.get(ATTR_TEMPERATURE))
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        await self.device.set_mode("COOK")

    async def async_turn_off(self) -> None:
        await self.device.set_mode("IDLE")
