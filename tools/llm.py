# tools/llm.py
from __future__ import annotations
import os
from typing import Optional
from openai import OpenAI

# 환경변수 OPENAI_MODEL 미설정 시 경량 모델 기본값
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_client: Optional[OpenAI] = None

def _client_lazy() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()  # OPENAI_API_KEY 필요
    return _client

def complete_markdown(prompt: str, system: str = "You are a strategy analyst. Write clear, concise Markdown without code fences.") -> str:
    client = _client_lazy()
    # 최신 SDK 기준 chat.completions가 계속 지원됩니다.
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content or ""
