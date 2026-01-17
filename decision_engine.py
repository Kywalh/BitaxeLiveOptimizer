# decision_engine.py
# V1 conservative decision engine.
# You will tune thresholds later; for now it avoids stupid moves.
from __future__ import annotations
from dataclasses import dataclass
from typing import Deque, Dict, Any, List, Tuple
import math

from models import Sample, Decision

def _linreg_slope(ts: List[float], ys: List[float]) -> float:
    n = len(ts)
    if n < 2:
        return 0.0
    t_mean = sum(ts) / n
    y_mean = sum(ys) / n
    num = sum((t - t_mean) * (y - y_mean) for t, y in zip(ts, ys))
    den = sum((t - t_mean) ** 2 for t in ts)
    return 0.0 if den == 0 else (num / den)

def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))

def decide(window: List[Sample], cfg: Dict[str, Any]) -> Decision:
    """Return a Decision based on a FIFO window of valid samples."""
    if len(window) < cfg["window_n_min_valid"]:
        return Decision(action="NO_CHANGE", reason="window_insufficient")

    temps = [s.temp for s in window]
    vrs = [s.vr_temp for s in window]
    errs = [s.err for s in window]
    ts = [s.ts for s in window]

    temp_avg = sum(temps) / len(temps)
    vr_avg = sum(vrs) / len(vrs)
    err_avg = sum(errs) / len(errs)

    slope_asic = _linreg_slope(ts, temps)
    slope_vr = _linreg_slope(ts, vrs)
    slope = max(slope_asic, slope_vr)

    cur = window[-1]
    freq = cur.freq
    vcore = cur.vcore

    # --- Priority 1: hard safety ---
    if temp_avg >= cfg["asic_hard"] or vr_avg >= cfg["vr_hard"]:
        # reduce freq first, then vcore
        new_freq = _clamp(freq - cfg["freq_step"], cfg["freq_min"], cfg["freq_max"])
        if new_freq != freq:
            return Decision("FREQ_DOWN", new_freq=new_freq, reason="temp_hard", temp_avg=temp_avg, vr_temp_avg=vr_avg, err_avg=err_avg, slope=slope)
        new_v = _clamp(vcore - cfg["vcore_step"], cfg["vcore_min"], cfg["vcore_max"])
        if new_v != vcore:
            return Decision("VCORE_DOWN", new_vcore=new_v, reason="temp_hard", temp_avg=temp_avg, vr_temp_avg=vr_avg, err_avg=err_avg, slope=slope)
        return Decision("NO_CHANGE", reason="at_min_limits_temp_hard", temp_avg=temp_avg, vr_temp_avg=vr_avg, err_avg=err_avg, slope=slope)

    # --- Priority 2: thermal trend (stability) ---
    if slope >= cfg["slope_limit"] and (temp_avg >= cfg["asic_soft"] or vr_avg >= cfg["vr_soft"]):
        new_freq = _clamp(freq - cfg["freq_step"], cfg["freq_min"], cfg["freq_max"])
        if new_freq != freq:
            return Decision("FREQ_DOWN", new_freq=new_freq, reason="slope_exceeded", temp_avg=temp_avg, vr_temp_avg=vr_avg, err_avg=err_avg, slope=slope)

    # --- Priority 3: error control ---
    if err_avg >= cfg["err_crit"]:
        new_freq = _clamp(freq - cfg["freq_step"], cfg["freq_min"], cfg["freq_max"])
        if new_freq != freq:
            return Decision("FREQ_DOWN", new_freq=new_freq, reason="err_crit", temp_avg=temp_avg, vr_temp_avg=vr_avg, err_avg=err_avg, slope=slope)
        new_v = _clamp(vcore - cfg["vcore_step"], cfg["vcore_min"], cfg["vcore_max"])
        if new_v != vcore:
            return Decision("VCORE_DOWN", new_vcore=new_v, reason="err_crit", temp_avg=temp_avg, vr_temp_avg=vr_avg, err_avg=err_avg, slope=slope)
        return Decision("NO_CHANGE", reason="at_min_limits_err_crit", temp_avg=temp_avg, vr_temp_avg=vr_avg, err_avg=err_avg, slope=slope)

    if err_avg >= cfg["err_high"]:
        new_freq = _clamp(freq - cfg["freq_step"], cfg["freq_min"], cfg["freq_max"])
        if new_freq != freq:
            return Decision("FREQ_DOWN", new_freq=new_freq, reason="err_high", temp_avg=temp_avg, vr_temp_avg=vr_avg, err_avg=err_avg, slope=slope)

    # --- Optional gentle up (disabled by default) ---
    if cfg.get("allow_ramp_up", False):
        if err_avg <= cfg["err_low"] and temp_avg <= cfg["asic_soft"] and vr_avg <= cfg["vr_soft"] and slope < cfg["slope_limit"]:
            new_freq = _clamp(freq + cfg["freq_step"], cfg["freq_min"], cfg["freq_max"])
            if new_freq != freq:
                return Decision("FREQ_UP", new_freq=new_freq, reason="margin", temp_avg=temp_avg, vr_temp_avg=vr_avg, err_avg=err_avg, slope=slope)

    return Decision("NO_CHANGE", reason="stable", temp_avg=temp_avg, vr_temp_avg=vr_avg, err_avg=err_avg, slope=slope)
