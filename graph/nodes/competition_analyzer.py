"""Node collecting competitor and market share insights."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from tools.parsing import extract_competitors
from tools.web_search import search_pages


async def competition_analyzer(state: Dict[str, Any]) -> Dict[str, Any]:
    """Identify major competitors and supporting evidence per country."""
    segment = state.get("segment", "")
    results: Dict[str, Any] = {}
    competition_entries: Dict[str, Any] = {}

    for country in state.get("countries", []):
        query = f"{country} {segment} top companies market share"
        pages = await search_pages(query=query, k=6)
        competitors, evidence = extract_competitors(pages)
        payload = {
            "players": deepcopy(competitors),
            "competitors": competitors,
            "evidence": evidence,
        }
        competition_entries[country] = payload
        results[country] = {"competitors": competitors, "evidence": evidence}

    updates: Dict[str, Any] = {"competition": competition_entries}
    if "interim" in state:
        interim = dict(state.get("interim") or {})
        interim["competition"] = results
        updates["interim"] = interim
    return updates
