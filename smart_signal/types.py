from typing import List, Tuple, Optional, Literal, Dict
from pydantic import BaseModel
from dataclasses import dataclass

ClassName = Literal["car","bus","truck","motorcycle","bicycle","pedestrian","unknown"]

@dataclass
class BBox:
    x1: float
    y1: float
    x2: float
    y2: float

class Detection(BaseModel):
    bbox: Tuple[float, float, float, float]
    score: float
    cls: ClassName
    frame_id: int
    approach_id: str

class Track(BaseModel):
    track_id: int
    bbox: Tuple[float, float, float, float]
    cls: ClassName
    approach_id: str
    last_seen_frame: int
    is_counted: bool = False

class LaneStat(BaseModel):
    approach_id: str
    lane_id: str
    movement: Literal["through","left","right"]
    queue_len: int
    arrival_rate_vph: float
    occupancy: float
    spillback: bool

class Phase(BaseModel):
    id: str
    movements: List[Tuple[str, str]]  # (approach_id, movement)
    protected: bool = True

class ControllerAction(BaseModel):
    phase_id: str
    action: Literal["hold","next","preempt"]
    duration_s: float

class EmergencyEvent(BaseModel):
    vehicle_id: str
    vehicle_type: Literal["ambulance","fire","police"]
    approach_id: str
    eta_s: float
    siren_on: bool = True

class Splits(BaseModel):
    cycle_s: float
    greens_s: Dict[str, float]  # phase_id -> green seconds