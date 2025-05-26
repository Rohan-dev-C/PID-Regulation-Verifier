"""
Low-level OpenCV helpers.
"""
from __future__ import annotations

import cv2
import numpy as np
from typing import Tuple


def preprocess(img: "np.ndarray") -> "np.ndarray":
    """Binarise + denoise for easier detection."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    return thresh


def deskew(img: "np.ndarray") -> "np.ndarray":
    """Very light deskew based on Hough-line predominant angle."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    coords = np.column_stack(np.where(gray < 255))
    if coords.size == 0:  # blank?
        return img
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
