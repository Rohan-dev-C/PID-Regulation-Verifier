"""
Central configuration (Pydantic v1 *or* v2 compatible).

✔  No hard-coded local model path anymore – defaults to 'yolov8n.pt',
   which Ultralytics will download to its cache at first use.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any

try:                               
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import Field
    _PD_V2 = True
except ModuleNotFoundError:           
    from pydantic import BaseSettings, Field  
    SettingsConfigDict = None            
    _PD_V2 = False

def _env_field(default: Any, env: str):
    """Return a Field with an env-var alias (works for v1 & v2)."""
    if _PD_V2:
        return Field(default, validation_alias=env)
    return Field(default, env=env)       

ROOT_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    pid_path:     Path = _env_field(ROOT_DIR / "data/pid/diagram.pdf", "PID_PATH")
    sop_path:     Path = _env_field(ROOT_DIR / "data/sop/sop.docx",    "SOP_PATH")
    output_dir:   Path = _env_field(ROOT_DIR / "output",               "OUTPUT_DIR")

    yolo_model: str | Path = _env_field("yolov8n.pt", "YOLO_MODEL")

    detection_conf: float = _env_field(0.3, "DETECTION_CONF")
    ocr_lang:       str   = _env_field("eng", "OCR_LANG")
    device:         str   = _env_field("cpu", "DEVICE")

    model_config = SettingsConfigDict(frozen=True) if SettingsConfigDict else {}

settings = Settings()

(settings.output_dir / "graphs").mkdir(parents=True, exist_ok=True)
(settings.output_dir / "logs").mkdir(parents=True,  exist_ok=True)
