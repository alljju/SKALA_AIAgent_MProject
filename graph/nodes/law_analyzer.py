"""Node responsible for collecting regulatory evidence."""
from __future__ import annotations

from typing import Any, Dict

from tools.parsing import extract_barrier_evidence
from tools.web_search import search_pages

LAW_PROMPT_NAME = "law_guideline.md"


async def law_analyzer(state: Dict[str, Any]) -> Dict[str, Any]:
    """Gather regulatory constraints for each country via web search stubs."""
    countries = state.get("countries", [])
    segment = state.get("segment", "")
    results: Dict[str, Any] = {}

    for country in countries:
        query = f"{country} {segment} foreign investment restriction data localization tax labor permit"
        pages = await search_pages(query=query, k=8)
        barriers, evidence = extract_barrier_evidence(pages, prompt=LAW_PROMPT_NAME)
        results[country] = {"barriers": barriers, "evidence": evidence}

    interim = dict(state.get("interim", {}))
    interim["law"] = results
    return {"interim": interim}
