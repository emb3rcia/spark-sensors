from spark_sensors.collectors.psutil_collector import PsutilCollector
from spark_sensors.collectors.hwmon_collector import HwmonCollector
from spark_sensors.dataset_definition import SensorReading

class CollectorManager:
    def __init__(self):
        self.collectors = [
            PsutilCollector(),
            HwmonCollector()
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
                #TODO/MEDIUM/Add exception handling/23.06.2026

        return readings
    
    def static_collect(self) -> list[SensorReading]:
        readings = []

        for collector in self.collectors:
            if hasattr(collector, "static_collect"):
                readings.extend(
                    collector.static_collect()
                )
        
        return readings