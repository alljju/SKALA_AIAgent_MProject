"""Compute initial entry mode suitability scores."""
from __future__ import annotations

from typing import Any, Dict

from tools.scoring import score_entry_modes


def entry_strategy(state: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate entry mode candidates using parsed market intelligence."""
    strategies: Dict[str, Any] = {}
    market = state.get("market", {})
    competition = state.get("competition", {})
    firm = state.get("firm", {})
    rules = state.get("rules", {})

    for country in state.get("countries", []):
        country_market = market.get(country, {}).get("market_overview", {})
        barriers = market.get(country, {}).get("barriers", {})
        players = competition.get(country, {}).get("players", [])

        scored_modes = score_entry_modes(barriers, country_market, firm, rules)
        strategies[country] = {
            "candidates": scored_modes,
            "context": {
                "players": players,
                "market": country_market,
            },
        }

    return {"strategies": strategies}
