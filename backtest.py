# backtest.py
# Offline analysis/backtest from metrics logs, using the same decision engine as main.py.
# Usage:
#   python3 backtest.py --log bitaxe_logs/<name>/20260116.log --out decisions.csv
from __future__ import annotations
import argparse
from datetime import datetime
from typing import List, Optional
from collections import deque
import csv

from models import Sample
from decision_engine import decide

def _parse_ts(s: str) -> float:
    # "YYYY-MM-DD HH:MM:SS"
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").timestamp()

def _read_samples(path: str) -> List[Sample]:
    out: List[Sample] = []
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline().strip()
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            if len(parts) != 6:
                continue
            ts, temp, vr, err, freq, vcore = parts
            if temp == "NA" or vr == "NA" or err == "NA" or freq == "NA" or vcore == "NA":
                continue
            out.append(Sample(
                ts=_parse_ts(ts),
                temp=float(temp),
                vr_temp=float(vr),
                err=float(err),
                freq=int(freq),
                vcore=int(vcore),
            ))
    return out

def main():
    p = argparse.ArgumentParser(description="BitaxeLiveOptimizer - backtest decisions on a metrics log")
    p.add_argument("--log", required=True, help="Path to a metrics log file (timestamp;temp;vrTemp;...)")
    p.add_argument("--out", default="decisions.csv", help="Output CSV (default decisions.csv)")
    p.add_argument("--apply-every", type=int, default=12, help="Apply/decide every N samples (default 12)")
    p.add_argument("--window", type=int, default=12, help="FIFO window size N (default 12)")
    args = p.parse_args()

    # Default cfg aligned with what we discussed; tune later
    cfg = {
        "freq_min": 400,
        "freq_max": 1100,
        "vcore_min": 1000,
        "vcore_max": 1400,
        "freq_step": 25,
        "vcore_step": 10,
        "window_n_min_valid": max(8, args.window // 2),
        "asic_soft": 65.0,
        "asic_hard": 68.0,
        "vr_soft": 78.0,
        "vr_hard": 82.0,
        "err_low": 0.6,
        "err_high": 1.0,
        "err_crit": 1.3,
        "slope_limit": 0.01,
        "allow_ramp_up": False,
    }

    samples = _read_samples(args.log)
    fifo = deque(maxlen=args.window)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ts","tempAvg","vrTempAvg","errAvg","slope","freq","vcore","decision","newFreq","newVcore","reason"])
        for i, s in enumerate(samples, start=1):
            fifo.append(s)
            if i % args.apply_every != 0:
                continue
            d = decide(list(fifo), cfg)
            w.writerow([
                datetime.fromtimestamp(s.ts).strftime("%Y-%m-%d %H:%M:%S"),
                d.temp_avg, d.vr_temp_avg, d.err_avg, d.slope,
                s.freq, s.vcore,
                d.action, d.new_freq, d.new_vcore, d.reason
            ])

if __name__ == "__main__":
    main()
