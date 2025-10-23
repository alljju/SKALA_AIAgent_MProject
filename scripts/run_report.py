"""CLI utility for generating the strategy report (step-by-step capable)."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from dotenv import load_dotenv
import langgraph.pregel as _langgraph_pregel

load_dotenv()


def _ensure_versions_defaultdict(checkpoint: Dict[str, Any]) -> Dict[str, Any]:
    versions_seen = checkpoint.get("versions_seen", {})
    if not isinstance(versions_seen, defaultdict):
        checkpoint["versions_seen"] = defaultdict(dict, versions_seen)
    return checkpoint


_ORIGINAL_EMPTY_CHECKPOINT = _langgraph_pregel.empty_checkpoint
_ORIGINAL_COPY_CHECKPOINT = _langgraph_pregel.copy_checkpoint


def _empty_checkpoint_with_defaultdict() -> Dict[str, Any]:
    return _ensure_versions_defaultdict(_ORIGINAL_EMPTY_CHECKPOINT())


def _copy_checkpoint_with_defaultdict(checkpoint: Dict[str, Any]) -> Dict[str, Any]:
    return _ensure_versions_defaultdict(_ORIGINAL_COPY_CHECKPOINT(checkpoint))


_langgraph_pregel.empty_checkpoint = _empty_checkpoint_with_defaultdict
_langgraph_pregel.copy_checkpoint = _copy_checkpoint_with_defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _get_builder():
    try:
        from agents.report.builder import build_report_graph  # type: ignore

        return build_report_graph
    except Exception:
        from graph.builder import build_report_graph

        return build_report_graph


def _compact(state: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key in ("market", "competition", "barriers", "strategies", "partners", "decision"):
        value = state.get(key)
        if isinstance(value, dict):
            out[key] = {
                sub_key: len(sub_val.get("evidence", []))
                for sub_key, sub_val in value.items()
                if isinstance(sub_val, dict)
            }
    return out


def _parse_json(value: str) -> Dict[str, Any]:
    try:
        parsed = json.loads(value)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"Invalid JSON payload: {exc}") from exc
    raise argparse.ArgumentTypeError("Expected a JSON object")


async def _run(state: Dict[str, Any], step: bool) -> None:
    build_report_graph = _get_builder()
    graph = build_report_graph().compile()
    run_config = {"configurable": {"run_id": f"report-{uuid4()}"}}

    if step:
        try:
            async for ev in graph.astream_events(state, config=run_config):
                et = ev.get("event")
                name = ev.get("name") or ev.get("node")
                if et in ("on_chain_start", "on_chain_end"):
                    print(f"### [{et}] {name}")
                if et == "on_chain_end":
                    out = ev.get("data", {}).get("output", {})
                    if out:
                        print(json.dumps(_compact(out), ensure_ascii=False, indent=2))
            return
        except Exception:
            result = await graph.ainvoke(state, config=run_config)
            print(json.dumps(_compact(result), ensure_ascii=False, indent=2))
            return

    result = await graph.ainvoke(state, config=run_config)
    print(json.dumps(result.get("report", {}), ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a multi-part market entry report")
    parser.add_argument("--countries", nargs="+", required=True)
    parser.add_argument("--segment", required=True)
    parser.add_argument("--company-name", required=True)
    parser.add_argument("--company-url")
    parser.add_argument("--company-notes")
    parser.add_argument("--lang", default="ko")
    parser.add_argument("--firm", type=_parse_json, default=_parse_json("{}"))
    parser.add_argument("--rules", type=_parse_json, default=_parse_json("{}"))
    parser.add_argument("--step", action="store_true", help="Print step-by-step progress")
    args = parser.parse_args()

    company: Dict[str, Any] = {"name": args.company_name}
    if args.company_url:
        company["url"] = args.company_url
    if args.company_notes:
        company["notes"] = args.company_notes

    firm: Dict[str, Any] = dict(args.firm)
    firm.setdefault("name", args.company_name)
    if args.company_url and "url" not in firm:
        firm["url"] = args.company_url
    if args.company_notes and "notes" not in firm:
        firm["notes"] = args.company_notes

    state: Dict[str, Any] = {
        "countries": args.countries,
        "segment": args.segment,
        "language": args.lang,
        "firm": firm,
        "rules": args.rules,
        "company": company,
    }
    asyncio.run(_run(state, args.step))


if __name__ == "__main__":
    main()
