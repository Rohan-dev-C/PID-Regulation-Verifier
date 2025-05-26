"""
Project-wide configuration, loaded once at start-up.

You can override any field via environment variables,
e.g.  PID_PATH=/other/file.pdf  python -m src.main …
"""
# src/config.py

from __future__ import annotations
from pathlib import Path
from pydantic import BaseSettings, Field

# ─── Determine project root ───────────────────────────────────────────────────
# Assumes this file lives at <project_root>/src/config.py
ROOT_DIR = Path(__file__).resolve().parent.parent

# ─── Settings ─────────────────────────────────────────────────────────────────
class Settings(BaseSettings):
    # input / output
    pid_path: Path = Field(ROOT_DIR / "data" / "pid" / "diagram.pdf", env="PID_PATH")
    sop_path: Path = Field(ROOT_DIR / "data" / "sop" / "sop.docx", env="SOP_PATH")
    output_dir: Path = Field(ROOT_DIR / "output", env="OUTPUT_DIR")

    # YOLO checkpoint (expects pre-trained-models/yolov5/yolov5s.pt under project root)
    yolo_model: Path = Field(
        ROOT_DIR / "pre-trained-models" / "yolov5" / "yolov5s.pt",
        env="YOLO_MODEL",
    )
    detection_conf: float = Field(0.3, env="DETECTION_CONF")
    ocr_lang: str = Field("eng", env="OCR_LANG")

    # device for torch
    device: str = Field("cpu", env="DEVICE")

    class Config:
        frozen = True  # make settings immutable

# ─── Instantiate ──────────────────────────────────────────────────────────────
settings = Settings()

# create output subdirectories if they don't exist
(settings.output_dir / "graphs").mkdir(parents=True, exist_ok=True)
(settings.output_dir / "logs").mkdir(parents=True, exist_ok=True)