"""Data fetchers for macro indicators and market intelligence."""
from __future__ import annotations

from typing import Any, Dict, List

from tools.sources.worldbank import get_macro
from tools.web_search import search_pages

OFFICIAL_FILTERS = [
    "site:.gov",
    "site:.go.kr",
    "site:.europa.eu",
    "site:worldbank.org",
    "site:oecd.org",
    "site:imf.org",
    "site:adb.org",
    "site:wto.org",
    "site:un.org",
]


async def fetch_worldbank_macro(country: str) -> Dict[str, float]:
    """Return macro indicators sourced from the World Bank API."""
    return await get_macro(country)


async def fetch_market_reports(
    country: str,
    segment: str,
    *,
    prefer_official: bool = True,
    max_results: int = 12,
) -> List[Dict[str, Any]]:
    """Query web sources for market reports, prioritising official datasets when possible."""
    results: List[Dict[str, Any]] = []
    queries: List[str] = []

    segment_clause = f"{segment} market size CAGR"

    if prefer_official:
        for filter_clause in OFFICIAL_FILTERS:
            queries.append(f"{country} {segment_clause} {filter_clause}")

    queries.append(f"{country} {segment_clause} 2024 report")
    queries.append(f"{country} {segment_clause} analysis")

    for query in queries:
        pages = await search_pages(query=query, k=min(6, max_results))
        if not pages:
            continue
        for page in pages:
            page.setdefault("query", query)
        results.extend(pages)
        if len(results) >= max_results:
            break

    return results[:max_results]
