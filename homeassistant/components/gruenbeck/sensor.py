"""Support for the SoftQLink sensor service."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SoftQLinkDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 1


@dataclass(frozen=True)
class SoftQLinkSensorEntityDescription(SensorEntityDescription):
    """Class describing SoftQLink sensor entities."""

    attrs: Callable[[dict[str, Any]], dict[str, Any]] = lambda data: {}


SENSOR_TYPES: tuple[SoftQLinkSensorEntityDescription, ...] = (
    SoftQLinkSensorEntityDescription(key="D_A_1_1"),
    SoftQLinkSensorEntityDescription(key="D_A_1_2"),
    SoftQLinkSensorEntityDescription(key="D_A_2_2"),
    SoftQLinkSensorEntityDescription(key="D_A_2_3"),
    SoftQLinkSensorEntityDescription(key="D_A_3_1"),
    SoftQLinkSensorEntityDescription(key="D_A_3_2"),
    SoftQLinkSensorEntityDescription(key="D_A_1_7"),
    SoftQLinkSensorEntityDescription(key="D_Y_5"),
    SoftQLinkSensorEntityDescription(key="D_A_2_1"),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SoftQLink sensor entities based on a config entry."""

    coordinator = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.info(coordinator.data)
    sensors = []
    for description in SENSOR_TYPES:
        # When we use the nearest method, we are not sure which sensors are available
        _LOGGER.info(description.key)
        sensors.append(SoftQLinkSensor(coordinator, description))

    async_add_entities(sensors, False)


class SoftQLinkSensor(CoordinatorEntity[SoftQLinkDataUpdateCoordinator], SensorEntity):
    """Define an Airly sensor."""

    _attr_attribution = "Data from SoftQLink"
    _attr_has_entity_name = True
    entity_description: SoftQLinkSensorEntityDescription

    def __init__(
        self,
        coordinator: SoftQLinkDataUpdateCoordinator,
        description: SoftQLinkSensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{description.key}")},
            manufacturer="Gruenbeck",
            name=description.key,
        )
        self._attr_unique_id = f"{coordinator.name}-{description.key}".lower()
        self._attr_native_value = coordinator.data.get(description.key)
        self._attr_extra_state_attributes = description.attrs(coordinator.data)
        self.entity_description = description

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data.get(self.entity_description.key)
        self._attr_extra_state_attributes = self.entity_description.attrs(
            self.coordinator.data
        )
        self.async_write_ha_state()
