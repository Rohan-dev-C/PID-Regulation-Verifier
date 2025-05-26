"""
Discrepancy logger.

• Writes a fresh JSONL log on every run (no duplicates from earlier runs)
• Converts that same data to Markdown for easy viewing.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


class DiscrepancyLogger:
    def __init__(self, file_path: Path) -> None:
        self.jsonl_path = Path(file_path).with_suffix(".jsonl")
        self.md_path = self.jsonl_path.with_suffix(".md")
        self._buffer: List[Dict[str, Any]] = []
        self._seen_in_run: Set[Tuple[str, str]] = set()  
        self._log = logging.getLogger(self.__class__.__name__)

    def log(
        self,
        category: str,
        message: str,
        extra: Dict[str, Any],
        level: str = "error",
    ) -> None:
        key = (category, message)
        if key in self._seen_in_run:
            return
        self._seen_in_run.add(key)

        entry = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "level": level.upper(),
            "category": category,
            "message": message,
            **extra,
        }
        self._buffer.append(entry)
        getattr(self._log, level, self._log.error)(message)

    def flush(self) -> None:
        if not self._buffer:
            return

        self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        with self.jsonl_path.open("w", encoding="utf-8") as fp:
            for rec in self._buffer:
                fp.write(json.dumps(rec) + "\n")

        self._write_markdown_report()

        self._log.info("Wrote %d discrepancy records", len(self._buffer))
        self._buffer.clear()
        self._seen_in_run.clear()

    def _write_markdown_report(self) -> None:
        records = self._buffer
        if not records:
            return

        lines = [
            "# P&ID ⇌ SOP Discrepancy Report",
            "",
            f"_Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}_",
            "",
            "| Timestamp (UTC) | Level | Category | Message |",
            "|-----------------|-------|----------|---------|",
        ]
        for r in records:
            lines.append(f"| {r['ts']} | {r['level']} | {r['category']} | {r['message']} |")

        self.md_path.write_text("\n".join(lines), encoding="utf-8")
