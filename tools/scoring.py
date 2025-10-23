"""Scoring utilities for country attractiveness and entry strategies."""
from __future__ import annotations

from typing import Any, Dict, List


def score_country(barriers: Dict[str, Any], market: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, float]:
    """Compute simple attractiveness and risk scores."""
    w_cagr = 0.4
    w_market = 0.3
    w_barrier = 0.3

    cagr = (market.get("cagr_pct") or 0.0) / 100.0
    size = market.get("market_size_usd") or market.get("size_usd") or 0.0
    size_norm = min(float(size) / 1_000_000_000, 1.0) if size else 0.0

    fdi_level = (barriers or {}).get("fdi_restriction") or "low"
    penalty = {"high": 0.3, "medium": 0.15}.get(str(fdi_level).lower(), 0.0)

    attractiveness = max(0.0, (w_cagr * cagr) + (w_market * size_norm) - (w_barrier * penalty))
    risk = min(1.0, penalty + (0.1 if len(competitors) > 5 else 0.0))
    return {
        "attractiveness": round(attractiveness * 100, 1),
        "risk": round(risk * 100, 1),
    }


def _clamp(score: float) -> float:
    return max(0.0, min(100.0, score))


def score_entry_modes(barriers: Dict[str, Any], market: Dict[str, Any], firm: Dict[str, Any], rules: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    """Produce fit scores (0-100) for core entry modes based on heuristics."""
    rules = rules or {}
    cagr = float(market.get("cagr_pct") or 0.0)
    cagr_good = float(rules.get("cagr_good", 8.0))
    fdi = str((barriers or {}).get("fdi_restriction") or "low").lower()
    data_localization = str((barriers or {}).get("data_localization") or "none").lower()
    other = " ".join((barriers or {}).get("other", [])).lower()

    control_pref = str(firm.get("control_pref", "medium")).lower()
    risk_appetite = str(firm.get("risk_appetite", "medium")).lower()

    modes: List[Dict[str, Any]] = []

    # Direct Investment
    direct_score = 55.0
    direct_pros: List[str] = []
    direct_cons: List[str] = []
    if control_pref == "high":
        direct_score += 15
        direct_pros.append("Matches high control preference")
    if cagr >= cagr_good:
        direct_score += 10
        direct_pros.append("Growth outlook supports wholly-owned expansion")
    if fdi in {"high", "medium"}:
        penalty = 20 if fdi == "high" else 10
        direct_score -= penalty
        direct_cons.append(f"FDI restriction level {fdi} limits equity ownership")
    if "equity cap" in other:
        direct_score -= 10
        direct_cons.append("Equity cap barriers reduce feasibility")
    if data_localization in {"broad", "sectoral"}:
        direct_score -= 5
        direct_cons.append("Data localization requirements raise compliance cost")
    modes.append({"mode": "direct_investment", "fit": _clamp(direct_score), "pros": direct_pros, "cons": direct_cons})

    # Joint Venture
    jv_score = 60.0
    jv_pros: List[str] = []
    jv_cons: List[str] = []
    if fdi in {"high", "medium"} or "equity cap" in other:
        jv_score += 10
        jv_pros.append("Local partner mitigates equity restrictions")
    if risk_appetite == "low":
        jv_score += 5
        jv_pros.append("Shares investment risk with local partner")
    if data_localization == "none":
        jv_score -= 5
        jv_cons.append("May not be necessary if regulatory friction is low")
    modes.append({"mode": "joint_venture", "fit": _clamp(jv_score), "pros": jv_pros, "cons": jv_cons})

    # Licensing
    licensing_score = 50.0
    licensing_pros: List[str] = []
    licensing_cons: List[str] = []
    if risk_appetite == "low":
        licensing_score += 10
        licensing_pros.append("Low capital exposure aligns with conservative stance")
    if control_pref == "high":
        licensing_score -= 10
        licensing_cons.append("Limited control conflicts with preference")
    if cagr >= cagr_good:
        licensing_cons.append("High growth may warrant more control than licensing provides")
    modes.append({"mode": "licensing", "fit": _clamp(licensing_score), "pros": licensing_pros, "cons": licensing_cons})

    # M&A
    mna_score = 55.0
    mna_pros: List[str] = []
    mna_cons: List[str] = []
    if cagr >= cagr_good:
        mna_score += 5
        mna_pros.append("Acquiring scale accelerates capture of fast growth")
    if risk_appetite == "high":
        mna_score += 10
        mna_pros.append("High risk appetite supports acquisition strategy")
    if "foreign ownership ban" in other:
        mna_score -= 15
        mna_cons.append("Foreign ownership restrictions complicate acquisitions")
    modes.append({"mode": "mna", "fit": _clamp(mna_score), "pros": mna_pros, "cons": mna_cons})

    return modes
