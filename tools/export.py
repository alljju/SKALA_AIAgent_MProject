# tools/export.py
"""Helpers for exporting rendered content to HTML (and optionally PDF)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

# _env가 함수일 수도, Environment 객체일 수도 있으므로 안전하게 래핑
from tools.templating import _env as _tmpl_env

def _get_env():
    return _tmpl_env() if callable(_tmpl_env) else _tmpl_env

def to_html(template_path: str, context: Dict[str, Any]) -> str:
    """Render the shared HTML template with provided markdown segments."""
    env = _get_env()

    # 절대/상대 경로 모두 허용
    p = Path(template_path)
    if p.is_file():
        text = p.read_text(encoding="utf-8")
        tmpl = env.from_string(text)
        return tmpl.render(**context)

    # 일반적으로는 파일명만 넘기는 것을 권장: "report.html"
    template = env.get_template(Path(template_path).name)
    return template.render(**context)

def to_pdf(html: str, out_path: str | Path | None = None, base_url: str | Path | None = None) -> Optional[str]:
    """Optional PDF export via WeasyPrint. Returns the output path if written."""
    try:
        from weasyprint import HTML  # type: ignore
    except ImportError:
        return None

    output_path = Path(out_path) if out_path else None
    kwargs: Dict[str, Any] = {}
    if base_url is not None:
        kwargs["base_url"] = str(base_url)
    document = HTML(string=html, **kwargs)
    if output_path:
        document.write_pdf(str(output_path))
        return str(output_path)

    # Return the raw PDF bytes when no path is provided.
    pdf_bytes = document.write_pdf()
    return pdf_bytes  # type: ignore[return-value]
