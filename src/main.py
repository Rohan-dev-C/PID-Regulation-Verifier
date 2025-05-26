"""
CLI entry-point:  python -m src.main  (or simply  python src/main.py)

Usage
-----
$ python -m src.main --pid data/pid/diagram.pdf --sop data/sop/sop.docx
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import cv2
import typer

from .config import settings
from .pid_parser import PIDParser
from .graph_builder import GraphBuilder
from .sop_parser import SOPParser
from .comparator import Comparator

LOGGER = logging.getLogger(__name__)
app = typer.Typer(add_completion=False)


@app.command()
def run(
    pid: Path = typer.Option(settings.pid_path, help="Path to P&ID PDF"),
    sop: Path = typer.Option(settings.sop_path, help="Path to SOP .docx"),
    out: Path = typer.Option(settings.output_dir, help="Output directory base"),
):
    LOGGER.info("Starting pipeline")
    # ---------- parse P&ID ----------
    pid_parser = PIDParser(pid)
    components = pid_parser.parse()

    # need original page image to infer edges; reuse the first page only for demo
    import pdf2image, numpy as np

    original_img = cv2.cvtColor(
        np.array(pdf2image.convert_from_path(str(pid))[0]), cv2.COLOR_RGB2BGR
    )

    graph_builder = GraphBuilder(components, original_img)
    G = graph_builder.build()
    graph_path = out / "graphs" / "pid_graph.gpickle"
    import networkx as nx

    nx.write_gpickle(G, graph_path)
    LOGGER.info("Saved graph → %s", graph_path)

    # ---------- parse SOP ----------
    sop_parser = SOPParser(sop)
    sop_reqs = sop_parser.parse()

    # ---------- compare ----------
    log_path = out / "logs" / "discrepancies.jsonl"
    comparator = Comparator(G, sop_reqs, log_path)
    comparator.run()
    LOGGER.info("Pipeline complete ✅")


if __name__ == "__main__":
    sys.exit(app())
