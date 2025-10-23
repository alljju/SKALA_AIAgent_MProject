"""Synthesize the final multi-part strategy report."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

import shutil
from tools.export import to_html, to_pdf
from tools.templating import markdown_to_html, render_md

SUMMARY_PROMPT = "prompts/summary.md"
MARKET_PROMPTS = ["prompts/market_overview.md"]
COMPETITION_PROMPTS = ["prompts/competition_analysis.md"]
ENTRY_PROMPT = "prompts/entry_strategy.md"
RISK_PROMPT = "prompts/risk_management.md"
AI_PROMPT = "prompts/ai_strategy.md"

SECTION_SPECS: list[tuple[str, list[str]]] = [
    ("summary", [SUMMARY_PROMPT]),
    ("market", MARKET_PROMPTS),
    ("barriers", ["prompts/barriers.md"]),
    ("competition", COMPETITION_PROMPTS),
    ("competition_guideline", ["prompts/competition_guideline.md"]),
    ("competitive_landscape", ["prompts/competitive_landscape.md"]),
    ("entry", [ENTRY_PROMPT]),
    ("entry_modes", ["prompts/entry_modes.md"]),
    ("entry_assessment", ["prompts/entry_assessment.md"]),
    ("decision_flow", ["prompts/decision_flow.md"]),
    ("ksf", ["prompts/ksf.md"]),
    ("risk", [RISK_PROMPT]),
    ("ai", [AI_PROMPT]),
    ("next_steps", ["prompts/next_steps.md"]),
    ("market_guideline", ["prompts/market_guideline.md"]),
]


def _render_sections(prompts: Iterable[str], state: Dict[str, Any]) -> str:
    fragments: List[str] = []
    for prompt in prompts:
        content = render_md(prompt, state).strip()
        if content:
            fragments.append(content)
    return "\n\n".join(fragments)


def _render_prompt_block(prompts: List[str], state: Dict[str, Any]) -> str:
    if not prompts:
        return ""
    if len(prompts) == 1:
        return render_md(prompts[0], state).strip()
    return _render_sections(prompts, state)


def _collect_evidence(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    evidence: List[Dict[str, Any]] = []
    for bucket in ("market", "competition", "partners"):
        payload = state.get(bucket, {})
        if isinstance(payload, dict):
            for item in payload.values():
                if isinstance(item, dict):
                    snippets = item.get("evidence", [])
                    if isinstance(snippets, list):
                        evidence.extend(snippets)
    decision = state.get("decision", {})
    if isinstance(decision, dict):
        for item in decision.values():
            if isinstance(item, dict):
                snippets = item.get("evidence", [])
                if isinstance(snippets, list):
                    evidence.extend(snippets)
    return evidence



def _cleanup_text(value: str) -> str:
    return value.replace("N/A", "추가 검증 필요")

def _slug(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in value.strip())
    return "_".join(filter(None, cleaned.split("_"))) or "report"


def report_writer(state: Dict[str, Any]) -> Dict[str, Any]:
    """Render markdown/HTML strategy report tailored to the provided company."""
    company = state.get("company", {}) or {}
    company_name = company.get("name", "Target Company")
    company_headline = company.get("headline") or company.get("description") or ""
    company_url = company.get("url")

    company_outline_md_lines = [
        "### Company Snapshot",
        f"- **Company:** {company_name}",
    ]
    if company_headline:
        company_outline_md_lines.append(f"- **Positioning:** {company_headline}")
    if company_url:
        company_outline_md_lines.append(f"- **Website:** {company_url}")
    if company.get("offerings"):
        offerings = "; ".join(company.get("offerings", []))
        company_outline_md_lines.append(f"- **Core Offerings:** {offerings}")
    if company.get("differentiators"):
        differentiators = "; ".join(company.get("differentiators", []))
        company_outline_md_lines.append(f"- **Differentiators:** {differentiators}")
    if company.get("target_segments"):
        targets = "; ".join(company.get("target_segments", []))
        company_outline_md_lines.append(f"- **Target Segments:** {targets}")

    company_outline_md = _cleanup_text("\n".join(company_outline_md_lines).strip())
    section_markdown: Dict[str, str] = {}
    for name, prompts in SECTION_SPECS:
        block = _render_prompt_block(prompts, state)
        section_markdown[name] = _cleanup_text(block)

    summary_md = section_markdown.get("summary", "")
    market_md = section_markdown.get("market", "")
    barriers_md = section_markdown.get("barriers", "")
    competition_md = section_markdown.get("competition", "")
    competition_guideline_md = section_markdown.get("competition_guideline", "")
    competitive_landscape_md = section_markdown.get("competitive_landscape", "")
    entry_md = section_markdown.get("entry", "")
    entry_modes_md = section_markdown.get("entry_modes", "")
    entry_assessment_md = section_markdown.get("entry_assessment", "")
    decision_flow_md = section_markdown.get("decision_flow", "")
    ksf_md = section_markdown.get("ksf", "")
    risk_md = section_markdown.get("risk", "")
    ai_md = section_markdown.get("ai", "")
    next_steps_md = section_markdown.get("next_steps", "")
    market_guideline_md = section_markdown.get("market_guideline", "")

    summary_html = markdown_to_html(summary_md) if summary_md else ""
    market_html = markdown_to_html(market_md) if market_md else ""
    barriers_html = markdown_to_html(barriers_md) if barriers_md else ""
    competition_guideline_html = (
        markdown_to_html(competition_guideline_md) if competition_guideline_md else ""
    )
    competitive_landscape_html = (
        markdown_to_html(competitive_landscape_md) if competitive_landscape_md else ""
    )
    ai_html = markdown_to_html(ai_md) if ai_md else ""
    competition_html = markdown_to_html(competition_md) if competition_md else ""
    entry_html = markdown_to_html(entry_md) if entry_md else ""
    entry_modes_html = markdown_to_html(entry_modes_md) if entry_modes_md else ""
    entry_assessment_html = (
        markdown_to_html(entry_assessment_md) if entry_assessment_md else ""
    )
    decision_flow_html = markdown_to_html(decision_flow_md) if decision_flow_md else ""
    ksf_html = markdown_to_html(ksf_md) if ksf_md else ""
    risk_html = markdown_to_html(risk_md) if risk_md else ""
    company_outline_html = markdown_to_html(company_outline_md) if company_outline_md else ""
    next_steps_html = markdown_to_html(next_steps_md) if next_steps_md else ""
    market_guideline_html = (
        markdown_to_html(market_guideline_md) if market_guideline_md else ""
    )

    markdown_sections = [f"# {company_name} Market Entry Strategy Report"]
    if company_outline_md:
        markdown_sections.append(company_outline_md)
    for key in [name for name, _ in SECTION_SPECS]:
        block = section_markdown.get(key)
        if block:
            markdown_sections.append(block)
    markdown_report = "\n\n".join(markdown_sections)

    countries_list = state.get("countries", [])
    segment = state.get("segment", "market")
    generated_at = datetime.now()

    html_report = to_html(
        "report.html",
        {
            "company_outline": company_outline_html,
            "summary": summary_html,
            "market": market_html,
            "barriers": barriers_html,
            "ai": ai_html,
            "competition": competition_html,
            "competition_guideline": competition_guideline_html,
            "competitive_landscape": competitive_landscape_html,
            "entry": entry_html,
            "entry_modes": entry_modes_html,
            "entry_assessment": entry_assessment_html,
            "decision_flow": decision_flow_html,
            "ksf": ksf_html,
            "risk": risk_html,
            "next_steps": next_steps_html,
            "market_guideline": market_guideline_html,
            "company_name": company_name,
            "company_headline": company_headline,
            "company_url": company_url,
            "segment": segment,
            "countries": ", ".join(countries_list),
            "generated_at": generated_at.strftime("%Y-%m-%d %H:%M"),
        },
    )

    out_dir = Path(__file__).resolve().parents[2] / "data" / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    countries = "_".join(_slug(c) for c in state.get("countries", []))
    segment = _slug(state.get("segment", "segment"))
    base_name = f"report_{countries}_{segment}_{stamp}"

    markdown_path = out_dir / f"{base_name}.md"
    markdown_path.write_text(markdown_report, encoding="utf-8")

    html_path = out_dir / f"{base_name}.html"
    html_path.write_text(html_report, encoding="utf-8")

    # Copy stylesheet alongside the report for correct rendering
    templates_root = Path(__file__).resolve().parents[2] / "templates"
    css_source = templates_root / "styles.css"
    if css_source.exists():
        try:
            shutil.copy(css_source, out_dir / "styles.css")
        except Exception:
            pass

    pdf_result = None
    try:
        pdf_result = to_pdf(
            html_report,
            out_path=out_dir / f"{base_name}.pdf",
            base_url=out_dir,
        )
    except Exception:
        pdf_result = None

    evidence = _collect_evidence(state)

    return {
        "report": {
            "summary": summary_md,
            "markdown": markdown_report,
            "markdown_path": str(markdown_path),
            "html": html_report,
            "html_path": str(html_path),
            "pdf_path": pdf_result,
            "company_outline": company_outline_md,
            "market": market_md,
            "barriers": barriers_md,
            "competition_guideline": competition_guideline_md,
            "competitive_landscape": competitive_landscape_md,
            "ai": ai_md,
            "competition": competition_md,
            "entry": entry_md,
            "entry_modes": entry_modes_md,
            "entry_assessment": entry_assessment_md,
            "decision_flow": decision_flow_md,
            "ksf": ksf_md,
            "risk": risk_md,
            "next_steps": next_steps_md,
            "market_guideline": market_guideline_md,
        },
        "evidence": evidence,
    }


