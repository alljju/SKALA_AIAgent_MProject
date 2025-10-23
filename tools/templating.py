"""Jinja2 기반 템플릿 렌더링 및 선택적 LLM 후처리 헬퍼."""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, Union

from jinja2 import Environment, FileSystemLoader

try:
    from markdown import markdown as _markdown
except ImportError:  # pragma: no cover - 마크다운 미설치 시 단순 통과
    def _markdown(text: str, **kwargs):  # type: ignore[misc]
        return text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = PROJECT_ROOT / "prompts"
TEMPLATES_DIR = PROJECT_ROOT / "templates"


@lru_cache(maxsize=1)
def _env() -> Environment:
    """프로젝트 내 템플릿 탐색 경로를 설정한 Jinja 환경을 반환."""
    search_paths = []
    for path in (PROMPTS_DIR, TEMPLATES_DIR, PROJECT_ROOT):
        if path.exists():
            search_paths.append(str(path))
    if not search_paths:
        search_paths.append(str(PROJECT_ROOT))
    return Environment(loader=FileSystemLoader(search_paths), autoescape=False, trim_blocks=True, lstrip_blocks=True)


def get_env() -> Environment:
    """외부에서 환경 재활용 시 사용."""
    return _env()


def _render_template(template_path: str, context: Dict[str, Any]) -> str:
    template = _env().get_template(template_path)
    return template.render(**context)


KO_TRANSLATIONS = {
    "Executive Summary Template": "\uacbd\uc601 \uc694\uc57d \ud15c\ud50c\ub9bf",
    "Executive Summary": "\uc694\uc57d",
    "[Role]": "[\uc5ed\ud560]",
    "[Output Format]": "[\ucd9c\ub825 \ud615\uc2dd]",
    "[Objective]": "[\ubaa9\ud45c]",
    "[Evidence]": "[\uadfc\uac70]",
    "[Output]": "[\uc0b0\ucd9c\ubb3c]",
    "[Requirements]": "[\uc694\uad6c \uc0ac\ud56d]",
    "Final Recommendation": "\ucd5c\uc885 \uad8c\uace0",
    "Key Evidence": "\ud575\uc2ec \uadfc\uac70",
    "Opportunities": "\uae30\ud68c",
    "Risks": "\uc704\ud5d8",
    "Sources Count": "\ucd9c\ucc98 \uc218",
    "Market Overview": "\uc2dc\uc7a5 \uac1c\uc694",
    "Competitive Landscape": "\uacbd\uc7c1 \uad6c\ub3c4",
    "Key Success Factors": "\ud575\uc2ec \uc131\uacf5 \uc694\uc778",
    "Entry Modes": "\uc9c4\uc785 \uc804\ub7b5",
    "Entry Assessment": "\uc9c4\uc785 \ubc29\uc2dd \ud3c9\uac00",
    "Critical Barriers": "\uc8fc\uc694 \uc9c4\uc785 \uc7a5\ubcbd",
    "Decision Flow": "\uc758\uc0ac\uacb0\uc815 \ud750\ub984",
    "Next Steps": "\ud5a5\ud6c4 \uc77c\uc815",
}


def _localize_stub(text: str, language: str) -> str:
    if language != "ko":
        return text
    localized = text
    for src, dest in KO_TRANSLATIONS.items():
        localized = localized.replace(src, dest)
    return localized


def _render_with_llm(content: str, state: Dict[str, Any]) -> str:
    """REPORT_RENDER_MODE=llm && OPENAI_API_KEY 설정 시 LLM으로 마크다운 재작성."""
    mode = os.getenv("REPORT_RENDER_MODE", "")
    mode = mode.strip().strip("\"'").lower()
    if mode != "llm":
        return content
    if not os.getenv("OPENAI_API_KEY"):
        return content

    try:
        from tools.llm import complete_markdown
    except ImportError:
        return content

    prompt = (
        "[INSTRUCTION]\n"
        f"{content}\n\n"
        "[STATE JSON]\n```json\n"
        f"{json.dumps(state, ensure_ascii=False, indent=2)}\n"
        "```\n\n"
        "[REQUIREMENTS]\n"
        f"- Output in {state.get('language', 'ko')}.\n"
        "- Use only grounded facts from STATE; if unknown, write 'N/A'.\n"
        "- Prefer Markdown tables or bullet lists where useful.\n"
    )

    try:
        output = complete_markdown(prompt) or ""
        return output.strip()
    except Exception:
        # LLM 호출 실패 시 원본 유지
        return content


def render_md(template_path: Union[str, Iterable[str]], state: Dict[str, Any]) -> str:
    """단일 또는 다중 마크다운 템플릿을 렌더링."""
    if isinstance(template_path, (list, tuple, set)):
        fragments = [render_md(path, state) for path in template_path]
        return "\n\n".join(fragments)

    context = {"state": state, **state}
    raw_content = _render_template(template_path, context)
    processed = _localize_stub(raw_content, state.get("language", "en"))
    processed = _render_with_llm(processed, state)
    return processed


def render_md_html(template_path: Union[str, Iterable[str]], state: Dict[str, Any]) -> str:
    """render_md 결과를 HTML로 변환."""
    return markdown_to_html(render_md(template_path, state))


def markdown_to_html(text: str) -> str:
    """마크다운을 HTML로 변환(테이블 등 확장 지원)."""
    return _markdown(
        text,
        extensions=[
            "extra",
            "sane_lists",
            "tables",
            "toc",
            "admonition",
            "smarty",
        ],
    )
