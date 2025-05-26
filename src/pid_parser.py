"""
Convert a P&ID PDF into detected components (but not yet a graph).
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
    """Helper: torch.Tensor → np.ndarray, otherwise return np.asarray(arr)."""
    return arr.cpu().numpy() if hasattr(arr, "cpu") else np.asarray(arr)


class PIDParser:
    """
    Parse a P&ID PDF into a list of detected components.

    The class-level ``model`` allows monkey-patching in tests.
    """
    model: YOLO | None = None  # populated lazily in __init__

    def __init__(self, pdf_path: Path | str | None = None) -> None:
        self.pdf_path = Path(pdf_path or settings.pid_path)
        if PIDParser.model is None:
            LOGGER.info("Loading YOLO model from %s", settings.yolo_model)
            PIDParser.model = YOLO(settings.yolo_model)
            PIDParser.model.fuse()

    # ------------------------------------------------------------------ public
    def parse(self) -> List[Component]:
        images = self._pdf_to_images()
        comps: List[Component] = []
        for idx, img in enumerate(images):
            comps.extend(self._process_page(img, idx))
        return comps

    # ---------------------------------------------------------------- private
    def _pdf_to_images(self) -> List[np.ndarray]:
        LOGGER.info("Converting %s to image(s)…", self.pdf_path)
        pil_pages = convert_from_path(str(self.pdf_path))
        return [cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR) for pil in pil_pages]

    def _process_page(self, img: np.ndarray, page_idx: int) -> List[Component]:
        img = deskew(img)

        results = PIDParser.model.predict(  # type: ignore[arg-type]
            img, conf=settings.detection_conf, verbose=False
        )[0]

        # ── normalise result arrays to NumPy ────────────────────────────────
        xyxy = _to_np(results.boxes.xyxy)
        cls_arr = _to_np(results.boxes.cls)
        conf_arr = _to_np(results.boxes.conf)

        comps: List[Component] = []
        for i, det in enumerate(xyxy):
            x1, y1, x2, y2 = map(int, det[:4])
            cls_id = int(cls_arr[i])
            conf = float(conf_arr[i])

            label = PIDParser.model.model.names[cls_id]  # type: ignore[attr-defined]
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
                    attributes={"confidence": f"{conf:.2f}"},
                )
            )
            LOGGER.debug("Detected %s @ %s (%s)", comp_type, (x1, y1, x2, y2), text or label)

        LOGGER.info("Page %d: %d components", page_idx, len(comps))
        return comps
