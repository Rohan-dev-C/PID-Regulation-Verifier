import numpy as np
import pytest
from src.pid_parser import PIDParser

class DummyResults:
    class Boxes:
        def __init__(self):
            self.xyxy = np.zeros((0, 4))
            self.cls = np.array([], dtype=int)
            self.conf = np.array([], dtype=float)
    def __init__(self):
        self.boxes = DummyResults.Boxes()

class DummyModel:
    def fuse(self): pass
    def predict(self, img, conf, verbose):
        return [DummyResults()]

@pytest.fixture(autouse=True)
def patch_parser(monkeypatch):
    monkeypatch.setattr(PIDParser, "_pdf_to_images", lambda self: [np.zeros((100,100,3), dtype=np.uint8)])
    monkeypatch.setattr(PIDParser, "model", DummyModel())
    yield

def test_parse_returns_empty_list_when_no_boxes():
    parser = PIDParser(pdf_path=None) 
    comps = parser.parse()
    assert isinstance(comps, list)
    assert comps == []
