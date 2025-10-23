"""Identify potential local partners and advisors."""
from __future__ import annotations

from typing import Any, Dict

from tools.web_search import search_pages


async def partner_sourcing(state: Dict[str, Any]) -> Dict[str, Any]:
    """Return placeholder partner suggestions for each country."""
    segment = state.get("segment", "")
    partners: Dict[str, Any] = {}

    for country in state.get("countries", []):
        query = f"{country} {segment} logistics partners investor consulting"
        pages = await search_pages(query=query, k=5)
        evidence = []
        for page in pages:
            evidence.append(
                {
                    "fact": (page.get("snippet") or page.get("title") or "")[:200],
                    "source_url": page.get("url") or page.get("source") or "",
                }
            )
        partners[country] = {
            "local_firms": [],
            "investors": [],
            "consultants": [],
            "evidence": evidence,
        }

    return {"partners": partners}
