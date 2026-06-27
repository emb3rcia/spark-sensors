from spark_sensors.collectors.psutil_collector import PsutilCollector
from spark_sensors.collectors.hwmon_collector import HwmonCollector
from spark_sensors.collectors.nvidia_collector import NvidiaCollector
from spark_sensors.collectors.battery_collector import BatteryCollector
from spark_sensors.collectors.intel_collector import IntelCollector
from spark_sensors.dataset_definition import SensorReading

class CollectorManager:
    def __init__(self):
        self.collectors = [
            PsutilCollector(),
            HwmonCollector(),
            NvidiaCollector(),
            BatteryCollector(),
            IntelCollector()
        ]
    
    def dynamic_collect(self) -> list[SensorReading]:
        readings = []

        for collector in self.collectors:
            try:
                readings.extend(
                    collector.dynamic_collect()
                )
            except Exception as e:
                continue
                #TODO/MEDIUM/Add exception handling/27.06.2026

        return readings
    
    def static_collect(self) -> list[SensorReading]:
        readings = []

        for collector in self.collectors:
            if hasattr(collector, "static_collect"):
                readings.extend(
                    collector.static_collect()
                )
        
        return readings