def decode_32bit_sensor(code: int):
    if code >= (1 << 32):
        return None

    code = code & 0xFFFFFFFF

    tipo_sensor = (code >> 29) & 0b111
    device_id = (code >> 13) & 0xFFFF
    raw_value = code & 0x1FFF

    sensor_type_map = {
        0: "temperature",
        1: "humidity",
        2: "binary",
        3: "distance",
        4: "power",
        5: "voltage",
        6: "current",
        7: "battery"
    }

    sensor_type = sensor_type_map.get(tipo_sensor, "unknown")

    if sensor_type == "temperature":
        if raw_value & 0x1000:
            raw_value -= 0x2000
        value = raw_value / 100.0

    elif sensor_type in ["voltage", "current", "humidity", "battery"]:
        value = raw_value / 10.0

    elif sensor_type in ["distance", "power"]:
        value = raw_value

    elif sensor_type == "binary":
        value = bool(raw_value & 0b01)
        auto_off = bool((raw_value >> 1) & 0b1)
        return {
            "sensor_type": sensor_type,
            "device_id": device_id,
            "value": value,
            "auto_off": auto_off
        }

    else:
        return None

    return {
        "sensor_type": sensor_type,
        "device_id": device_id,
        "value": value
    }