import pynvml

from spark_sensors.dataset_definition import SensorReading
class NvidiaCollector:
    def __init__(self):
        self.success_device_count = False
        self.device_count = 0

        try:
            pynvml.nvmlInit()
            self.device_count = pynvml.nvmlDeviceGetCount()
        except pynvml.NVMLError:
            return
        
        self.success_device_count = True

    def dynamic_collect(self) -> list[SensorReading]:
        readings = []

        if self.success_device_count:
            for i in range(self.device_count):
                vram = None
                util = None
                temp = None
                power = None
                try:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle)
                except pynvml.NVMLError:
                    continue

                try:
                    vram = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    vram_used = vram.used
                    vram_free = vram.free
                except pynvml.NVMLError:
                    pass
                
                try:
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                except pynvml.NVMLError:
                    pass

                try:
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                except pynvml.NVMLError:
                    pass

                try:
                    power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000
                except pynvml.NVMLError:
                    pass

                display_name = f"{name} #{i}" if self.device_count > 1 else str(name)
                if vram is not None:
                    readings.append(
                        SensorReading(
                            id=f"nvidia_gpu_{i}_vram_used",
                            name=f"{display_name} VRAM Used",
                            value=float(f"{vram_used / (1024 ** 3):.2f}"),
                            unit="GiB",
                            category="gpu_memory",
                            source="nvidia"
                        )
                    )
                    
                    readings.append(
                        SensorReading(
                            id=f"nvidia_gpu_{i}_vram_free",
                            name=f"{display_name} VRAM Free",
                            value=float(f"{vram_free / (1024 ** 3):.2f}"),
                            unit="GiB",
                            category="gpu_memory",
                            source="nvidia"
                        )
                    )

                if power is not None:
                    readings.append(
                        SensorReading(
                            id=f"nvidia_gpu_{i}_power",
                            name=f"{display_name} Power",
                            value=power,
                            unit="W",
                            category="gpu_power",
                            source="nvidia"
                        )
                    )
                
                if util is not None:
                    readings.append(
                        SensorReading(
                            id=f"nvidia_gpu_{i}_gpu_utilization",
                            name=f"{display_name} GPU Utilization",
                            value=util.gpu,
                            unit="%",
                            category="gpu_general",
                            source="nvidia"
                        )
                    )

                    readings.append(
                        SensorReading(
                            id=f"nvidia_gpu_{i}_memory_utilization",
                            name=f"{display_name} Memory Utilization",
                            value=util.memory,
                            unit="%",
                            category="gpu_memory",
                            source="nvidia"
                        )
                    )
                    
                if temp is not None:
                    readings.append(
                        SensorReading(
                            id=f"nvidia_gpu_{i}_temperature",
                            name=f"{display_name} Temperature",
                            value=temp,
                            unit="°C",
                            category="gpu_temperature",
                            source="nvidia"
                        )
                    )


        return readings
    
    def static_collect(self) -> list[SensorReading]:
        readings = []
            
        
        if self.success_device_count:
            try:
                driver_version = pynvml.nvmlSystemGetDriverVersion()
            except pynvml.NVMLError:
                return []
            
            readings.append(
                SensorReading(
                    id="nvidia_driver_version",
                    name="NVIDIA Driver Version",
                    value=str(driver_version),
                    unit="",
                    category="gpu_general",
                    source="nvidia"
                )
            )
            
            for i in range(self.device_count):
                try:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle)
                    vram = pynvml.nvmlDeviceGetMemoryInfo(handle)
                except pynvml.NVMLError:
                    continue
                vram_total = vram.total
                display_name = f"{name} #{i}" if self.device_count > 1 else str(name)
                readings.append(
                    SensorReading(
                        id=f"nvidia_gpu_{i}_vram_total",
                        name=f"{display_name} VRAM Total",
                        value=float(f"{vram_total / (1024 ** 3):.3f}"),
                        unit="GiB",
                        category="gpu_memory",
                        source="nvidia"
                    )
                )
        else:
            return readings
        
        return readings