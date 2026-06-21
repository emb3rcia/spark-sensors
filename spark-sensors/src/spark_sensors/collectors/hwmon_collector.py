from spark_sensors.dataset_definition import SensorReading

import pathlib

class HwmonCollector:
    def dynamic_collect(self) -> list[SensorReading]:
        hwmons = {}
        for hwmon in pathlib.Path("/sys/class/hwmon").iterdir():
            try:
                name = (hwmon / "name").read_text().strip()
            except OSError:
                continue
            for file in hwmon.iterdir():
                parts = file.name.split("_")
                if len(parts) < 2:
                    continue
                if str(hwmon) not in hwmons:
                    hwmons[str(hwmon)] = {
                        "chip": name,
                        "sensors": {}
                    }
                if parts[0] not in hwmons[str(hwmon)]["sensors"]:
                    hwmons[str(hwmon)]["sensors"][parts[0]] = {}

                attribute = file.name.removeprefix(f"{parts[0]}_")
                hwmons[str(hwmon)]["sensors"][parts[0]][attribute] = file
        readings = []
        for hwmon_data in hwmons.values():
                chip = hwmon_data["chip"]
                for sensor_id, sensor_files in hwmon_data["sensors"].items():
                    if "input" not in sensor_files:
                        continue
                    try:
                        raw_value = sensor_files["input"].read_text().strip()
                    except (OSError, ValueError):
                        continue
                    try:
                        raw_value = int(raw_value)
                    except ValueError:
                        continue
                    try:
                        label = sensor_id if "label" not in sensor_files else sensor_files["label"].read_text().strip()
                    except OSError:
                        label = sensor_id
                    sensor_uid = f"{chip}_{sensor_id}_{label.lower().replace(' ', '_')}"
                    if sensor_id.startswith("temp"):
                        readings.append(
                            SensorReading(
                                id=sensor_uid,
                                name=label,
                                value = raw_value / 1000,
                                unit="°C",
                                category="temperature",
                                source="hwmon"
                            )
                        )
                    elif sensor_id.startswith("fan"):
                        readings.append(
                            SensorReading(
                                id=sensor_uid,
                                name=label,
                                value = raw_value,
                                unit="RPM",
                                category="fan",
                                source="hwmon"
                            )
                        )
                    elif sensor_id.startswith("in"):
                        readings.append(
                            SensorReading(
                                id=sensor_uid,
                                name=label,
                                value = raw_value / 1000,
                                unit="V",
                                category="voltage",
                                source="hwmon"
                            )
                        )
                    elif sensor_id.startswith("curr"):
                        readings.append(
                            SensorReading(
                                id=sensor_uid,
                                name=label,
                                value = raw_value / 1000,
                                unit="A",
                                category="current",
                                source="hwmon"
                            )
                        )
                    elif sensor_id.startswith("power"):
                        readings.append(
                            SensorReading(
                                id=sensor_uid,
                                name=label,
                                value = raw_value / 1_000_000,
                                unit="W",
                                category="power",
                                source="hwmon"
                            )
                        )

        return readings