"""Node collating market size and growth figures."""
from __future__ import annotations

from typing import Any, Dict

from tools.fetchers import fetch_market_reports, fetch_worldbank_macro
from tools.parsing import compute_gdp_proxy, extract_market_numbers


async def market_analyzer(state: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch macro indicators and market metrics for each country."""
    countries = state.get("countries", [])
    segment = state.get("segment", "")
    results: Dict[str, Any] = {}

    for country in countries:
        wb_indicators = await fetch_worldbank_macro(country)
        reports = await fetch_market_reports(country, segment, prefer_official=True)
        size, cagr, period, evidence = extract_market_numbers(reports)

        proxy = compute_gdp_proxy(wb_indicators, segment)
        proxy_used = False
        if size is None and proxy.get("market_size_usd") is not None:
            size = proxy["market_size_usd"]
            evidence.append(
                {
                    "fact": f"GDP \ub300\ube44 \ucd94\uc815 \ube44\uc728\uc744 \ud65c\uc6a9\ud55c \uc2dc\uc7a5\uaddc\ubaa8 \ud504\ub85d\uc2dc: {proxy['note']}",
                    "source_url": proxy.get("source", ""),
                }
            )
            proxy_used = True

        if cagr is None and proxy.get("cagr_pct") is not None:
            cagr = proxy["cagr_pct"]
            if not proxy_used:
                evidence.append(
                    {
                        "fact": f"GDP \uae30\ubc18 \ucd94\uc815 \uc131\uc7a5\ub960 \uc801\uc6a9: {cagr}%",
                        "source_url": proxy.get("source", ""),
                    }
                )

        results[country] = {
            "market": {
                "segment": segment,
                "market_size_usd": size,
                "cagr_pct": cagr,
                "period": period,
                "aux_indicators": wb_indicators,
                "proxy_note": proxy.get("note") if proxy_used else None,
            },
            "evidence": evidence,
        }

    interim = dict(state.get("interim", {}))
    interim["market"] = results
    return {"interim": interim}
