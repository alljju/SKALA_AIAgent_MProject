"""Typed Dict schemas describing the agent state containers."""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict


EntryBarrier = TypedDict(
    "EntryBarrier",
    {
        "fdi_restriction": Optional[str],
        "data_localization": Optional[str],
        "tax_regime": Optional[Dict[str, Any]],
        "labor_regulation": Optional[Dict[str, Any]],
        "other": Optional[List[str]],
    },
)


MarketFacts = TypedDict(
    "MarketFacts",
    {
        "segment": str,
        "market_size_usd": Optional[float],
        "cagr_pct": Optional[float],
        "period": Optional[str],
        "aux_indicators": Dict[str, float],
    },
)


Competitor = TypedDict(
    "Competitor",
    {
        "name": str,
        "share_pct": Optional[float],
        "notes": Optional[str],
        "source_url": Optional[str],
    },
)


Evidence = TypedDict(
    "Evidence",
    {
        "fact": str,
        "source_url": str,
    },
)


InsightLayer = TypedDict(
    "InsightLayer",
    {
        "country": str,
        "barriers": EntryBarrier,
        "market": MarketFacts,
        "competition": List[Competitor],
        "scores": Dict[str, float],
        "evidence": List[Evidence],
    },
)


CompanyProfile = TypedDict(
    "CompanyProfile",
    {
        "name": str,
        "url": Optional[str],
        "headline": Optional[str],
        "description": Optional[str],
        "offerings": List[str],
        "differentiators": List[str],
        "target_segments": List[str],
        "expansion_risks": List[str],
        "notes": Optional[str],
        "raw_excerpt": Optional[str],
    },
    total=False,
)


class State(TypedDict, total=False):
    """State shared across the insight LangGraph pipeline."""

    countries: List[str]
    segment: str
    language: Literal["ko", "en"]
    interim: Dict[str, Any]
    insights: List[InsightLayer]
    company: CompanyProfile
    references: Dict[str, Any]


class FirmProfile(TypedDict, total=False):
    capital_usd: Optional[float]
    control_pref: Literal["high", "medium", "low"]
    speed_priority: Literal["high", "medium", "low"]
    risk_appetite: Literal["high", "medium", "low"]
    tech_assets: List[str]


class RuleThresholds(TypedDict, total=False):
    min_evidence: int
    cagr_good: float
    barrier_high: List[str]


class ReportState(TypedDict, total=False):
    """Extended state for the multi-agent strategy report pipeline."""

    countries: List[str]
    segment: str
    language: Literal["ko", "en"]
    firm: FirmProfile
    rules: RuleThresholds
    company: CompanyProfile
    references: Dict[str, Any]
    market: Dict[str, Any]
    competition: Dict[str, Any]
    barriers: Dict[str, Any]
    strategies: Dict[str, Any]
    partners: Dict[str, Any]
    decision: Dict[str, Any]
    report: Dict[str, Any]
