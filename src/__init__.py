"""
pid2graph package initialisation.

Having this file makes the directory importable as `import src ...`.
It also sets a root logger configuration so sub-modules inherit it.
"""
from __future__ import annotations
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
