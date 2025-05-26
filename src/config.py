"""
Central configuration (Pydantic v1 *or* v2 compatible).

✔  No hard-coded local model path anymore – defaults to 'yolov8n.pt',
   which Ultralytics will download to its cache at first use.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any

# ─── Pydantic compatibility shim ────────────────────────────────────────────
try:                                      # Pydantic v2
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import Field
    _PD_V2 = True
except ModuleNotFoundError:               # Pydantic v1
    from pydantic import BaseSettings, Field  # type: ignore
    SettingsConfigDict = None             # type: ignore
    _PD_V2 = False


def _env_field(default: Any, env: str):
    """Return a Field with an env-var alias (works for v1 & v2)."""
    if _PD_V2:
        return Field(default, validation_alias=env)
    return Field(default, env=env)         # type: ignore[arg-type]


ROOT_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # ── I/O paths ──────────────────────────────────────────────────────────
    pid_path:     Path = _env_field(ROOT_DIR / "data/pid/diagram.pdf", "PID_PATH")
    sop_path:     Path = _env_field(ROOT_DIR / "data/sop/sop.docx",    "SOP_PATH")
    output_dir:   Path = _env_field(ROOT_DIR / "output",               "OUTPUT_DIR")

    # ── YOLO model (string triggers Ultralytics auto-download) ────────────
    yolo_model: str | Path = _env_field("yolov8n.pt", "YOLO_MODEL")

    detection_conf: float = _env_field(0.3, "DETECTION_CONF")
    ocr_lang:       str   = _env_field("eng", "OCR_LANG")
    device:         str   = _env_field("cpu", "DEVICE")

    # v2 uses model_config; v1 ignores it (safe).
    model_config = SettingsConfigDict(frozen=True) if SettingsConfigDict else {}

settings = Settings()

# Ensure output sub-dirs exist
(settings.output_dir / "graphs").mkdir(parents=True, exist_ok=True)
(settings.output_dir / "logs").mkdir(parents=True,  exist_ok=True)
