"""World Bank API client for macro indicators with simple caching."""
from __future__ import annotations

import asyncio
from typing import Any, Dict

import httpx

TIMEOUT = float(25)
BASE_URL = "https://api.worldbank.org/v2/country/{code}/indicator/{indicator}"
INDICATORS = {
    "gdp_usd_bil": "NY.GDP.MKTP.CD",
    "population_m": "SP.POP.TOTL",
    "internet_users_pct": "IT.NET.USER.ZS",
}

_COUNTRY_ALIASES = {
    "united states": "USA",
    "united states of america": "USA",
    "south korea": "KOR",
    "korea, republic of": "KOR",
    "mongolia": "MNG",
}
_CACHE: Dict[str, Dict[str, float]] = {}
_CACHE_LOCK = asyncio.Lock()


def _resolve_country_code(country: str) -> str:
    key = country.strip().lower()
    if key in _COUNTRY_ALIASES:
        return _COUNTRY_ALIASES[key]
    letters = [ch for ch in key.upper() if ch.isalpha()]
    return "".join(letters[:3]).ljust(3, "X")


async def _fetch_indicator(client: httpx.AsyncClient, code: str, indicator: str) -> float:
    params = {"format": "json", "per_page": 5, "MRV": 1}
    url = BASE_URL.format(code=code, indicator=indicator)
    resp = await client.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    try:
        value = data[1][0]["value"]
    except (IndexError, KeyError, TypeError):
        return 0.0
    return float(value) if value is not None else 0.0


async def get_macro(country: str) -> Dict[str, float]:
    """Fetch GDP, population, and internet penetration for a country."""
    code = _resolve_country_code(country)
    async with _CACHE_LOCK:
        if code in _CACHE:
            return _CACHE[code]

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        results: Dict[str, float] = {}
        for key, indicator in INDICATORS.items():
            try:
                value = await _fetch_indicator(client, code, indicator)
            except httpx.HTTPError:
                value = 0.0
            if key == "gdp_usd_bil":
                value /= 1_000_000_000  # convert to billions
            if key == "population_m":
                value /= 1_000_000
            results[key] = round(value, 4)

    async with _CACHE_LOCK:
        _CACHE[code] = results
    return results
