"""
Structured discrepancy logger.

• Writes JSON-lines (machine-readable) to <name>.jsonl
• Automatically produces a parallel Markdown report   <name>.md
  that’s easy to read or view in GitHub.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class DiscrepancyLogger:
    def __init__(self, file_path: Path) -> None:
        self.jsonl_path = Path(file_path).with_suffix(".jsonl")
        self.md_path = self.jsonl_path.with_suffix(".md")
        self._buffer: List[Dict[str, Any]] = []
        self._log = logging.getLogger(self.__class__.__name__)

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

    def flush(self) -> None:
        if not self._buffer:
            return

        # 1️⃣  JSON-lines
        self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        with self.jsonl_path.open("a", encoding="utf-8") as fp:
            for rec in self._buffer:
                fp.write(json.dumps(rec) + "\n")

        # 2️⃣  Markdown table
        self._write_markdown_report()

        self._log.info(
            "Wrote %d records → %s (and Markdown)", len(self._buffer), self.jsonl_path
        )
        self._buffer.clear()

    def _write_markdown_report(self) -> None:
        """Convert the entire JSONL file to a Markdown table."""
        if not self.jsonl_path.is_file():
            return

        records = [
            json.loads(line)
            for line in self.jsonl_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if not records:
            return

        lines = [
            "# P&ID ⇌ SOP Discrepancy Report",
            "",
            f"_Updated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}_",
            "",
            "| Timestamp (UTC) | Level | Category | Message |",
            "|-----------------|-------|----------|---------|",
        ]
        for rec in records:
            lines.append(
                f"| {rec['ts']} | {rec['level'].upper()} | "
                f"{rec['category']} | {rec['message']} |"
            )

        self.md_path.write_text("\n".join(lines), encoding="utf-8")
