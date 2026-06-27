from spark_sensors.dataset_definition import SensorReading

import pathlib

class BatteryCollector:
    def _read_text(self, path: pathlib.Path) -> str | None:
        try:
            return path.read_text().strip()
        except OSError:
            return None
        
    def _read_number(self, path: pathlib.Path, divider: float = 1) -> float | None:
        try:
            return float(path.read_text().strip()) / divider
        except (OSError, ValueError):
            return None
    
    def _read_int(self, path: pathlib.Path) -> int | None:
        try:
            return int(path.read_text().strip())
        except (OSError, ValueError):
            return None

    def dynamic_collect(self) -> list[SensorReading]:
        readings = []

        root = pathlib.Path("/sys/class/power_supply")

        if not root.is_dir():
            return []

        for battery in root.iterdir():
            if self._read_text(battery / "type") != "Battery":
                continue

            uid = battery.name.lower()
            display_name = battery.name

            cycles = self._read_int(battery / "cycle_count")
            energy_now = self._read_number(battery / "energy_now", 1000000)
            charge_now = self._read_number(battery / "charge_now", 1000000)
            power_now = self._read_number(battery / "power_now", 1000000)
            current_now = self._read_number(battery / "current_now", 1000000)
            voltage_now = self._read_number(battery / "voltage_now", 1000000)
            status = self._read_text(battery / "status")
            capacity = self._read_int(battery / "capacity")

            if cycles is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_cycles",
                        name=f"{display_name} Cycles",
                        value=cycles,
                        unit="cycles",
                        category="battery",
                        source="power_supply"
                    )
                )
            if energy_now is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_energy_now",
                        name=f"{display_name} Energy Now",
                        value=energy_now,
                        unit="Wh",
                        category="battery",
                        source="power_supply"
                    )
                )
            if charge_now is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_charge_now",
                        name=f"{display_name} Charge Now",
                        value=charge_now,
                        unit="Ah",
                        category="battery",
                        source="power_supply"
                    )
                )
            if power_now is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_power_now",
                        name=f"{display_name} Power Now",
                        value=power_now,
                        unit="W",
                        category="battery",
                        source="power_supply"
                    )
                )
            if current_now is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_current_now",
                        name=f"{display_name} Current Now",
                        value=current_now,
                        unit="A",
                        category="battery",
                        source="power_supply"
                    )
                )
            if voltage_now is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_voltage_now",
                        name=f"{display_name} Voltage Now",
                        value=voltage_now,
                        unit="V",
                        category="battery",
                        source="power_supply"
                    )
                )
            if status is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_status",
                        name=f"{display_name} Status",
                        value=status,
                        unit="",
                        category="battery",
                        source="power_supply"
                    )
                )
            if capacity is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_capacity",
                        name=f"{display_name} Capacity",
                        value=capacity,
                        unit="%",
                        category="battery",
                        source="power_supply"
                    )
                )

        return readings


    def static_collect(self) -> list[SensorReading]:
        readings = []

        root = pathlib.Path("/sys/class/power_supply")

        if not root.is_dir():
            return []

        for battery in root.iterdir():
            if self._read_text(battery / "type") != "Battery":
                continue

            uid = battery.name.lower()
            display_name = battery.name

            model_name = self._read_text(battery / "model_name")
            manufacturer = self._read_text(battery / "manufacturer")
            energy_full = self._read_number(battery / "energy_full", 1000000)
            energy_full_design = self._read_number(battery / "energy_full_design", 1000000)
            charge_full = self._read_number(battery / "charge_full", 1000000)
            charge_full_design = self._read_number(battery / "charge_full_design", 1000000)
            technology = self._read_text(battery / "technology")
            serial_number = self._read_text(battery / "serial_number")
            voltage_min_design = self._read_number(battery / "voltage_min_design", 1000000)

            health = None

            if energy_full is not None and energy_full_design not in (None, 0):
                health = round(energy_full / energy_full_design * 100, 1)
            elif charge_full is not None and charge_full_design not in (None, 0):
                health = round(charge_full / charge_full_design * 100, 1)

            if model_name is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_model_name",
                        name=f"{display_name} Model Name",
                        value=model_name,
                        unit="",
                        category="battery",
                        source="power_supply"
                    )
                )
            if manufacturer is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_manufacturer",
                        name=f"{display_name} Manufacturer",
                        value=manufacturer,
                        unit="",
                        category="battery",
                        source="power_supply"
                    )
                )
            if energy_full is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_energy_full",
                        name=f"{display_name} Energy Full",
                        value=energy_full,
                        unit="Wh",
                        category="battery",
                        source="power_supply"
                    )
                )
            if energy_full_design is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_energy_full_design",
                        name=f"{display_name} Energy Full Design",
                        value=energy_full_design,
                        unit="Wh",
                        category="battery",
                        source="power_supply"
                    )
                )
            if charge_full is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_charge_full",
                        name=f"{display_name} Charge Full",
                        value=charge_full,
                        unit="Ah",
                        category="battery",
                        source="power_supply"
                    )
                )
            if charge_full_design is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_charge_full_design",
                        name=f"{display_name} Charge Full Design",
                        value=charge_full_design,
                        unit="Ah",
                        category="battery",
                        source="power_supply"
                    )
                )
            if health is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_health",
                        name=f"{display_name} Health",
                        value=health,
                        unit="%",
                        category="battery",
                        source="power_supply"
                    )
                )
            if technology is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_technology",
                        name=f"{display_name} Technology",
                        value=technology,
                        unit="",
                        category="battery",
                        source="power_supply"
                    )
                )
            if serial_number is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_serial_number",
                        name=f"{display_name} Serial Number",
                        value=serial_number,
                        unit="",
                        category="battery",
                        source="power_supply"
                    )
                )
            if voltage_min_design is not None:
                readings.append(
                    SensorReading(
                        id=f"battery_{uid}_voltage_min_design",
                        name=f"{display_name} Voltage Min Design",
                        value=voltage_min_design,
                        unit="V",
                        category="battery",
                        source="power_supply"
                    )
                )

        return readings