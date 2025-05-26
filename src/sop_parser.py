"""
Extract component & step information from an SOP .docx.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

from docx import Document

from .config import settings
from .utils import sent_tokenize

LOGGER = logging.getLogger(__name__)


class SOPParser:
    def __init__(self, sop_path: Path | str | None = None) -> None:
        self.sop_path = Path(sop_path or settings.sop_path)

    # ---------------------------------------------------------------- public
    def parse(self) -> Dict[str, List[str]]:
        """
        Returns a dict:
            { step_id: [list_of_required_component_labels] }
        """
        LOGGER.info("Parsing SOP %s", self.sop_path)
        doc = Document(str(self.sop_path))
        comp_by_step: Dict[str, List[str]] = {}

        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if not text:
                continue
            # naïve: each paragraph = one step
            step_id = f"step_{i}"
            sentences = sent_tokenize(text)
            comps = [
                tok
                for sent in sentences
                for tok in sent.split()
                if tok.isupper() and len(tok) > 1  # heuristic: component labels are ALLCAPS
            ]
            comp_by_step[step_id] = comps
            LOGGER.debug("SOP %s → %s", step_id, comps)
        LOGGER.info("Extracted %d SOP steps", len(comp_by_step))
        return comp_by_step
