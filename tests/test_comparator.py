import json
import networkx as nx
from src.comparator import Comparator

def test_comparator_logs_missing_and_unreferenced(tmp_path):
    G = nx.Graph()
    G.add_node("n1", label="PUMP")
    G.add_node("n2", label="VALVE")

    sop_reqs = {"step_0": ["PUMP", "SENSOR"]}

    log_path = tmp_path / "discrepancies.jsonl"
    comp = Comparator(G, sop_reqs, log_path)
    comp.run()

    lines = log_path.read_text().splitlines()
    entries = [json.loads(l) for l in lines]

    categories = {e["category"] for e in entries}
    assert "MISSING_COMPONENT" in categories
    assert "UNREFERENCED_COMPONENT" in categories

    messages = [e["message"] for e in entries]
    assert any("SENSOR" in m for m in messages)
    assert any("VALVE" in m for m in messages)
