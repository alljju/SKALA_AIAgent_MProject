"""Derive a recommended entry path per country from strategy candidates."""
from __future__ import annotations

from typing import Any, Dict, List

MODE_LABELS = {
    "direct_investment": "\uc9c1\uc811 \ud22c\uc790",
    "joint_venture": "\uc870\uc778\ud2b8 \ubca4\ucc98",
    "licensing": "\ub77c\uc774\uc120\uc2a4",
    "mna": "\uc778\uc218\ud569\ubcd1",
    "additional_research": "\ucd94\uac00 \uc870\uc0ac \ud544\uc694",
}


def _compose_rationale(country: str, market: Dict[str, Any], barriers: Dict[str, Any], evidence_count: int) -> List[str]:
    rationale = [
        f"\uac80\ud1a0 \uad6d\uac00: {country}",
        f"\uc218\uc9d1\ub41c \uadfc\uac70: {evidence_count}\uac74",
    ]
    cagr = market.get("cagr_pct")
    if cagr is not None:
        rationale.append(f"\ubcf4\uace0\ub41c CAGR: {cagr}%")
    fdi = barriers.get("fdi_restriction") if isinstance(barriers, dict) else None
    if fdi:
        rationale.append(f"FDI \uc81c\ud55c \uc218\uc900: {fdi}")
    data_loc = barriers.get("data_localization") if isinstance(barriers, dict) else None
    if data_loc:
        rationale.append(f"\ub370\uc774\ud130 \ud604\uc9c0\ud654 \uc694\uad6c \uc218\uc900: {data_loc}")
    if len(rationale) < 3:
        rationale.append("\ud30c\ud2b8\ub108 \ud658\uacbd \uac80\uc99d\uc744 \uc704\ud55c \ucd94\uac00 \uc870\uc0ac\uac00 \uad8c\uc7a5\ub429\ub2c8\ub2e4.")
    return rationale


def decision_flow_controller(state: Dict[str, Any]) -> Dict[str, Any]:
    """Pick the highest-fit entry mode and prepare rationale bullets."""
    strategies = state.get("strategies", {})
    market = state.get("market", {})
    min_evidence = state.get("rules", {}).get("min_evidence", 0)
    decisions: Dict[str, Any] = {}
    shortages: List[str] = []

    for country in state.get("countries", []):
        candidates = strategies.get(country, {}).get("candidates", [])
        best = max(candidates, key=lambda item: item.get("fit", 0)) if candidates else {}
        recommended = best.get("mode", "additional_research")
        score = round(float(best.get("fit", 0.0)), 2)

        market_overview = market.get(country, {}).get("market_overview", {})
        barriers = market.get(country, {}).get("barriers", {})
        evidence_count = len(market.get(country, {}).get("evidence", []))
        if evidence_count < min_evidence:
            shortages.append(country)

        rationale = _compose_rationale(country, market_overview, barriers, evidence_count)
        decisions[country] = {
            "recommended": recommended,
            "recommended_label": MODE_LABELS.get(recommended, recommended),
            "score": score,
            "rationale": rationale,
        }

    payload: Dict[str, Any] = {"decision": decisions}
    if shortages and not state.get("_retry_performed"):
        payload["retry_countries"] = shortages
        payload["trigger_retry"] = True
    return payload
