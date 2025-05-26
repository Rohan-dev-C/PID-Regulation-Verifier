"""
Convert detected components into a NetworkX graph with inferred edges.
"""
from __future__ import annotations

import logging
from typing import List

import cv2
import networkx as nx
import numpy as np

from .models import Component, Edge
from .utils import preprocess

LOGGER = logging.getLogger(__name__)


class GraphBuilder:
    def __init__(self, components: List[Component], original_img):
        self.components = components
        self.img = original_img  
        
    def build(self) -> nx.Graph:
        G = nx.Graph()
        for comp in self.components:
            G.add_node(
                comp.id,
                type=comp.type.value,
                label=comp.label,
                **comp.attributes,
                bbox=comp.bbox,
            )

        edges = self._infer_edges()
        for edge in edges:
            G.add_edge(edge.src_id, edge.dst_id, label=edge.label)

        LOGGER.info("Graph built - %d nodes, %d edges", G.number_of_nodes(), G.number_of_edges())
        return G

    def _infer_edges(self) -> List[Edge]:
        """
        Ultra-light heuristic:
            • Convert page to binary mask of dark lines.
            • Build a skeleton and find connected component centroids.
            • Connect nearest pairs if a line exists between their centroids.
        This is *not* production-grade; tweak for real projects.
        """
        bin_img = preprocess(self.img)
        lines = cv2.Canny(bin_img, 50, 150, apertureSize=3)
        edges: List[Edge] = []

        centroids = {
            comp.id: (
                comp.bbox[0] + comp.bbox[2] // 2,
                comp.bbox[1] + comp.bbox[3] // 2,
            )
            for comp in self.components
        }
        ids = list(centroids.keys())

        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                p1, p2 = centroids[ids[i]], centroids[ids[j]]
                mask = self._sample_line(lines, p1, p2)
                if np.count_nonzero(mask) > 0:  
                    edges.append(Edge(src_id=ids[i], dst_id=ids[j]))
                    LOGGER.debug("Edge inferred %s ↔ %s", ids[i], ids[j])
        return edges

    @staticmethod
    def _sample_line(edge_img, p1, p2, num=50):
        xs = np.linspace(p1[0], p2[0], num=num).astype(int)
        ys = np.linspace(p1[1], p2[1], num=num).astype(int)
        return edge_img[ys, xs]
