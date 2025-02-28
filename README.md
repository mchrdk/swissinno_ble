# 🐀 SWISSINNO BLE Trap Integration for Home Assistant

A **custom Home Assistant integration** for **SWISSINNO Bluetooth traps**, allowing real-time monitoring of **trap status, battery levels, and signal strength (RSSI).**  

![image](https://github.com/user-attachments/assets/99f7ad4c-0344-4547-89e7-5c4329c465a4)
 

---

## 🚀 Features
✔️ **Automatic BLE scanning** – Detects traps without manual pairing.  
✔️ **Trap Status Monitoring** – See if traps are set or triggered.  
✔️ **Battery Level Sensor** – Displays accurate battery voltage.  
✔️ **Signal Strength (RSSI) Sensor** – Helps position traps for best connectivity.  
✔️ **Custom Lovelace Dashboard** – Displays traps visually with dynamic icons.  

---

## 📥 Installation
### 1️⃣ **Manual Installation**
1. Download the `custom_components/swissinno_ble` folder.
2. Place it inside your Home Assistant `config/custom_components/` directory.
3. Restart Home Assistant.
4. Go to **Settings → Devices & Services** and add "SWISSINNO BLE."

### 2️⃣ **HACS Installation (Coming Soon)**
*(Once HACS support is added, update this section!)*  

---

## ⚙️ Configuration
Once installed, Home Assistant will **automatically detect nearby SWISSINNO traps**.  
You **do not** need to manually configure YAML.  

To customize the **Lovelace UI**, follow the instructions below.  

---

## 📊 Lovelace Dashboard
### **Basic Lovelace Card**
Use this Lovelace configuration to monitor trap status, battery level, and signal strength:  

```yaml
type: entities
title: 🐀 SWISSINNO Traps
show_header_toggle: false
entities:
  - entity: binary_sensor.swissinno_trap_DC140300
    name: Trap Status
    icon: mdi:rodent
    state_color: true

  - type: custom:template-entity-row
    entity: sensor.swissinno_battery_DC140300
    name: Battery Level
    state: "{{ states('sensor.swissinno_battery_DC140300') | round(2) }} V"
    icon: >-
      {% raw %}
      {% set battery = states('sensor.swissinno_battery_DC140300') | float(0) %}
      {% if battery >= 3.0 %} mdi:battery
      {% elif battery >= 2.8 %} mdi:battery-80
      {% elif battery >= 2.6 %} mdi:battery-60
      {% elif battery >= 2.4 %} mdi:battery-40
      {% elif battery >= 2.2 %} mdi:battery-20
      {% else %} mdi:battery-alert
      {% endif %}
      {% endraw %}

  - entity: sensor.swissinno_rssi_DC140300
    name: Signal Strength
    icon: mdi:wifi
```

🔹 **Tip:**  
- Replace `DC140300` with your trap’s actual ID.  
- Install [Template Entity Row](https://github.com/thomasloven/lovelace-template-entity-row) via HACS to enable dynamic battery icons.  

---

## 🔧 Troubleshooting
### ❓ **No devices are found?**
✔️ Ensure your Home Assistant device has **Bluetooth enabled**.  
✔️ Check **Settings → Devices & Services → Bluetooth** to verify BLE is working.  
✔️ **Restart Home Assistant** after installation.  

### ❓ **Battery voltage is incorrect?**
✔️ Ensure you are using the latest version of this integration.  
✔️ The correct formula for battery voltage is:  
  ```
  Voltage = (Raw Value * 3.6) / 255
  ```

### ❓ **Trap status doesn’t update?**
✔️ Move the trap **closer to Home Assistant** for better signal reception.  
✔️ Check **Developer Tools → States** for `binary_sensor.swissinno_trap_<ID>` state.  

---

## 🤝 Contributing
🚀 **Want to improve this integration?** Contributions are welcome!  
- Open an **issue** for bug reports or feature requests.  
- Fork the repository and submit a **pull request**.  

---

## 📜 License
**MIT License** – Free to use and modify.  

📌 **Enjoy automating your SWISSINNO traps in Home Assistant!** 🚀🔥  

---

## 📌 Future Improvements  
✔️ **HACS Support** (planned)  
✔️ **More Lovelace UI options**  
✔️ **Custom SWISSINNO BLE logo**  
✔️ **Optimized Bluetooth scanning**  

---

## 📢 Need Help?
💬 **Open a GitHub issue** or ask in the Home Assistant community!  
