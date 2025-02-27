import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS_MILLIWATT
from homeassistant.helpers.entity import DeviceInfo
from datetime import datetime, timedelta
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

LAST_SEEN_TIMEOUT = timedelta(minutes=10)  # Make sensor unavailable if unseen for 10 minutes

class SwissinnoRssiSensor(SensorEntity):
    """Representation of a SWISSINNO RSSI Sensor."""

    def __init__(self, address, trap_id, rssi):
        _LOGGER.info(f"SWISSINNO BLE: Creating RSSI sensor for trap {trap_id}")
        self._attr_name = f"SWISSINNO Trap RSSI {trap_id}"
        self._attr_unique_id = f"swissinno_rssi_{trap_id}"
        self._attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
        self._attr_state_class = "measurement"
        self._attr_device_class = "signal_strength"
        self._rssi = rssi
        self._last_seen = datetime.utcnow()
        self._attr_should_poll = False  # No polling needed for BLE
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, address)},
            name=f"SWISSINNO Trap {trap_id}",
            manufacturer="SWISSINNO",
            model="BLE Trap Sensor"
        )

    async def async_added_to_hass(self):
        """Ensure the entity is properly registered in Home Assistant."""
        _LOGGER.info(f"SWISSINNO BLE: Successfully added RSSI sensor {self._attr_unique_id} to HA.")

    @property
    def native_value(self):
        """Return the RSSI value."""
        return self._rssi

    @property
    def available(self):
        """Make the sensor unavailable if not detected for a certain time."""
        return datetime.utcnow() - self._last_seen < LAST_SEEN_TIMEOUT

    def update_state(self, rssi):
        """Update RSSI value and refresh last seen timestamp."""
        _LOGGER.info(f"SWISSINNO BLE: Updating RSSI for {self._attr_unique_id} - RSSI: {rssi}")
        self._rssi = rssi
        self._last_seen = datetime.utcnow()
        self.async_write_ha_state()
