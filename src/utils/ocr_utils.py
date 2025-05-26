"""
Thin wrapper around pytesseract so call-sites stay clean.
"""
from __future__ import annotations

from pytesseract import image_to_string
import cv2
from typing import Tuple


def ocr_text(img, lang: str = "eng") -> str:
    """
    Returns raw OCR text for the given OpenCV image.

    Parameters
    ----------
    img : np.ndarray
        BGR or grayscale image.
    lang : str
        Tesseract language code, default "eng".
    """
    # pytesseract expects RGB
    if len(img.shape) == 2:
        rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    else:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return image_to_string(rgb, lang=lang).strip()
