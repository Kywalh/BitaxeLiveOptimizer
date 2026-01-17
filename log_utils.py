# log_utils.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, TextIO

METRICS_HEADER = "timestamp;temp;vrTemp;errorPercentage;frequency;coreVoltage"
DECISIONS_HEADER = "timestamp;tempAvg;vrTempAvg;errAvg;slope;frequency;coreVoltage;decision;newFrequency;newCoreVoltage;reason"

def fmt_ts(now: datetime) -> str:
    return now.strftime("%Y-%m-%d %H:%M:%S")

@dataclass
class DailyFileWriter:
    base_dir: Path
    bitaxe_name: str
    header: str
    keep_days: int = 30

    _current_date: Optional[str] = None
    _fh: Optional[TextIO] = None

    def _folder(self) -> Path:
        d = self.base_dir / self.bitaxe_name
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _path_for_date(self, yyyymmdd: str) -> Path:
        return self._folder() / f"{yyyymmdd}.log"

    def _open_for(self, now: datetime) -> None:
        yyyymmdd = now.strftime("%Y%m%d")
        if self._current_date == yyyymmdd and self._fh is not None:
            return
        self.close()
        self._current_date = yyyymmdd
        path = self._path_for_date(yyyymmdd)
        new_file = not path.exists()
        self._fh = open(path, "a", encoding="utf-8", newline="\n")
        if new_file:
            self._fh.write(self.header + "\n")
            self._fh.flush()
        self._prune_old_files()

    def _prune_old_files(self) -> None:
        files = sorted(self._folder().glob("*.log"))
        if len(files) <= self.keep_days:
            return
        for p in files[: max(0, len(files) - self.keep_days)]:
            try:
                p.unlink()
            except OSError:
                pass

    def write(self, now: datetime, line: str) -> None:
        self._open_for(now)
        assert self._fh is not None
        self._fh.write(line + "\n")
        self._fh.flush()

    def close(self) -> None:
        if self._fh:
            try:
                self._fh.flush()
            except Exception:
                pass
            try:
                self._fh.close()
            except Exception:
                pass
        self._fh = None
        self._current_date = None
