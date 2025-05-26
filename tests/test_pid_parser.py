import numpy as np
import pytest
from src.pid_parser import PIDParser

# --- Dummy objects to patch into PIDParser.model.predict() ---
class DummyResults:
    class Boxes:
        def __init__(self):
            # no detections
            self.xyxy = np.zeros((0, 4))
            self.cls = np.array([], dtype=int)
            self.conf = np.array([], dtype=float)
    def __init__(self):
        self.boxes = DummyResults.Boxes()

class DummyModel:
    def fuse(self): pass
    def predict(self, img, conf, verbose):
        # return a list of one DummyResults
        return [DummyResults()]

@pytest.fixture(autouse=True)
def patch_parser(monkeypatch):
    # replace PDF→images with a single blank page
    monkeypatch.setattr(PIDParser, "_pdf_to_images", lambda self: [np.zeros((100,100,3), dtype=np.uint8)])
    # inject dummy model so no real YOLO runs
    monkeypatch.setattr(PIDParser, "model", DummyModel())
    yield

def test_parse_returns_empty_list_when_no_boxes():
    parser = PIDParser(pdf_path=None)  # path is ignored by our patch
    comps = parser.parse()
    assert isinstance(comps, list)
    assert comps == []
