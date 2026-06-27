import pathlib
import ctypes

from spark_sensors.dataset_definition import SensorReading, IntelCard


class IntelCollector:
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
        
    #made with HELP of ai     
    def _try_pyzes(self):
        try:
            import pyzes
            self.pyzes = pyzes
        except ModuleNotFoundError as error:
            if error.name != "pyzes":
                raise

            self.pyzes = None
        except OSError:
            self.pyzes = None

    #made with HELP of ai
    def _init_pyzes(self):

        self.sysman_available = False
        self.sysman_drivers = []
        self.sysman_devices = []
        
        pyzes = self.pyzes
        
        if pyzes is None:
            return
        
        try:
            result = pyzes.zesInit(0)
        except OSError:
            return


        if result != pyzes.ZE_RESULT_SUCCESS:
            return
        
        driver_count = ctypes.c_uint32(0)

        try:
            result = pyzes.zesDriverGet(
                ctypes.byref(driver_count),
                None
            )
        except OSError:
            return

        if result != pyzes.ZE_RESULT_SUCCESS:
            return

        if driver_count.value == 0:
            return

        DriverArray = (
            pyzes.zes_driver_handle_t * driver_count.value
        )

        drivers = DriverArray()
        try:
            result = pyzes.zesDriverGet(
                ctypes.byref(driver_count),
                drivers
            )
        except OSError:
            return

        if result != pyzes.ZE_RESULT_SUCCESS:
            return
        
        self.sysman_drivers = list(drivers[:driver_count.value])

        for driver in self.sysman_drivers:
            device_count = ctypes.c_uint32(0)
            
            try:
                result = pyzes.zesDeviceGet(
                    driver,
                    ctypes.byref(device_count),
                    None
                )
            except OSError:
                continue

            if result != pyzes.ZE_RESULT_SUCCESS:
                continue

            if device_count.value == 0:
                continue

            DeviceArray = (
                pyzes.zes_device_handle_t * device_count.value
            )

            devices = DeviceArray()

            try:
                result = pyzes.zesDeviceGet(
                    driver,
                    ctypes.byref(device_count),
                    devices
                )
            except OSError:
                continue

            if result != pyzes.ZE_RESULT_SUCCESS:
                continue

            self.sysman_devices.extend(
                devices[:device_count.value]
            )
            
        self.sysman_available = len(self.sysman_devices) > 0

    #made with HELP of ai
    def _get_sysman_device_properties(self, handle):
        pyzes = self.pyzes
        if pyzes is None:
            return None
        props = pyzes.zes_device_properties_t()
        props.stype = pyzes.ZES_STRUCTURE_TYPE_DEVICE_PROPERTIES
        props.pNext = None

        try:
            result = pyzes.zesDeviceGetProperties(
                handle,
                ctypes.byref(props)
            )
        except OSError:
            return None

        if result != pyzes.ZE_RESULT_SUCCESS:
            return None
        
        return props
        
    #made with HELP of ai
    def _decode_sysman_text(self, value) -> str:
        raw = bytes(value)
        return raw.split(b"\0", 1)[0].decode(
            "utf-8",
            errors="replace",
        )

    #made with HELP of ai
    def _get_sysman_pci_bdf(self, handle) -> str | None:
        pyzes = self.pyzes

        if pyzes is None:
            return None

        if not hasattr(pyzes, "zesDevicePciGetProperties"):
            return None
        
        pci = pyzes.zes_pci_properties_t()
        pci.stype = pyzes.ZES_STRUCTURE_TYPE_PCI_PROPERTIES
        pci.pNext = None
        try:
            result = pyzes.zesDevicePciGetProperties(
                handle,
                ctypes.byref(pci),
            )
        except OSError:
            return None
        
        if result != pyzes.ZE_RESULT_SUCCESS:
            return None
        
        address = pci.address
        bdf = (
            f"{address.domain:04x}:"
            f"{address.bus:02x}:"
            f"{address.device:02x}."
            f"{address.function:x}"
        )
        return bdf

    def _map_sysman_to_bdf(self):
        self.sysman_by_bdf.clear()
        self.sysman_properties_by_bdf.clear()

        cards_by_bdf = {
            card.pci_bdf.lower(): card
            for card in self.cards
        }

        for handle in self.sysman_devices:
            props = self._get_sysman_device_properties(handle)
            if props is None:
                continue

            bdf = self._get_sysman_pci_bdf(handle)
            if bdf is None:
                continue

            card = cards_by_bdf.get(bdf.lower())

            if card is None:
                continue

            self.sysman_by_bdf[bdf.lower()] = handle
            self.sysman_properties_by_bdf[bdf.lower()] = props

    def _enumerate_frequency_domains(self, device_handle):
        pyzes = self.pyzes
        if pyzes is None:
            return []
        
        frequency_count = ctypes.c_uint32(0)

        try:
            result = pyzes.zesDeviceEnumFrequencyDomains(
                device_handle,
                ctypes.byref(frequency_count),
                None
            )
        except OSError:
            return []
        
        if result != pyzes.ZE_RESULT_SUCCESS:
            return []
        
        if frequency_count.value == 0:
            return []

        FrequencyArray = (
            pyzes.zes_freq_handle_t * frequency_count.value
        )

        handles = FrequencyArray()

        try:
            result = pyzes.zesDeviceEnumFrequencyDomains(
                device_handle,
                ctypes.byref(frequency_count),
                handles
            )
        except OSError:
            return []
        
        if result != pyzes.ZE_RESULT_SUCCESS:
            return []
        
        return list(handles[:frequency_count.value])
    
    def _get_frequency_properties(self, frequency_handle):
        pyzes = self.pyzes

        if pyzes is None:
            return None
        
        props = pyzes.zes_freq_properties_t()
        props.stype = pyzes.ZES_STRUCTURE_TYPE_FREQ_PROPERTIES
        props.pNext = None

        try:
            result = pyzes.zesFrequencyGetProperties(
                frequency_handle,
                ctypes.byref(props),
            )
        except OSError:
            return None
        
        if result != pyzes.ZE_RESULT_SUCCESS:
            return None
        
        return props
    
    def _get_frequency_state(self, frequency_handle):
        pyzes = self.pyzes
        
        if pyzes is None:
            return None
        
        state = pyzes.zes_freq_state_t()
        state.stype = pyzes.ZES_STRUCTURE_TYPE_FREQ_STATE
        state.pNext = None

        try:
            result = pyzes.zesFrequencyGetState(
                frequency_handle,
                ctypes.byref(state)
            )
        except OSError:
            return None
        
        if result != pyzes.ZE_RESULT_SUCCESS:
            return None
        
        return state
    
    def _map_frequency_domains(self):
        self.frequency_domains_by_bdf.clear()
        
        for bdf, handle in self.sysman_by_bdf.items():
            freq_handles = self._enumerate_frequency_domains(handle)
            if not freq_handles:
                continue

            properties = []

            for freq_handle in freq_handles:
                freq_props = self._get_frequency_properties(freq_handle)
                if freq_props is None:
                    continue
                
                properties.append((freq_handle, freq_props))
            if properties:
                self.frequency_domains_by_bdf[bdf] = properties

    def _frequency_domain_name(self, domain_type):
        pyzes = self.pyzes
        memory_domain = getattr(pyzes, "ZES_FREQ_DOMAIN_MEMORY", None)

        if pyzes is None:
            return "Unknown domain pyzes error"

        if domain_type is None:
            return "Unknown domain type is none"
        
        if domain_type == pyzes.ZES_FREQ_DOMAIN_GPU:
            return "GPU"
        elif domain_type == memory_domain and memory_domain is not None:
            return "Memory"
        else:
            return f"Unknown {domain_type}"

    def __init__(self):
        self.cards: list[IntelCard] = []
        self.pyzes = None
        self.sysman_available = False
        self.sysman_drivers = []
        self.sysman_devices = []
        self.sysman_by_bdf: dict[str, object] = {}
        self.sysman_properties_by_bdf: dict[str, object] = {}
        self.frequency_domains_by_bdf: dict[str, list[tuple[object, object]]] = {}
        self._try_pyzes()
        root = pathlib.Path("/sys/class/drm")

        if not root.is_dir():
            return

        for card in root.iterdir():
            if not card.name.startswith("card"):
                continue

            if not card.name[4:].isdigit():
                continue

            device_path = (card / "device")
            
            if not device_path.is_dir():
                continue

            vendor = self._read_text(device_path / "vendor")

            if vendor is None or vendor.lower() != "0x8086":
                continue
            resolved_path = device_path.resolve()
            device_id = self._read_text(device_path / "device")
            bdf = resolved_path.name
            driver_path = (device_path / "driver")

            if driver_path.exists():
                driver_name = driver_path.resolve().name
            else:
                driver_name = None

            pcie_class = self._read_text(device_path / "class")
            rev = self._read_text(device_path / "revision")
            sub_vendor = self._read_text(device_path / "subsystem_vendor")
            sub_device = self._read_text(device_path / "subsystem_device")

            self.cards.append(
                IntelCard(
                    pci_bdf=bdf,
                    card_path=card,
                    vendor_id=vendor,
                    device_id=device_id,
                    pci_class=pcie_class,
                    revision=rev,
                    subsystem_vendor=sub_vendor,
                    subsystem_device=sub_device,
                    bound_driver=driver_name,
                    resolved_path=resolved_path
                )
            )
        for render in root.iterdir():
            if not render.name.startswith("renderD"):
                continue

            if not render.name[7:].isdigit():
                continue

            render_device_path = render / "device"

            if not render_device_path.is_dir():
                continue
            
            resolved_render_device = render_device_path.resolve()

            for card in self.cards:
                if card.resolved_path == resolved_render_device:
                    card.render_node = pathlib.Path("/dev/dri") / render.name
                    break  

        if self.cards:
            self._init_pyzes() 

        if self.sysman_available: 
            self._map_sysman_to_bdf()
            self._map_frequency_domains()
    
    def dynamic_collect(self) -> list[SensorReading]:
        readings = []
        
        for bdf, domains in self.frequency_domains_by_bdf.items():
            for frequency_handle, properties in domains:
                state = self._get_frequency_state(frequency_handle)

                if state is None:
                    continue

                domain_name = self._frequency_domain_name(properties.type)
                domain_id = domain_name.lower().replace(" ", "_")
                bdf_id = bdf.replace(":", "_").replace(".", "_")

                if state.actual >= 0:
                    readings.append(
                        SensorReading(
                            id=f"intel_gpu_{bdf_id}_actual_frequency_{domain_id}",
                            name=f"Intel GPU {bdf} {domain_name} Actual Frequency",
                            value=state.actual,
                            unit="MHz",
                            category="gpu",
                            source="intel_sysman"
                        )
                    )

                if state.request >= 0:
                    readings.append(
                        SensorReading(
                            id=f"intel_gpu_{bdf_id}_requested_frequency_{domain_id}",
                            name=f"Intel GPU {bdf} {domain_name} Requested Frequency",
                            value=state.request,
                            unit="MHz",
                            category="gpu",
                            source="intel_sysman"
                        )
                    )

        return readings

    def static_collect(self) -> list[SensorReading]:
        readings = []
        
        for bdf, domains in self.frequency_domains_by_bdf.items():
            for _, properties in domains:
                domain_name = self._frequency_domain_name(properties.type)
                domain_id = domain_name.lower().replace(" ", "_")
                bdf_id = bdf.replace(":", "_").replace(".", "_")

                if properties.min >= 0:
                    readings.append(
                        SensorReading(
                            id=f"intel_gpu_{bdf_id}_min_frequency_{domain_id}",
                            name=f"Intel GPU {bdf} {domain_name} Minimum Frequency",
                            value=properties.min,
                            unit="MHz",
                            category="gpu",
                            source="intel_sysman"
                        )
                    )
                
                if properties.max >= 0:
                    readings.append(
                        SensorReading(
                            id=f"intel_gpu_{bdf_id}_max_frequency_{domain_id}",
                            name=f"Intel GPU {bdf} {domain_name} Maximum Frequency",
                            value=properties.max,
                            unit="MHz",
                            category="gpu",
                            source="intel_sysman"
                        )
                    )
        for bdf, properties in self.sysman_properties_by_bdf.items():
                model = self._decode_sysman_text(properties.modelName)
                vendor = self._decode_sysman_text(properties.vendorName)
                driver = self._decode_sysman_text(properties.driverVersion)
                bdf_id = bdf.replace(":", "_").replace(".", "_")

                if model:
                    readings.append(
                        SensorReading(
                            id=f"intel_gpu_{bdf_id}_model_name",
                            name=f"Intel GPU {bdf} Model Name",
                            value=model,
                            unit="",
                            category="gpu",
                            source="intel_sysman"
                        )
                    )
                
                if vendor:
                    readings.append(
                        SensorReading(
                            id=f"intel_gpu_{bdf_id}_vendor_name",
                            name=f"Intel GPU {bdf} Vendor Name",
                            value=vendor,
                            unit="",
                            category="gpu",
                            source="intel_sysman"
                        )
                    )
                
                if driver:
                    readings.append(
                        SensorReading(
                            id=f"intel_gpu_{bdf_id}_driver_version",
                            name=f"Intel GPU {bdf} Driver Version",
                            value=driver,
                            unit="",
                            category="gpu",
                            source="intel_sysman"
                        )
                    )

        return readings