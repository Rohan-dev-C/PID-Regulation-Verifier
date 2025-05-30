"""
Convert a P&ID PDF into detected components.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import cv2
import numpy as np
from pdf2image import convert_from_path
from ultralytics import YOLO

from .config import settings
from .models import Component, ComponentType
from .utils import deskew, ocr_text

LOGGER = logging.getLogger(__name__)


def _to_np(arr):
    """torch.Tensor → np.ndarray, else np.asarray."""
    return arr.cpu().numpy() if hasattr(arr, "cpu") else np.asarray(arr)


class PIDParser:
    """
    Parse a P&ID PDF into a list of detected components.

    * Robustly loads the YOLO model:
        1. Try the path/name in `settings.yolo_model`.
        2. If that fails, fall back to `"yolov8n.pt"` which Ultralytics
           auto-downloads and caches.
    """

    model: YOLO | None = None  

    def __init__(self, pdf_path: Path | str | None = None) -> None:
        self.pdf_path = Path(pdf_path or settings.pid_path)

        if PIDParser.model is None:
            PIDParser.model = self._load_model()
            PIDParser.model.fuse()

    def _load_model(self) -> YOLO:
        """Try user-provided model, else fall back to yolov8n.pt."""
        model_ref = settings.yolo_model
        try:
            LOGGER.info("Loading YOLO model from %s", model_ref)
            return YOLO(model_ref)
        except Exception as exc:  
            LOGGER.warning(
                "Could not load model '%s' (%s). Falling back to 'yolov8n.pt'.",
                model_ref,
                exc,
            )
            return YOLO("yolov8n.pt")

    def parse(self) -> List[Component]:
        images = self._pdf_to_images()
        comps: List[Component] = []
        for idx, img in enumerate(images):
            comps.extend(self._process_page(img, idx))
        return comps

    def _pdf_to_images(self) -> List[np.ndarray]:
        pil_pages = convert_from_path(str(self.pdf_path))
        return [cv2.cvtColor(np.array(p), cv2.COLOR_RGB2BGR) for p in pil_pages]

    def _process_page(self, img: np.ndarray, page_idx: int) -> List[Component]:
        img = deskew(img)

        results = PIDParser.model.predict( 
            img, conf=settings.detection_conf, verbose=False
        )[0]

        xyxy   = _to_np(results.boxes.xyxy)
        cls_id = _to_np(results.boxes.cls)
        confs  = _to_np(results.boxes.conf)

        comps: List[Component] = []
        for i, det in enumerate(xyxy):
            x1, y1, x2, y2 = map(int, det[:4])
            label = PIDParser.model.model.names[int(cls_id[i])]  
            comp_type = (
                ComponentType(label)
                if label in ComponentType.__members__.values()
                else ComponentType.OTHER
            )
            crop = img[y1:y2, x1:x2]
            text = ocr_text(crop, lang=settings.ocr_lang)

            comps.append(
                Component(
                    id=f"p{page_idx}_{i}",
                    type=comp_type,
                    label=text or label,
                    bbox=(x1, y1, x2 - x1, y2 - y1),
                    attributes={"confidence": f"{float(confs[i]):.2f}"},
                )
            )
        return comps
