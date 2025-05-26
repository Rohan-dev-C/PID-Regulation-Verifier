"""
Pytest start-up hook.

Goals
-----
1.  Ensure the *current* repository’s ``src/`` directory is at the very
    front of ``sys.path`` so that::

        import src.pid_parser

    always succeeds.

2.  Remove any *other* ``…/PID-Diagram-Analyzer/src`` entries that might
    still linger on ``sys.path`` from an old duplicate checkout.
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# (1) Determine THIS repo’s src/ path
REPO_ROOT = Path(inspect.getfile(inspect.currentframe())).resolve().parents[1]
SRC_PATH  = REPO_ROOT / "src"

if not SRC_PATH.is_dir():
    raise RuntimeError(f"Expected src/ folder at {SRC_PATH}, but it doesn't exist!")

# Put it at the very front of the import search path
sys.path.insert(0, str(SRC_PATH))

# --------------------------------------------------------------------------- #
# (2) Prune stale duplicates (old check-outs called PID-Diagram-Analyzer/src)
for p in list(sys.path)[1:]:        # skip index 0 (we just added the good path)
    if p.endswith("PID-Diagram-Analyzer/src") and Path(p) != SRC_PATH:
        sys.path.remove(p)
# --------------------------------------------------------------------------- #
