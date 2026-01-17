# models.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Sample:
    ts: float
    temp: float
    vr_temp: float
    err: float
    freq: int
    vcore: int

@dataclass(frozen=True)
class Decision:
    action: str  # NO_CHANGE | FREQ_UP | FREQ_DOWN | VCORE_UP | VCORE_DOWN
    new_freq: Optional[int] = None
    new_vcore: Optional[int] = None
    reason: str = ""
    temp_avg: Optional[float] = None
    vr_temp_avg: Optional[float] = None
    err_avg: Optional[float] = None
    slope: Optional[float] = None
