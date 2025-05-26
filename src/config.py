"""
Central configuration, loaded once at start-up.

✓ Works on both **Pydantic v1** and **v2** without deprecation warnings.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

# --------------------------------------------------------------------------- #
# Determine Pydantic version & import the right objects
try:                    # Pydantic v2
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import Field
    _PD_VERSION = 2
except ModuleNotFoundError:   # Pydantic v1 fallback
    from pydantic import BaseSettings, Field  # type: ignore
    SettingsConfigDict = None                 # type: ignore
    _PD_VERSION = 1

# --------------------------------------------------------------------------- #
# Helper: create a Field with an environment-variable alias
def _env_field(default: Any, env_name: str):
    if _PD_VERSION == 1:
        return Field(default, env=env_name)
    return Field(default, validation_alias=env_name)

# --------------------------------------------------------------------------- #
ROOT_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # ---------- paths ----------
    pid_path: Path  = _env_field(ROOT_DIR / "data/pid/diagram.pdf", "PID_PATH")
    sop_path: Path  = _env_field(ROOT_DIR / "data/sop/sop.docx",   "SOP_PATH")
    output_dir: Path = _env_field(ROOT_DIR / "output",             "OUTPUT_DIR")

    # ---------- model ----------
    yolo_model: Path  = _env_field(
        ROOT_DIR / "pre-trained-models/yolov5/yolov5s.pt", "YOLO_MODEL"
    )
    detection_conf: float = _env_field(0.3, "DETECTION_CONF")

    # ---------- misc ----------
    ocr_lang: str = _env_field("eng", "OCR_LANG")
    device: str   = _env_field("cpu", "DEVICE")

    # Pydantic v2 prefers model_config; v1 ignores it.
    model_config = SettingsConfigDict(frozen=True) if SettingsConfigDict else {}

settings = Settings()

# ensure output folders exist
(settings.output_dir / "graphs").mkdir(parents=True, exist_ok=True)
(settings.output_dir / "logs").mkdir(parents=True, exist_ok=True)
