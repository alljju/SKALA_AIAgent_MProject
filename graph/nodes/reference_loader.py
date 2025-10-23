"""Load reference documents into the graph state."""
from __future__ import annotations

from typing import Any, Dict, Mapping

from tools.reference_loader import load_logistics_glossary


async def reference_loader(state: Dict[str, Any]) -> Dict[str, Any]:
    existing = state.get("references") or {}
    if isinstance(existing, Mapping):
        references: Dict[str, Any] = dict(existing)
    else:
        references = {}
    glossary_text = load_logistics_glossary()
    if glossary_text:
        references["logistics_glossary"] = glossary_text
    else:
        references.setdefault(
            "logistics_glossary",
            "참고용 물류/유통 용어 사전이 발견되지 않았습니다. data/reference/logistics_glossary/ 경로에 PDF를 추가해 주세요.",
        )
    return {"references": references}
