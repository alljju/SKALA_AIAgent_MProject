"""CLI utility for running the market insight agent (step-by-step capable)."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from platform import system
from typing import Any, Dict

from dotenv import load_dotenv

from graph.nodes.company_profile import company_profile
from graph.nodes.reference_loader import reference_loader
from graph.nodes.law_analyzer import law_analyzer
from graph.nodes.market_analyzer import market_analyzer
from graph.nodes.competition_analyzer import competition_analyzer
from graph.nodes.barrier_extractor import barrier_extractor
from graph.nodes.insight_integrator import insight_integrator

load_dotenv()
if system().lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

INSIGHT_PIPELINE = [
    ("company_loader", company_profile),
    ("reference_loader", reference_loader),
    ("law_analysis", law_analyzer),
    ("market_analysis", market_analyzer),
    ("competition_analysis", competition_analyzer),
    ("barrier_normalizer", barrier_extractor),
    ("insight_integrator", insight_integrator),
]


def _compact_state(state: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    interim = state.get("interim")
    if isinstance(interim, dict):
        for key in ("law", "market", "competition", "barriers"):
            value = interim.get(key)
            if isinstance(value, dict):
                out[key] = len(value)
    insights = state.get("insights")
    if isinstance(insights, list):
        out["insights"] = len(insights)
    return out


def _merge_state(state: Dict[str, Any], update: Dict[str, Any]) -> None:
    if not update:
        return
    for key, value in update.items():
        if key in state and isinstance(state[key], dict) and isinstance(value, dict):
            state[key].update(value)
        else:
            state[key] = value


def _run_stepwise(state: Dict[str, Any], name: str, output: Dict[str, Any], step: bool) -> None:
    if step:
        print(f"### [on_chain_end] {name}")
        print(json.dumps(_compact_state(state), ensure_ascii=False, indent=2))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the market insight agent")
    parser.add_argument("--countries", nargs="+", required=True)
    parser.add_argument("--segment", required=True)
    parser.add_argument("--company-name", default="Target Company")
    parser.add_argument("--company-url")
    parser.add_argument("--company-notes")
    parser.add_argument("--lang", default="ko")
    parser.add_argument("--step", action="store_true", help="Print step-by-step progress")
    parser.add_argument("--out", help="Save insights JSON to this path (optional)")
    return parser.parse_args()


async def _run(state: Dict[str, Any], step: bool, out_path: str | None) -> None:
    working_state = dict(state)
    for name, func in INSIGHT_PIPELINE:
        if step:
            print(f"### [on_chain_start] {name}")
        if asyncio.iscoroutinefunction(func):
            output = await func(working_state)
        else:
            output = func(working_state)
        if isinstance(output, dict):
            _merge_state(working_state, output)
        _run_stepwise(working_state, name, output or {}, step)

    insights = working_state.get("insights", [])
    payload = json.dumps(insights, ensure_ascii=False, indent=2)
    print(payload)
    if out_path:
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")


def main() -> None:
    args = _parse_args()

    company: Dict[str, Any] = {"name": args.company_name}
    if args.company_url:
        company["url"] = args.company_url
    if args.company_notes:
        company["notes"] = args.company_notes

    state: Dict[str, Any] = {
        "countries": args.countries,
        "segment": args.segment,
        "language": args.lang,
        "company": company,
    }
    asyncio.run(_run(state, args.step, args.out))


if __name__ == "__main__":
    main()
