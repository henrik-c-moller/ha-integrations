from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import VOLUME_CUBIC_METERS
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AflasCoordinator
from .sensor_debug import AflasDebugSensor
from .sensor_rolling import AflasRollingUsageSensor
from .utils import parse_aflas_label
from . import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinators = data["coordinators"]

    entities = []

    for meter, coordinator in coordinators.items():
        # Daily usage
        entities.append(AflasWaterUsageSensor(coordinator, meter))

        # Flow
        entities.append(AflasWaterFlowSensor(coordinator, meter))

        # Rolling usage sensors
        entities.append(AflasRollingUsageSensor(coordinator, meter, 24))        # 24h
        entities.append(AflasRollingUsageSensor(coordinator, meter, 24 * 7))    # 7d
        entities.append(AflasRollingUsageSensor(coordinator, meter, 24 * 30))   # 30d

        # Debug
        entities.append(AflasDebugSensor(coordinator, meter))

    async_add_entities(entities, True)

