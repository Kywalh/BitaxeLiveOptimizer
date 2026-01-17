# timeparse.py
# Parses durations like "3600" (seconds), "5s", "10min", "2h", "1d"
import re

_UNITS = {
    "s": 1, "sec": 1, "secs": 1, "second": 1, "seconds": 1,
    "m": 60, "min": 60, "mins": 60, "minute": 60, "minutes": 60,
    "h": 3600, "hr": 3600, "hrs": 3600, "hour": 3600, "hours": 3600,
    "d": 86400, "day": 86400, "days": 86400,
}

def parse_duration_to_seconds(value: str) -> int:
    """Default unit is seconds when the input is digits only."""
    if value is None:
        raise ValueError("Duration is None")
    s = str(value).strip().lower()
    if s.isdigit():
        return int(s)
    m = re.fullmatch(r"(\d+)\s*([a-z]+)", s)
    if not m:
        raise ValueError(f"Invalid duration format: {value}")
    n = int(m.group(1))
    unit = m.group(2)
    if unit not in _UNITS:
        raise ValueError(f"Unknown duration unit: {unit}")
    return n * _UNITS[unit]
