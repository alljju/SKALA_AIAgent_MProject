"""Thin wrapper for external web-search providers (e.g., Tavily)."""
from __future__ import annotations

import os
from typing import Any, Dict, List

import httpx

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SEARCH_ENDPOINT = os.getenv("TAVILY_ENDPOINT", "https://api.tavily.com/search")
DEFAULT_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", 25))


async def search_pages(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Return a list of search results, or an empty collection if disabled."""
    if not TAVILY_API_KEY:
        return []

    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": k,
    }

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.post(SEARCH_ENDPOINT, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError:
        return []
    return data.get("results", [])
