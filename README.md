# Rebuli RF Bridge

**Rebuli RF Bridge** is a custom integration for Home Assistant that decodes and exposes RF 433 MHz signals as entities, using structured 32-bit messages over MQTT.

This bridge allows you to create real, auto-discovered Home Assistant entities — like sensors and binary sensors — from raw RF data, with support for filtering allowed devices and custom auto-off logic.

---

## 📡 Features

- Automatic decoding of 32-bit RF codes via MQTT
- Support for 8 sensor types:
  - Temperature
  - Humidity
  - Distance
  - Power (W)
  - Voltage (V)
  - Current (A)
  - Battery Level (%)
  - Binary (e.g. buttons or contact sensors)
- Auto-off feature for binary sensors (e.g. momentary buttons)
- Devices grouped by unique device ID
- UI-based configuration (no YAML required)
- Entity auto-discovery and dynamic creation

---

## 🧰 Installation (Manual)

1. Download or clone this repository.
2. Copy the `custom_components/rebuli_rf_bridge` folder into your Home Assistant `config/custom_components/` directory.
3. Restart Home Assistant.
4. Go to **Settings > Devices & Services > Integrations**, click **Add Integration**, and search for **Rebuli RF Bridge**.
5. Configure the MQTT topic, auto-off timeout, and allowed device IDs.

---

## 🔧 Configuration Options

These options are configurable in the Home Assistant UI:

| Option              | Description                                               | Default                        |
|---------------------|-----------------------------------------------------------|--------------------------------|
| **MQTT Topic**      | MQTT topic to listen to incoming RF codes                 | `home/rebuli_rf/received`      |
| **Auto-Off Timeout**| Seconds to turn off binary sensors automatically          | `2` seconds                    |
| **Allowed IDs**     | List of allowed 16-bit device IDs (e.g., `0009, A1B2`)    | *(empty = accept all)*         |

---

## 🔢 Message Format

RF codes are sent as 32-bit integers via MQTT, e.g.:
```json
{ "code": 12345678 }
```

The code format is:
```css
[3 bits: type][16 bits: device ID][13 bits: raw data]
```

Each sensor type is identified by a 3-bit prefix:


| Type ID | Sensor Type   | Notes                                    |
| ------- | ------------- | ---------------------------------------- |
| `000`   | Temperature   | Signed int × 100 → `-40.96°C to 40.95°C` |
| `001`   | Humidity      | Unsigned int × 10 → `0.0% to 819.1%`     |
| `010`   | Binary        | Bit 0 = state, Bit 1 = auto-off flag     |
| `011`   | Distance      | Unsigned int (cm) → `0 to 8191`          |
| `100`   | Power         | Unsigned int (W) → `0 to 8191`           |
| `101`   | Voltage       | Unsigned int × 10 → `0.0V to 819.1V`     |
| `110`   | Current       | Unsigned int × 10 → `0.0A to 819.1A`     |
| `111`   | Battery Level | Unsigned int × 10 → `0.0% to 819.1%`     |

---

## Device Filtering
You can limit which RF devices are accepted by specifying their 16-bit ID in the Allowed IDs field in the integration settings.

Any message from an unknown device will be ignored and logged.

---

## 🚨 Example MQTT Payloads
```json
{ "code": 93994128 }  // Device 0x0009 - Temperature: 23.56°C
{ "code": 111411712 } // Device 0x0009 - Binary ON with auto-off
---

## 👤 Author
Developed by Rebuli Home Automation
Open for contributions and ideas!

## 📄 License
This project is licensed under the MIT License.
