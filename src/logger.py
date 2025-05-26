"""
Structured discrepancy logger that writes JSON lines.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class DiscrepancyLogger:
    def __init__(self, file_path: Path) -> None:
        self.file = Path(file_path)
        self._buffer: List[Dict[str, Any]] = []
        self._log = logging.getLogger(self.__class__.__name__)

    # ----------------------------------------------------------------
    def log(
        self,
        category: str,
        message: str,
        extra: Dict[str, Any],
        level: str = "error",
    ) -> None:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "level": level,
            "category": category,
            "message": message,
            **extra,
        }
        self._buffer.append(entry)
        getattr(self._log, level, self._log.error)(message)

    # ----------------------------------------------------------------
    def flush(self) -> None:
        if not self._buffer:
            return
        with self.file.open("a", encoding="utf-8") as fp:
            for rec in self._buffer:
                fp.write(json.dumps(rec) + "\n")
        self._log.info(
            "Wrote %d discrepancy records → %s", len(self._buffer), self.file
        )
        self._buffer.clear()
