# bitaxe_api.py
# Minimal AxeOS HTTP client. Endpoints can vary by firmware; we try common ones.
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional
import requests

@dataclass
class BitaxeAPI:
    ip: str
    timeout_s: float = 5.0
    session: Optional[requests.Session] = None

    def __post_init__(self):
        if self.session is None:
            self.session = requests.Session()

    def _base(self) -> str:
        return f"http://{self.ip}"

    def get_status(self) -> Dict[str, Any]:
        endpoints = ["/api/system/status", "/api/status", "/api/v1/status"]
        last = None
        for ep in endpoints:
            try:
                r = self.session.get(self._base() + ep, timeout=self.timeout_s)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                last = e
        raise RuntimeError(f"Unable to fetch status from {self.ip}: {last}")

    def set_settings(self, frequency: Optional[int] = None, core_voltage: Optional[int] = None) -> None:
        payload: Dict[str, Any] = {}
        if frequency is not None:
            payload["frequency"] = int(frequency)
        if core_voltage is not None:
            payload["coreVoltage"] = int(core_voltage)
        if not payload:
            return
        endpoints = ["/api/system/settings", "/api/settings", "/api/v1/settings"]
        last = None
        for ep in endpoints:
            try:
                r = self.session.post(self._base() + ep, json=payload, timeout=self.timeout_s)
                r.raise_for_status()
                return
            except Exception as e:
                last = e
        raise RuntimeError(f"Unable to set settings on {self.ip}: {last}")
