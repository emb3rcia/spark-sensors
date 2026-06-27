import pathlib
from dataclasses import dataclass

@dataclass
class SensorReading:
    id: str
    name: str
    value: float|int|str|tuple
    unit: str
    category: str
    source: str

@dataclass
class IntelCard:
    pci_bdf: str
    card_path: pathlib.Path
    vendor_id: str
    device_id: str | None
    pci_class: str | None
    revision: str | None
    subsystem_vendor: str | None
    subsystem_device: str | None
    bound_driver: str | None
    resolved_path: pathlib.Path
    render_node: pathlib.Path | None = None