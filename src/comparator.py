"""
Compare SOP requirements versus the P&ID graph and log discrepancies.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List

import networkx as nx

from .logger import DiscrepancyLogger

LOGGER = logging.getLogger(__name__)


class Comparator:
    def __init__(self, graph: nx.Graph, sop_reqs: Dict[str, List[str]], log_path: Path):
        self.graph = graph
        self.sop_reqs = sop_reqs
        self.logger = DiscrepancyLogger(log_path)

    # ---------------------------------------------------------------- public
    def run(self) -> None:
        self._missing_components()
        self._unused_components()
        self.logger.flush()

    # ---------------------------------------------------------------- private
    def _missing_components(self) -> None:
        pid_labels = {data["label"] for _, data in self.graph.nodes(data=True) if data["label"]}
        for step, required in self.sop_reqs.items():
            missing = [c for c in required if c not in pid_labels]
            if missing:
                self.logger.log(
                    category="MISSING_COMPONENT",
                    message=f"SOP {step} requires {missing} not found in P&ID",
                    extra={"step": step, "missing": missing},
                )

    def _unused_components(self) -> None:
        sop_all = {c for comps in self.sop_reqs.values() for c in comps}
        for node, data in self.graph.nodes(data=True):
            label = data["label"]
            if label and label not in sop_all:
                self.logger.log(
                    category="UNREFERENCED_COMPONENT",
                    message=f"P&ID component {label} unused in SOP",
                    extra={"node": node, "label": label},
                    level="warning",
                )
