"""
Ensure the current checkout is first on sys.path.

Placing the project root (not the src/ sub-folder) on sys.path lets
`import src.comparator` resolve correctly.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent      # …/PID-Regulation-Verifier
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Optional: drop any stale paths that still point at old duplicates
for p in list(sys.path)[1:]:
    if p.endswith("PID-Diagram-Analyzer") and Path(p) != ROOT:
        sys.path.remove(p)
