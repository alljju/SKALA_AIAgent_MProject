"""Combine interim artifacts into the final insight layer."""
from __future__ import annotations

from typing import Any, Dict, List

from tools.scoring import score_country


def _collect_evidence(*chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    evidence: List[Dict[str, Any]] = []
    for chunk in chunks:
        if not chunk:
            continue
        evidence.extend(chunk)
    return evidence


def insight_integrator(state: Dict[str, Any]) -> Dict[str, Any]:
    """Integrate market, competition, and barrier data into insights."""
    countries = state.get("countries", [])
    interim = state.get("interim", {})
    market = interim.get("market", {})
    competition = interim.get("competition", {})
    barriers = interim.get("barriers", {})

    insights = []
    for country in countries:
        market_payload = market.get(country, {})
        competition_payload = competition.get(country, {})
        barrier_payload = barriers.get(country, {})
        law_payload = interim.get("law", {}).get(country, {})

        scores = score_country(
            barrier_payload,
            market_payload.get("market", {}),
            competition_payload.get("competitors", []),
        )
        evidence = _collect_evidence(
            market_payload.get("evidence", []),
            competition_payload.get("evidence", []),
            law_payload.get("evidence", []),
        )
        insights.append(
            {
                "country": country,
                "barriers": barrier_payload,
                "market": market_payload.get("market", {}),
                "competition": competition_payload.get("competitors", []),
                "scores": scores,
                "evidence": evidence,
            }
        )

    return {"insights": insights}
