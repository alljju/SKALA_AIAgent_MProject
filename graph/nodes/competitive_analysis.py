"""Multi-agent competitive landscape collector."""
from __future__ import annotations

from typing import Any, Dict

from tools.parsing import extract_competitors
from tools.web_search import search_pages


async def competitive_analysis(state: Dict[str, Any]) -> Dict[str, Any]:
    """Aggregate competitor profiles for the extended report."""
    segment = state.get("segment", "")
    results: Dict[str, Any] = {}

    for country in state.get("countries", []):
        query = f"{country} {segment} leading companies market share strategy"
        pages = await search_pages(query=query, k=6)
        players, evidence = extract_competitors(pages)
        structure = "concentrated" if len(players) <= 5 else "fragmented"
        results[country] = {
            "players": players,
            "structure": structure,
            "evidence": evidence,
        }

    return {"competition": results}
