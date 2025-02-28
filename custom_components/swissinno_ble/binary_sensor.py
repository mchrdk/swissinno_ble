import asyncio
import logging
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_register_callback,
    BluetoothScanningMode,
)
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from datetime import datetime, timedelta
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

MANUFACTURER_ID = 0x0BBB  # SWISSINNO Manufacturer ID
LAST_SEEN_TIMEOUT = timedelta(minutes=10)  # Make trap unavailable if unseen for 10 minutes

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up SWISSINNO BLE binary sensors using HA’s Bluetooth API."""
    
    _LOGGER.info("SWISSINNO BLE: Registering Bluetooth scanner callback...")
    sensors = {}

    @callback
    def detection_callback(service_info: BluetoothServiceInfoBleak, change):
        """Callback for BLE advertisement detection via Home Assistant."""
        _LOGGER.debug(f"SWISSINNO BLE: Found BLE device: {service_info.name} - Address: {service_info.address}")

        manufacturer_data = service_info.manufacturer_data
        if MANUFACTURER_ID in manufacturer_data:
            data = manufacturer_data[MANUFACTURER_ID]
            rssi = service_info.rssi

            if len(data) >= 9:
                trap_id = f"{data[2]:02X}{data[3]:02X}{data[4]:02X}{data[5]:02X}"
                tripped = data[0] == 0x01

                # ✅ Extract battery voltage from byte 8 (after manufacturer ID)
                battery_raw = data[7]  
                battery_v = round((battery_raw * 3.6) / 255, 2)  # Correct voltage conversion

                _LOGGER.info(f"SWISSINNO BLE: Updating trap {trap_id}, Tripped: {tripped}, RSSI: {rssi} dBm, Battery: {battery_v} V")

                if trap_id in sensors:
                    sensors[trap_id].update_state(tripped)
                else:
                    _LOGGER.info(f"SWISSINNO BLE: Creating new binary sensor for {trap_id}")
                    trap_sensor = SwissinnoTrapSensor(service_info.address, trap_id, tripped)
                    sensors[trap_id] = trap_sensor
                    async_add_entities([trap_sensor], update_before_add=True)

                if "update_sensors" in hass.data.get(DOMAIN, {}):
                    hass.async_create_task(hass.data[DOMAIN]["update_sensors"](trap_id, service_info.address, rssi, battery_v))
                else:
                    _LOGGER.warning(f"SWISSINNO BLE: `update_sensors` not found, retrying in 5 seconds.")

                    async def retry_update():
                        await asyncio.sleep(5)
                        if "update_sensors" in hass.data.get(DOMAIN, {}):
                            _LOGGER.info(f"SWISSINNO BLE: Retrying sensor updates for {trap_id}")
                            hass.async_create_task(hass.data[DOMAIN]["update_sensors"](trap_id, service_info.address, rssi, battery_v))
                        else:
                            _LOGGER.error(f"SWISSINNO BLE: `update_sensors` still missing after retry.")

                    hass.async_create_task(retry_update())

    cancel_callback = async_register_callback(hass, detection_callback, {}, BluetoothScanningMode.PASSIVE)
    hass.bus.async_listen_once("homeassistant_stop", cancel_callback)

    _LOGGER.info("SWISSINNO BLE: Bluetooth scanner callback registered successfully!")

class SwissinnoTrapSensor(BinarySensorEntity):
    """Representation of a SWISSINNO Trap."""

    def __init__(self, address, trap_id, is_tripped):
        _LOGGER.info(f"SWISSINNO BLE: Creating sensor for trap {trap_id}")
        self._attr_name = f"SWISSINNO Trap {trap_id}"
        self._attr_unique_id = f"swissinno_trap_{trap_id}"
        self._attr_device_class = "motion"
        self._attr_icon = "mdi:rodent"  # ✅ Updated to use `mdi:rodent`
        self._state = is_tripped
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
        _LOGGER.info(f"SWISSINNO BLE: Successfully added sensor {self._attr_unique_id} to HA.")

    @property
    def is_on(self):
        """Return the state of the trap."""
        return self._state

    @property
    def available(self):
        """Make the trap unavailable if not detected for a certain time."""
        return datetime.utcnow() - self._last_seen < LAST_SEEN_TIMEOUT

    def update_state(self, is_tripped):
        """Update trap state and refresh last seen timestamp."""
        _LOGGER.info(f"SWISSINNO BLE: Updating state for {self._attr_unique_id} - Tripped: {is_tripped}")
        self._state = is_tripped
        self._last_seen = datetime.utcnow()
        self.async_write_ha_state()  # Forces HA to update the entity state
