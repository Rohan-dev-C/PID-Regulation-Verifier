"""
Very small NLP helpers – we try spaCy, fall back to regex.
"""
from __future__ import annotations

from typing import List
import re

try:
    import spacy

    _nlp = spacy.load("en_core_web_sm")  
except Exception: 
    _nlp = None


def sent_tokenize(text: str) -> List[str]:
    """Return a list of sentences."""
    if _nlp:
        doc = _nlp(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    return [s.strip() for s in re.split(r"[.!?]\s+", text) if s.strip()]
