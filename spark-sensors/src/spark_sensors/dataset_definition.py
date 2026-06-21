from dataclasses import dataclass

@dataclass
class SensorReading:
    id: str
    name: str
    value: float|int|str|tuple
    unit: str
    category: str
    source: str