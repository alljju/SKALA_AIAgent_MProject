"""Normalize raw regulatory findings into structured barriers."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

# ---- simple classifiers ------------------------------------------------------

def _collect_texts(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    payload 내부의 규제 관련 텍스트 스니펫들을 최대한 긁어 모아 반환.
    반환 원소: {"text": ..., "source_url": ...}
    """
    out: List[Dict[str, str]] = []

    # 1) evidence 형식
    for it in payload.get("evidence", []) or []:
        txt = (it.get("fact") or it.get("text") or "").strip()
        if txt:
            out.append({"text": txt, "source_url": it.get("source_url", "")})

    # 2) pages 형식(있다면)
    for pg in payload.get("pages", []) or []:
        txt = ""
        for key in ("content", "snippet", "summary", "title"):
            v = pg.get(key)
            if v:
                txt = str(v).strip()
                break
        if txt:
            out.append({"text": txt, "source_url": pg.get("url") or pg.get("source") or ""})

    # 3) 기타 관례적 키
    for key in ("notes", "law_text", "raw"):
        v = payload.get(key)
        if isinstance(v, str) and v.strip():
            out.append({"text": v.strip(), "source_url": ""})

    return out


def _classify_fdi(text: str) -> str | None:
    """텍스트에서 외국인투자 제한 레벨 추정 (low/medium/high)."""
    t = text.lower()

    # 강한 제한 신호
    if re.search(r"\bforeign\s+(ownership|investment)\s+(ban|prohibition|prohibited)\b", t):
        return "high"
    if re.search(r"\b(sector|industry)\s+(reserved|restricted)\s+for\s+(nationals|locals)\b", t):
        return "high"

    # 중간 제한 신호
    if re.search(r"\b(equity\s+cap|foreign\s+ownership\s+(cap|limit|restriction)|local\s+partner\s+required|joint\s+venture\s+required)\b", t):
        return "medium"

    # 낮은 제한 신호
    if re.search(r"\bno\s+(statutory|regulatory)\s+limits?\s+on\s+foreign\s+ownership\b", t):
        return "low"
    if re.search(r"\bno\s+(general\s+)?foreign\s+ownership\s+restrictions\b", t):
        return "low"

    return None


def _classify_data_loc(text: str) -> str | None:
    """
    텍스트에서 데이터 현지화/이전 제한 범주 추정.
    반환: 'broad' | 'sectoral' | 'cross-border restrictions' | None
    """
    t = text.lower()

    # 일반적인 '데이터 현지화' 용어
    if "data localization" in t or "store data locally" in t or "local storage of data" in t:
        # 포괄/전면적
        if any(k in t for k in ["all personal data", "across sectors", "broad requirement"]):
            return "broad"
        return "sectoral"

    # 미국 DOJ Bulk Data Transfer Rule 같은 '이전 제한' (현지화와는 구분)
    if "bulk data transfer rule" in t or "countries of concern" in t:
        return "cross-border restrictions"

    # 법명과 결합된 이전 제한 문구 (느슨한 분류)
    if "data protection" in t and "cross-border" in t and "transfer" in t:
        return "sectoral"

    return None


def _extract_tax_labor(text: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """텍스트에서 세제/노동 관련 흔한 요소만 플래그로 추출."""
    t = text.lower()
    tax: Dict[str, Any] = {}
    labor: Dict[str, Any] = {}

    if "vat" in t or "value-added tax" in t:
        tax.setdefault("vat", "exists")
    if "corporate tax" in t or "corporate income tax" in t:
        tax.setdefault("corporate_income_tax", "exists")
    if "withholding" in t:
        tax.setdefault("withholding", "exists")

    if "work permit" in t or "labor permit" in t or "labour permit" in t or "quota" in t:
        labor.setdefault("work_permit_quota", "exists")
    if "minimum wage" in t:
        labor.setdefault("minimum_wage", "exists")

    return tax, labor


def _merge_level(current: str | None, new: str | None) -> str | None:
    """제한 강도 통합: high > medium > low."""
    order = {"high": 3, "medium": 2, "low": 1, None: 0}
    return new if order.get(new, 0) > order.get(current, 0) else current


# ---- main node --------------------------------------------------------------

def barrier_extractor(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    law 노드 결과를 규격화된 barriers 스키마로 매핑 + 간단한 규칙 기반 보강.
    출력 예:
    interim: {
      barriers: {
        "United States": {
          "fdi_restriction": "medium",
          "data_localization": "cross-border restrictions",
          "tax_regime": {...},
          "labor_regulation": {...},
          "other": [...],
          "evidence": [ {fact, source_url}, ... ]
        },
        ...
      }
    }
    """
    law_results = state.get("interim", {}).get("law", {}) or {}
    normalized: Dict[str, Any] = {}

    for country, payload in law_results.items():
        # 초기값 (law 노드가 이미 일부 정규화했으면 존중)
        base = payload.get("barriers", {}) or {}
        fdi_level: str | None = base.get("fdi_restriction")
        data_loc: str | None = base.get("data_localization")
        tax_regime: Dict[str, Any] = dict(base.get("tax_regime") or {})
        labor_reg: Dict[str, Any] = dict(base.get("labor_regulation") or {})
        other: List[str] = list(base.get("other") or [])
        evidence: List[Dict[str, str]] = []

        # 텍스트 수집
        snippets = _collect_texts(payload)
        # 텍스트 기반 분류
        for sn in snippets:
            text = sn.get("text") or ""
            src = sn.get("source_url") or ""
            if text:
                # FDI
                fdi_guess = _classify_fdi(text)
                fdi_level = _merge_level(fdi_level, fdi_guess)

                # 데이터 현지화/이전
                dl_guess = _classify_data_loc(text)
                data_loc = data_loc or dl_guess  # 보수적으로 최초 추정만 채움

                # 세제/노동 플래그
                tax_add, labor_add = _extract_tax_labor(text)
                for k, v in (tax_add or {}).items():
                    tax_regime.setdefault(k, v)
                for k, v in (labor_add or {}).items():
                    labor_reg.setdefault(k, v)

                # 증거 축적
                evidence.append({"fact": text[:220], "source_url": src})

        # 최종 매핑
        normalized[country] = {
            "fdi_restriction": fdi_level,                    # "low" | "medium" | "high" | None
            "data_localization": data_loc,                   # "broad" | "sectoral" | "cross-border restrictions" | None
            "tax_regime": tax_regime,
            "labor_regulation": labor_reg,
            "other": other,
            "evidence": evidence,                            # ← 보고서에서 근거로 활용 가능
        }

    # state 병합
    interim = dict(state.get("interim", {}))
    interim["barriers"] = normalized
    return {"interim": interim}
