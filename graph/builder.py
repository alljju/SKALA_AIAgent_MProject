"""LangGraph builders wiring the agent nodes."""
from __future__ import annotations

from typing import Any, Callable

from langgraph.graph import StateGraph

from graph.state import ReportState, State
from graph.logging_utils import log_node_io
from graph.nodes.barrier_extractor import barrier_extractor
from graph.nodes.company_profile import company_profile
from graph.nodes.competition_analyzer import competition_analyzer
from graph.nodes.country_market_research import country_market_research
from graph.nodes.decision_flow_controller import decision_flow_controller
from graph.nodes.entry_strategy import entry_strategy
from graph.nodes.insight_integrator import insight_integrator
from graph.nodes.law_analyzer import law_analyzer
from graph.nodes.market_analyzer import market_analyzer
from graph.nodes.partner_sourcing import partner_sourcing
from graph.nodes.reference_loader import reference_loader
from graph.nodes.report_writer import report_writer


def _instrument(node_name: str, func: Callable[..., Any]) -> Callable[..., Any]:
    """Attach structured execution logging to a node."""
    return log_node_io(node_name)(func)


def build_graph() -> StateGraph:
    """Create the base pipeline graph for market insights."""
    graph = StateGraph(State)
    graph.add_node("company_loader", _instrument("company_loader", company_profile))
    graph.add_node("reference_loader", _instrument("reference_loader", reference_loader))
    graph.add_node("law_analysis", _instrument("law_analysis", law_analyzer))
    graph.add_node("market_analysis", _instrument("market_analysis", market_analyzer))
    graph.add_node("competition_analysis", _instrument("competition_analysis", competition_analyzer))
    graph.add_node("barrier_normalizer", _instrument("barrier_normalizer", barrier_extractor))
    graph.add_node("insight_aggregator", _instrument("insight_aggregator", insight_integrator))

    graph.set_entry_point("company_loader")
    graph.add_edge("company_loader", "reference_loader")
    graph.add_edge("reference_loader", "law_analysis")
    graph.add_edge("law_analysis", "market_analysis")
    graph.add_edge("market_analysis", "competition_analysis")
    graph.add_edge("competition_analysis", "barrier_normalizer")
    graph.add_edge("barrier_normalizer", "insight_aggregator")
    graph.set_finish_point("insight_aggregator")
    return graph


def build_report_graph() -> StateGraph:
    """Create the extended multi-agent graph for strategy reporting."""
    graph = StateGraph(ReportState)
    graph.add_node("company_loader", _instrument("company_loader", company_profile))
    graph.add_node("reference_loader", _instrument("reference_loader", reference_loader))
    graph.add_node("market_assessment", _instrument("market_assessment", country_market_research))
    graph.add_node("competition_assessment", _instrument("competition_assessment", competition_analyzer))
    graph.add_node("strategy_planner", _instrument("strategy_planner", entry_strategy))
    graph.add_node("partner_mapper", _instrument("partner_mapper", partner_sourcing))
    graph.add_node("decision_router", _instrument("decision_router", decision_flow_controller))
    graph.add_node("report_builder", _instrument("report_builder", report_writer))

    graph.set_entry_point("company_loader")
    graph.add_edge("company_loader", "reference_loader")
    graph.add_edge("reference_loader", "market_assessment")
    graph.add_edge("market_assessment", "competition_assessment")
    graph.add_edge("competition_assessment", "strategy_planner")
    graph.add_edge("strategy_planner", "partner_mapper")
    graph.add_edge("partner_mapper", "decision_router")
    graph.add_edge("decision_router", "report_builder")
    graph.set_finish_point("report_builder")
    return graph
