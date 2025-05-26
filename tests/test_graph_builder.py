import numpy as np
import networkx as nx
from src.graph_builder import GraphBuilder
from src.models import Component, ComponentType

def test_blank_image_no_edges():
    # two components but no lines drawn in image
    components = [
        Component(id="c1", type=ComponentType.PUMP,  label="PUMP",  bbox=(10, 10, 20, 20)),
        Component(id="c2", type=ComponentType.VALVE, label="VALVE", bbox=(50, 50, 20, 20)),
    ]
    blank = np.zeros((100, 100, 3), dtype=np.uint8)
    builder = GraphBuilder(components, blank)
    G = builder.build()

    # Should have exactly two nodes, zero edges
    assert G.number_of_nodes() == 2
    assert G.number_of_edges() == 0

    # Node attributes preserved
    for comp in components:
        assert comp.id in G.nodes
        assert G.nodes[comp.id]["label"] == comp.label
        assert G.nodes[comp.id]["type"] == comp.type.value
