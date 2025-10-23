"""Helpers for loading logistics reference documents."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    from PyPDF2 import PdfReader  # type: ignore
except ImportError:  # pragma: no cover
    PdfReader = None  # type: ignore


DEFAULT_MAX_CHARS = 8000
REFERENCE_DIR = Path(__file__).resolve().parents[1] / "data" / "reference" / "logistics_glossary"


def _ensure_reference_dir() -> Path:
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    return REFERENCE_DIR


def _read_pdf(path: Path) -> str:
    if not PdfReader:
        return ""
    try:
        reader = PdfReader(str(path))
        texts = []
        for page in reader.pages:
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                continue
        return "\n".join(texts)
    except Exception:
        return ""


def load_logistics_glossary(max_chars: int = DEFAULT_MAX_CHARS) -> str:
    """Load and concatenate reference glossary text from PDFs."""
    reference_path = _ensure_reference_dir()
    texts = []
    for pdf in sorted(reference_path.glob("*.pdf")):
        text = _read_pdf(pdf)
        if text:
            texts.append(text)
    combined = "\n".join(texts).strip()
    if not combined:
        return ""
    return combined[:max_chars]
