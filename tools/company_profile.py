"""Utilities for extracting and summarising company information."""
from __future__ import annotations

import json
import os
from typing import Dict, Optional

import httpx
from bs4 import BeautifulSoup

from tools.llm import complete_markdown

DEFAULT_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", 20))
MAX_CHARS = 4000


def _extract_text(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(soup.stripped_strings)
    return text[:MAX_CHARS]


async def _fetch_page(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except httpx.HTTPError:
        return ""


def _summarise_with_llm(name: str, notes: Optional[str], raw_text: str) -> Dict[str, any]:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("LLM disabled")

    prompt = f"""
You are a strategy analyst preparing a company brief for market-entry planning.
Return ONLY valid JSON with the following keys: name, headline, description, offerings, differentiators,
target_segments, expansion_risks, notes. Lists should contain strings. Use "N/A" or an empty list when
information is missing.

[Company Name]
{name}

[Site/Text Extract]
{raw_text or "N/A"}

[Additional Notes]
{notes or "N/A"}
"""
    completion = complete_markdown(prompt, system="Produce clean JSON for strategy teams.")
    json_text = completion.strip()
    start = json_text.find("{")
    end = json_text.rfind("}")
    if start != -1 and end != -1:
        json_text = json_text[start : end + 1]
    return json.loads(json_text)


def _fallback_profile(name: str, notes: Optional[str], raw_text: str) -> Dict[str, any]:
    return {
        "name": name,
        "headline": "N/A",
        "description": raw_text[:400] or "Additional qualitative analysis required.",
        "offerings": [],
        "differentiators": [],
        "target_segments": [],
        "expansion_risks": [],
        "notes": notes or "",
    }


async def build_company_profile(
    name: str,
    url: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, any]:
    """Fetch and summarise company information from the provided URL/notes."""
    html = ""
    if url:
        html = await _fetch_page(url)
    raw_text = _extract_text(html)

    try:
        profile = _summarise_with_llm(name, notes, raw_text)
    except Exception:
        profile = _fallback_profile(name, notes, raw_text)

    profile["name"] = profile.get("name") or name
    if url:
        profile["url"] = url
    if notes:
        profile["notes"] = notes
    profile["raw_excerpt"] = raw_text[:1000] if raw_text else ""
    return profile
