"""Utility helpers for parsing textual market intelligence."""
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

USD_PATTERN = re.compile(r"\$?\s*([\d,.]+)\s*(trillion|billion|million|tn|bn|m|k)?", re.IGNORECASE)
CAGR_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*%\s*(?:CAGR)?", re.IGNORECASE)
PERIOD_PATTERN = re.compile(r"(20\d{2})\D+(20\d{2})")


def _normalize_usd(value: str, multiplier: Optional[str]) -> Optional[float]:
    try:
        numeric = float(value.replace(",", ""))
    except ValueError:
        return None
    scale = 1.0
    if multiplier:
        token = multiplier.lower()
        if token in {"trillion", "tn"}:
            scale = 1_000_000_000_000
        if token in {"billion", "bn"}:
            scale = 1_000_000_000
        elif token in {"million", "m"}:
            scale = 1_000_000
        elif token == "k":
            scale = 1_000
    return numeric * scale


def extract_numbers(text: str) -> Dict[str, Optional[Any]]:
    """Extract USD market size, CAGR percentage, and period from raw text."""
    usd_value: Optional[float] = None
    cagr_value: Optional[float] = None
    period_value: Optional[str] = None

    usd_matches = list(USD_PATTERN.finditer(text))
    if usd_matches:
        for match in usd_matches:
            candidate = _normalize_usd(match.group(1), match.group(2))
            if candidate:
                if usd_value is None or candidate > usd_value:
                    usd_value = candidate

    cagr_matches = list(CAGR_PATTERN.finditer(text))
    if cagr_matches:
        try:
            for match in cagr_matches:
                value = float(match.group(1))
                if cagr_value is None or value > cagr_value:
                    cagr_value = value
        except ValueError:
            cagr_value = None

    period_match = PERIOD_PATTERN.search(text)
    if period_match:
        start, end = period_match.groups()
        period_value = f"{start}-{end}"

    return {"usd": usd_value, "cagr_pct": cagr_value, "period": period_value}


def extract_barrier_evidence(pages: Iterable[Dict[str, Any]], prompt: str) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
    """Transform raw search results into structured barrier hints."""
    barriers = {
        "fdi_restriction": None,
        "data_localization": None,
        "tax_regime": {},
        "labor_regulation": {},
        "other": [],
    }
    evidence: List[Dict[str, str]] = []

    for page in pages or []:
        url = page.get("url") or page.get("source") or ""
        summary = page.get("content") or page.get("snippet") or page.get("title") or ""
        if not summary:
            continue
        evidence.append({"fact": summary[:220], "source_url": url})

    return barriers, evidence


def extract_market_numbers(reports: Iterable[Dict[str, Any]]) -> Tuple[Optional[float], Optional[float], Optional[str], List[Dict[str, str]]]:
    """Parse market size, CAGR, and period from a list of documents."""
    market_size: Optional[float] = None
    cagr: Optional[float] = None
    period: Optional[str] = None
    evidence: List[Dict[str, str]] = []

    for report in reports or []:
        text = " ".join(
            str(report.get(key, ""))
            for key in ("content", "summary", "snippet", "title")
        )
        numbers = extract_numbers(text)
        usd_candidate = numbers.get("usd")
        if usd_candidate is not None:
            if market_size is None or usd_candidate > market_size:
                market_size = usd_candidate
        cagr_candidate = numbers.get("cagr_pct")
        if cagr_candidate is not None:
            if cagr is None or cagr_candidate > cagr:
                cagr = cagr_candidate
        period = period or numbers.get("period")
        url = report.get("url") or report.get("source")
        if url and text:
            evidence.append({"fact": text[:220], "source_url": url})

    return market_size, cagr, period, evidence


def extract_competitors(pages: Iterable[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """Derive a basic competitor list and supporting evidence."""
    competitors: List[Dict[str, Any]] = []
    evidence: List[Dict[str, str]] = []

    for page in pages or []:
        title = page.get("title", "")
        url = page.get("url") or page.get("source") or ""
        if title:
            competitors.append({"name": title, "share_pct": None, "notes": page.get("snippet"), "source_url": url})
        snippet = page.get("snippet") or page.get("content")
        if snippet:
            evidence.append({"fact": snippet[:220], "source_url": url})

    return competitors, evidence


SEGMENT_GDP_RATIOS = {
    "logistics": 0.022,
    "ecommerce": 0.035,
    "healthcare": 0.08,
    "energy": 0.07,
    "manufacturing": 0.12,
    "agriculture": 0.04,
}

SEGMENT_DEFAULT_CAGR = {
    "logistics": 6.5,
    "ecommerce": 10.0,
    "healthcare": 7.2,
    "energy": 4.5,
    "manufacturing": 5.0,
    "agriculture": 3.8,
}


def compute_gdp_proxy(macro: Dict[str, Any], segment: str) -> Dict[str, Any]:
    """Estimate market size and growth using GDP-based heuristics."""
    gdp_bil = macro.get("gdp_usd_bil")
    if not gdp_bil:
        return {}

    normalized = segment.lower()
    ratio = None
    for key, value in SEGMENT_GDP_RATIOS.items():
        if key in normalized:
            ratio = value
            break
    ratio = ratio or 0.03

    cagr = None
    for key, value in SEGMENT_DEFAULT_CAGR.items():
        if key in normalized:
            cagr = value
            break
    cagr = cagr or 5.0

    size = gdp_bil * 1_000_000_000 * ratio
    note = f"GDP \ub300\ube44 {ratio*100:.1f}% \ube44\uc728\uc744 \uc801\uc6a9\ud55c \ucd94\uc815\uce58"

    return {
        "market_size_usd": size,
        "cagr_pct": cagr,
        "note": note,
        "source": "proxy:gdp_ratio",
    }
