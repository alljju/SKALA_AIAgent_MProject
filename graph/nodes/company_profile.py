"""Derive company-specific insights and context."""
from __future__ import annotations

from typing import Any, Dict

from tools.company_profile import build_company_profile


async def company_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch and summarise company information, merging back into state."""
    company_state = dict(state.get("company", {}))
    firm_state = dict(state.get("firm", {}))

    name = (
        company_state.get("name")
        or firm_state.get("name")
        or state.get("company_name")
        or "Target Company"
    )
    url = company_state.get("url") or firm_state.get("url")
    notes = company_state.get("notes") or firm_state.get("notes")

    profile = await build_company_profile(name=name, url=url, notes=notes)

    company_state.update(profile)
    firm_state.setdefault("name", profile.get("name", name))
    if profile.get("headline") and "headline" not in firm_state:
        firm_state["headline"] = profile["headline"]
    if profile.get("url") and "url" not in firm_state:
        firm_state["url"] = profile["url"]
    if profile.get("notes") and "notes" not in firm_state:
        firm_state["notes"] = profile["notes"]

    return {
        "company": company_state,
        "firm": firm_state,
    }
