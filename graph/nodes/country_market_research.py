"""Collect market overviews, regulatory snippets, and evidence per country."""
from __future__ import annotations

from typing import Any, Dict

from tools.fetchers import fetch_market_reports
from tools.parsing import compute_gdp_proxy, extract_barrier_evidence, extract_market_numbers
from tools.sources.worldbank import get_macro

LAW_PROMPT = "law_guideline.md"


async def country_market_research(state: Dict[str, Any]) -> Dict[str, Any]:
    """Populate the extended report state with market snapshots."""
    countries = state.get("countries", [])
    segment = state.get("segment", "")
    min_evidence = state.get("rules", {}).get("min_evidence", 0)
    market_payload: Dict[str, Any] = {}

    for country in countries:
        macro = await get_macro(country)
        reports = await fetch_market_reports(
            country,
            segment,
            prefer_official=True,
            max_results=max(8, min_evidence or 0),
        )
        size, cagr, period, market_evidence = extract_market_numbers(reports)
        barriers, barrier_evidence = extract_barrier_evidence(reports, prompt=LAW_PROMPT)

        proxy = compute_gdp_proxy(macro, segment)
        proxy_note = None
        if size is None and proxy.get("market_size_usd") is not None:
            size = proxy["market_size_usd"]
            market_evidence.append(
                {
                    "fact": f"GDP \ucd94\uc815 \ube44\uc728 \uae30\ubc18 \uc2dc\uc7a5\uaddc\ubaa0 \ud504\ub85d\uc2dc: {proxy['note']}",
                    "source_url": proxy.get("source", ""),
                }
            )
            proxy_note = proxy.get("note")
        if cagr is None and proxy.get("cagr_pct") is not None:
            cagr = proxy["cagr_pct"]
            market_evidence.append(
                {
                    "fact": f"GDP \uae30\ubc18 \ucd94\uc815 \uc131\uc7a5\ub960 \uc801\uc6a9: {cagr}%",
                    "source_url": proxy.get("source", ""),
                }
            )

        market_payload[country] = {
            "market_overview": {
                "segment": segment,
                "size_usd": size,
                "cagr_pct": cagr,
                "period": period,
                "trend": [],
                "macro": macro,
                "proxy_note": proxy_note,
            },
            "barriers": barriers,
            "evidence": market_evidence + barrier_evidence,
        }

    return {"market": market_payload}
