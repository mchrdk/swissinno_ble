import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS_MILLIWATT, UnitOfElectricPotential
from homeassistant.helpers.entity import DeviceInfo
from datetime import datetime, timedelta
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

LAST_SEEN_TIMEOUT = timedelta(minutes=10)  # Sensor unavailable if unseen for 10 minutes
sensors = {}  # Store sensor instances globally

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up SWISSINNO BLE sensors (RSSI & Battery Voltage)."""
    _LOGGER.info("SWISSINNO BLE: Setting up RSSI and Battery sensors.")

    if DOMAIN not in hass.data:
        _LOGGER.warning(f"SWISSINNO BLE: {DOMAIN} not found in hass.data, initializing now.")
        hass.data[DOMAIN] = {}

    async def add_or_update_sensors(trap_id, address, rssi, battery_v):
        """Function to create or update RSSI and Battery sensors."""
        _LOGGER.info(f"SWISSINNO BLE: Updating sensors for {trap_id} - RSSI: {rssi} dBm, Battery: {battery_v} V")

        if trap_id in sensors:
            _LOGGER.info(f"SWISSINNO BLE: Updating existing sensors for {trap_id}")
            sensors[trap_id]["rssi"].update_rssi(rssi)
            sensors[trap_id]["battery"].update_battery(battery_v)
        else:
            _LOGGER.info(f"SWISSINNO BLE: Creating new sensors for {trap_id}")
            rssi_sensor = SwissinnoRssiSensor(address, trap_id, rssi)
            battery_sensor = SwissinnoBatterySensor(address, trap_id, battery_v)

            sensors[trap_id] = {"rssi": rssi_sensor, "battery": battery_sensor}
            hass.async_create_task(async_add_entities([rssi_sensor, battery_sensor], update_before_add=True))

    hass.data[DOMAIN]["update_sensors"] = add_or_update_sensors
    _LOGGER.info("SWISSINNO BLE: `update_sensors` function registered successfully.")

class SwissinnoRssiSensor(SensorEntity):
    """Representation of a SWISSINNO RSSI Sensor."""

    def __init__(self, address, trap_id, rssi):
        self._attr_name = f"SWISSINNO Trap RSSI {trap_id}"
        self._attr_unique_id = f"swissinno_rssi_{trap_id}"
        self._attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
        self._attr_state_class = "measurement"
        self._attr_device_class = "signal_strength"
        self._rssi = round(rssi, 2)  # ✅ Round to 2 decimals
        self._last_seen = datetime.utcnow()
        self._attr_should_poll = False
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, address)},
            name=f"SWISSINNO Trap {trap_id}",
            manufacturer="SWISSINNO",
            model="BLE Trap Sensor"
        )

    @property
    def native_value(self):
        """Return the RSSI value."""
        return self._rssi

    def update_rssi(self, rssi):
        """Update RSSI value (rounded to 2 decimals)."""
        self._rssi = round(rssi, 2)
        self.async_write_ha_state()

class SwissinnoBatterySensor(SensorEntity):
    """Representation of a SWISSINNO Battery Voltage Sensor."""

    def __init__(self, address, trap_id, battery_v):
        self._attr_name = f"SWISSINNO Trap Battery {trap_id}"
        self._attr_unique_id = f"swissinno_battery_{trap_id}"
        self._attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
        self._attr_state_class = "measurement"
        self._attr_device_class = "voltage"
        self._battery_v = round(battery_v, 2)  # ✅ Round to 2 decimals
        self._last_seen = datetime.utcnow()
        self._attr_should_poll = False
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, address)},
            name=f"SWISSINNO Trap {trap_id}",
            manufacturer="SWISSINNO",
            model="BLE Trap Sensor"
        )

    @property
    def native_value(self):
        """Return the battery voltage."""
        return self._battery_v

    def update_battery(self, battery_v):
        """Update battery voltage (rounded to 2 decimals)."""
        self._battery_v = round(battery_v, 2)
        self.async_write_ha_state()
