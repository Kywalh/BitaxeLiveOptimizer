# main.py
# BitaxeLiveOptimizer - LIVE optimizer (runs indefinitely).
#
# It reads config.json (IPs are fixed; no autodiscovery), polls every 5s,
# uses a FIFO window (12 samples by default), and may apply changes every window.
#
# Usage:
#   python3 main.py --config config.json
#
from __future__ import annotations
import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Dict, Any

from bitaxe_api import BitaxeAPI
from models import Sample
from decision_engine import decide
from log_utils import DailyFileWriter, DECISIONS_HEADER, fmt_ts

def _extract(status: Dict[str, Any]):
    def pick(*keys):
        for k in keys:
            if k in status and status[k] is not None:
                return status[k]
        return None
    temp = pick("temp", "asicTemp", "asic_temp")
    vr = pick("vrTemp", "vrmTemp", "vr_temp", "vrm_temp")
    err = pick("errorPercentage", "errorPercent", "error_percentage", "errPercent")
    freq = pick("frequency", "freq", "asicFrequency")
    vcore = pick("coreVoltage", "core_voltage", "vcore", "voltage")
    if None in (temp, vr, err, freq, vcore):
        return None
    return float(temp), float(vr), float(err), int(freq), int(vcore)

def main():
    p = argparse.ArgumentParser(description="BitaxeLiveOptimizer - LIVE optimizer (indefinite)")
    p.add_argument("--config", default="config.json", help="Path to config.json (default ./config.json)")
    args = p.parse_args()

    cfg_path = Path(args.config)
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    outdir = Path(cfg.get("logs_dir", "bitaxe_logs"))
    window_n = int(cfg.get("window_n", 12))
    apply_every_n = int(cfg.get("apply_every_n", 12))
    poll_interval_s = float(cfg.get("poll_interval_s", 5.0))
    timeout_s = float(cfg.get("timeout_s", 5.0))

    engine_cfg = cfg["engine"]
    engine_cfg["window_n_min_valid"] = int(engine_cfg.get("window_n_min_valid", max(8, window_n // 2)))

    # Per-device state
    devices = {}
    for d in cfg["devices"]:
        name = d["name"]
        ip = d["ip"]
        api = BitaxeAPI(ip, timeout_s=timeout_s)
        fifo = deque(maxlen=window_n)
        decisions_writer = DailyFileWriter(outdir / "decisions", name, DECISIONS_HEADER, keep_days=int(cfg.get("keep_days", 30)))
        devices[name] = {
            "api": api,
            "fifo": fifo,
            "writer": decisions_writer,
            "counter": 0,
            "last_freq": None,
            "last_vcore": None,
        }

    try:
        while True:
            now = datetime.now()
            for name, st in devices.items():
                api: BitaxeAPI = st["api"]
                fifo = st["fifo"]
                st["counter"] += 1

                sample = None
                try:
                    status = api.get_status()
                    ex = _extract(status)
                    if ex:
                        temp, vr, err, freq, vcore = ex
                        sample = Sample(ts=now.timestamp(), temp=temp, vr_temp=vr, err=err, freq=freq, vcore=vcore)
                        fifo.append(sample)
                except Exception:
                    # Skip sample on timeout/error
                    sample = None

                # Decide/apply every N polls (roughly 60s at 5s interval)
                if st["counter"] % apply_every_n != 0:
                    continue

                if not fifo:
                    # Still log a decision line so you can see "why nothing happened"
                    line = f"{fmt_ts(now)};NA;NA;NA;NA;NA;NA;NO_CHANGE;NA;NA;no_samples"
                    st["writer"].write(now, line)
                    continue

                d = decide(list(fifo), engine_cfg)
                cur = fifo[-1]

                new_freq = d.new_freq
                new_vcore = d.new_vcore

                # Apply changes if needed
                try:
                    if d.action == "FREQ_DOWN" or d.action == "FREQ_UP":
                        api.set_settings(frequency=new_freq)
                    elif d.action == "VCORE_DOWN" or d.action == "VCORE_UP":
                        api.set_settings(core_voltage=new_vcore)
                    # NO_CHANGE: do nothing
                except Exception:
                    # If apply fails, keep decision but note it
                    d = d.__class__(**{**d.__dict__, "reason": d.reason + "|apply_failed"})

                line = (
                    f"{fmt_ts(now)};"
                    f"{d.temp_avg if d.temp_avg is not None else 'NA'};"
                    f"{d.vr_temp_avg if d.vr_temp_avg is not None else 'NA'};"
                    f"{d.err_avg if d.err_avg is not None else 'NA'};"
                    f"{d.slope if d.slope is not None else 'NA'};"
                    f"{cur.freq};{cur.vcore};"
                    f"{d.action};"
                    f"{new_freq if new_freq is not None else 'NA'};"
                    f"{new_vcore if new_vcore is not None else 'NA'};"
                    f"{d.reason}"
                )
                st["writer"].write(now, line)

            time.sleep(max(0.0, poll_interval_s))
    finally:
        for st in devices.values():
            st["writer"].close()

if __name__ == "__main__":
    main()
