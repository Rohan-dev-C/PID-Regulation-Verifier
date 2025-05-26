"""
src package for PID-Diagram-Analyzer.

Having this file means you can do:

    >>> from src.pid_parser import PIDParser

from anywhere once the `src/` directory is on `sys.path`.

It also sets a simple root logger so all sub-modules inherit it.
"""
from __future__ import annotations
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
