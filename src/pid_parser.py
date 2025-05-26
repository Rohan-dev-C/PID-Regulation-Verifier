"""
Convert a P&ID PDF into detected components (but not yet a graph).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import cv2
import numpy as np
from pdf2image import convert_from_path  # pillow-style images
from ultralytics import YOLO

from .config import settings
from .models import Component, ComponentType
from .utils import deskew, preprocess, ocr_text

LOGGER = logging.getLogger(__name__)


class PIDParser:
    def __init__(self, pdf_path: Path | str | None = None) -> None:
        self.pdf_path = Path(pdf_path or settings.pid_path)
        self.model = YOLO(settings.yolo_model)  # auto-download if needed
        self.model.fuse()
        LOGGER.info("Loaded YOLO model from %s", settings.yolo_model)

    # ------------------------------------------------------------------ public
    def parse(self) -> List[Component]:
        """Main entry – returns a list of detected `Component`s."""
        images = self._pdf_to_images()
        components: List[Component] = []
        for page_idx, img in enumerate(images):
            comps = self._process_page(img, page_idx)
            components.extend(comps)
        return components

    # ---------------------------------------------------------------- private
    def _pdf_to_images(self) -> List["np.ndarray"]:
        LOGGER.info("Converting %s to image(s)…", self.pdf_path)
        pil_pages = convert_from_path(str(self.pdf_path))
        return [cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR) for pil in pil_pages]

    def _process_page(self, img: "np.ndarray", page_idx: int) -> List[Component]:
        img = deskew(img)
        # run object detection
        results = self.model.predict(img, conf=settings.detection_conf, verbose=False)[0]

        comps: List[Component] = []
        for i, det in enumerate(results.boxes.xyxy.cpu().numpy()):
            x1, y1, x2, y2 = map(int, det[:4])
            cls_id = int(results.boxes.cls[i])
            conf = float(results.boxes.conf[i])
            label = self.model.model.names[cls_id]
            comp_type = ComponentType(label) if label in ComponentType.__members__.values() else ComponentType.OTHER

            crop = img[y1:y2, x1:x2]
            text = ocr_text(crop, lang=settings.ocr_lang)

            comp = Component(
                id=f"p{page_idx}_{i}",
                type=comp_type,
                label=text or label,
                bbox=(x1, y1, x2 - x1, y2 - y1),
                attributes={"confidence": f"{conf:.2f}"},
            )
            comps.append(comp)
            LOGGER.debug("Detected %s @ %s (%s)", comp.type, comp.bbox, comp.label)
        LOGGER.info("Page %d: %d components", page_idx, len(comps))
        return comps
