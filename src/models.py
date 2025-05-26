"""
Dataclasses & helper types shared across the project.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Tuple


class ComponentType(str, Enum):
    VALVE = "valve"
    PUMP = "pump"
    SENSOR = "sensor"
    PIPE = "pipe"
    OTHER = "other"


BBox = Tuple[int, int, int, int]  # x, y, w, h


@dataclass
class Component:
    id: str
    type: ComponentType
    label: str
    bbox: BBox
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class Edge:
    src_id: str
    dst_id: str
    label: str = ""
