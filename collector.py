# collector.py
# Generates metrics logs for later analysis/backtest.
# Usage: python3 collector.py <IP> --duration 24h --interval 5
from __future__ import annotations
import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from bitaxe_api import BitaxeAPI
from log_utils import DailyFileWriter, METRICS_HEADER, fmt_ts
from timeparse import parse_duration_to_seconds

def _extract(status: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    def pick(*keys):
        for k in keys:
            if k in status and status[k] is not None:
                return status[k]
        return None
    try:
        temp = pick("temp", "asicTemp", "asic_temp")
        vr = pick("vrTemp", "vrmTemp", "vr_temp", "vrm_temp")
        err = pick("errorPercentage", "errorPercent", "error_percentage", "errPercent")
        freq = pick("frequency", "freq", "asicFrequency")
        vcore = pick("coreVoltage", "core_voltage", "vcore", "voltage")
        if None in (temp, vr, err, freq, vcore):
            return None
        return {
            "temp": float(temp),
            "vrTemp": float(vr),
            "errorPercentage": float(err),
            "frequency": int(freq),
            "coreVoltage": int(vcore),
        }
    except Exception:
        return None

def main():
    p = argparse.ArgumentParser(
        description=(
            "BitaxeLiveOptimizer - collector (metrics only).\n"
            "Duration default unit is seconds if digits only (e.g. 3600). You can also use 5s, 10min, 2h, 1d."
        )
    )
    p.add_argument("ip", help="Bitaxe IP address")
    p.add_argument("--name", default=None, help="Bitaxe name (folder). Default: IP")
    p.add_argument("--outdir", default="bitaxe_logs", help="Base directory for logs")
    p.add_argument("--interval", type=float, default=5.0, help="Poll interval (default 5s)")
    p.add_argument("--duration", default="24h", help="How long to run (default 24h)")
    p.add_argument("--timeout", type=float, default=5.0, help="HTTP timeout (default 5s)")
    p.add_argument("--keep-days", type=int, default=30, help="Keep last N daily files (default 30)")
    args = p.parse_args()

    api = BitaxeAPI(args.ip, timeout_s=args.timeout)
    name = args.name or args.ip
    writer = DailyFileWriter(Path(args.outdir), name, METRICS_HEADER, keep_days=args.keep_days)

    end = datetime.now() + timedelta(seconds=parse_duration_to_seconds(args.duration))

    try:
        while datetime.now() < end:
            now = datetime.now()
            fields = None
            try:
                status = api.get_status()
                fields = _extract(status)
            except Exception:
                fields = None

            if not fields:
                row = f"{fmt_ts(now)};NA;NA;NA;NA;NA"
            else:
                row = (
                    f"{fmt_ts(now)};"
                    f"{fields['temp']};{fields['vrTemp']};{fields['errorPercentage']};"
                    f"{fields['frequency']};{fields['coreVoltage']}"
                )
            writer.write(now, row)
            time.sleep(max(0.0, args.interval))
    finally:
        writer.close()

if __name__ == "__main__":
    main()
