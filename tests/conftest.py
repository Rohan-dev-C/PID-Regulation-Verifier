"""
Ensure the current checkout is first on sys.path.

Placing the project root (not the src/ sub-folder) on sys.path lets
`import src.comparator` resolve correctly.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent    
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

for p in list(sys.path)[1:]:
    if p.endswith("PID-Diagram-Analyzer") and Path(p) != ROOT:
        sys.path.remove(p)
