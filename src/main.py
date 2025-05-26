"""
CLI entry-point:  python -m src.main
"""
from __future__ import annotations

import logging
import pickle
import sys
from pathlib import Path

import typer

from .config import settings
from .pid_parser import PIDParser
from .graph_builder import GraphBuilder
from .sop_parser import SOPParser
from .comparator import Comparator

LOGGER = logging.getLogger(__name__)
app = typer.Typer(add_completion=False)


# --------------------------------------------------------------------------- #
def _save_graph_pickle(graph, path: Path) -> None:
    """Version-agnostic helper to pickle a NetworkX graph."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fp:
        pickle.dump(graph, fp)
    LOGGER.info("Saved graph → %s", path)


@app.command()
def run(
    pid: Path = typer.Option(settings.pid_path, help="Path to P&ID PDF"),
    sop: Path = typer.Option(settings.sop_path, help="Path to SOP .docx"),
    out: Path = typer.Option(settings.output_dir, help="Output directory base"),
) -> None:
    LOGGER.info("Starting pipeline")

    # ---------- P&ID → components ------------------------------------------
    pid_parser = PIDParser(pid)
    components = pid_parser.parse()

    # Need first-page image for edge detection demo
    import pdf2image, numpy as np, cv2

    first_page = pdf2image.convert_from_path(str(pid))[0]
    original_img = cv2.cvtColor(np.array(first_page), cv2.COLOR_RGB2BGR)

    graph_builder = GraphBuilder(components, original_img)
    G = graph_builder.build()

    _save_graph_pickle(G, out / "graphs" / "pid_graph.gpickle")

    # ---------- SOP parse ---------------------------------------------------
    sop_reqs = SOPParser(sop).parse()

    # ---------- Compare & log ----------------------------------------------
    Comparator(G, sop_reqs, out / "logs" / "discrepancies.jsonl").run()
    LOGGER.info("Pipeline complete ✅")


if __name__ == "__main__":
    sys.exit(app())
