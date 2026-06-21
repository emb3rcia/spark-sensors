import psutil
import time
from spark_sensors.dataset_definition import SensorReading

class PsutilCollector:
    def __init__(self):
        psutil.cpu_percent(interval=0)
        self.previous_net = None
        self.previous_time = None


    def dynamic_collect(self) -> list[SensorReading]:
        readings = []
        current_net = psutil.net_io_counters()
        current_time = time.monotonic()
        
        if self.previous_net is None or self.previous_time is None:
                rx_rate = 0
                tx_rate = 0
        else:
            elapsed = max(
                current_time - self.previous_time,
                0.001,
            )

            rx_rate = (
                current_net.bytes_recv - self.previous_net.bytes_recv
            ) / elapsed

            tx_rate = (
                current_net.bytes_sent - self.previous_net.bytes_sent
            ) / elapsed

        self.previous_net = current_net
        self.previous_time = current_time

        readings.append(
            SensorReading(
                id="cpu_percent",
                name="CPU Usage",
                value=psutil.cpu_percent(interval=0),
                unit="%",
                category="cpu",
                source="psutil"
            )
        )

        readings.append(
            SensorReading(
                id="cpu_freq",
                name="CPU Frequency",
                value=psutil.cpu_freq(percpu=False).current,
                unit="MHz",
                category="cpu",
                source="psutil"
            )
        )

        cpu_freqency_percore = psutil.cpu_freq(percpu=True)

        for i, core in enumerate(cpu_freqency_percore):
            readings.append(
                SensorReading(
                    id=f"core{str(i)}_freq",
                    name=f"Core {str(i)} Frequency",
                    value=core.current,
                    unit="MHz",
                    category="cpu",
                    source="psutil"
                )
            )

        mem = psutil.virtual_memory()

        readings.append(
            SensorReading(
                id="memory_used",
                name="RAM Used",
                value=mem.used / (1024 ** 3),
                unit="GiB",
                category="memory",
                source="psutil"
            )
        )

        readings.append(
            SensorReading(
                id="memory_available",
                name="RAM Available",
                value=mem.available / (1024 ** 3),
                unit="GiB",
                category="memory",
                source="psutil"
            )
        )

        readings.append(
            SensorReading(
                id="memory_used_percentage",
                name="RAM Used Percentage",
                value=mem.percent,
                unit="%",
                category="memory",
                source="psutil"
            )
        )

        swap = psutil.swap_memory()

        readings.append(
            SensorReading(
                id="swap_used",
                name="SWAP Used",
                value=swap.used / (1024 ** 3),
                unit="GiB",
                category="memory",
                source="psutil"
            )
        )

        readings.append(
            SensorReading(
                id="swap_free",
                name="SWAP Free",
                value=swap.free / (1024 ** 3),
                unit="GiB",
                category="memory",
                source="psutil"
            )
        )

        readings.append(
            SensorReading(
                id="swap_percentage",
                name="SWAP Used Percentage",
                value=swap.percent,
                unit="%",
                category="memory",
                source="psutil"
            )
        )

        readings.append(
            SensorReading(
                id="network_sent",
                name="Bytes sent/s",
                value=tx_rate,
                unit="B/s",
                category="network",
                source="psutil"
            )
        )

        readings.append(
            SensorReading(
                id="network_received",
                name="Bytes received/s",
                value=rx_rate,
                unit="B/s",
                category="network",
                source="psutil"
            )
        )
        
        return readings

    def static_collect(self) -> list[SensorReading]:
        readings = []

        readings.append(
            SensorReading(
                id="cpu_core_count",
                name="CPU Cores",
                value=psutil.cpu_count(logical=False),
                unit="cores",
                category="cpu",
                source="psutil"
            )
        )

        readings.append(
            SensorReading(
                id="cpu_thread_count",
                name="CPU Threads",
                value=psutil.cpu_count(logical=True),
                unit="threads",
                category="cpu",
                source="psutil"
            )
        )

        mem = psutil.virtual_memory()

        readings.append(
            SensorReading(
                id="memory_total",
                name="RAM Total",
                value=mem.total / (1024 ** 3),
                unit="GiB",
                category="memory",
                source="psutil"
            )
        )

        swap = psutil.swap_memory()

        readings.append(
            SensorReading(
                id="swap_total",
                name="SWAP Total",
                value=swap.total / (1024 ** 3),
                unit="GiB",
                category="memory",
                source="psutil"
            )
        )

        return readings
