# SKALA_AIAgent_MProject  
AI 물류·유통 스타트업을 위한 다국적 시장 진출 의사결정 지원 서비스

---

## 🛰️ Overview

**목표**  
AI 기반 다중 노드(LangGraph) 파이프라인을 활용해 물류/유통 스타트업이 국가별 시장 특성과 규제 환경을 빠르게 파악하고, 실행 가능한 진입 전략을 선택할 수 있도록 돕습니다.

**작동 방식**  
1. LangGraph 기반 다중 에이전트 파이프라인이 회사 프로필, 참고 자료, 시장/경쟁/규제 데이터를 순차적으로 수집·정규화합니다.  
2. 규칙 기반 스코어링과 시나리오 로직으로 진입 모드 후보를 평가하고 if-then 의사결정 플로우를 만듭니다.  
3. 프롬프트 템플릿과 HTML 템플릿을 조합해 Markdown/HTML/PDF 형태의 전략 보고서를 생성합니다.  

**핵심 도구**

| Purpose            | Stack / File                                                   |
|--------------------|----------------------------------------------------------------|
| Workflow Orchestration | LangGraph (`graph/builder.py`, `graph/nodes/*`)              |
| LLM & Prompting    | OpenAI API + 커스텀 프롬프트 (`prompts/*.md`, `tools/llm.py`)   |
| Retrieval / Stubs  | 로컬 fetchers & web search 스텁 (`tools/fetchers.py`, `tools/web_search.py`) |
| Reporting          | Markdown → HTML/PDF (`tools/templating.py`, `templates/report.html`) |

---

## ✨ Features

- **다국적 시장 인텔 수집**: 경제 지표, 시장 규모/CAGR, 경쟁 구도, 규제 이슈를 순차적으로 수집.  
- **법·규제 장벽 요약**: FDI, 데이터 로컬라이제이션, 세제, 노동 규제를 표 형태로 정리.  
- **전략 옵션 점수화**: Direct/JV/Licensing/M&A 모드를 가중치 기반으로 평가하고 적합도 점수 생성.  
- **If-Then 의사결정 흐름**: 조건 충족/미충족 시나리오와 루프백 검증 포인트를 출력.  
- **파트너 추천 시그널**: 검색 스텁 기반으로 잠재 협력사/컨설턴트 스니펫을 모읍니다.  
- **다양한 포맷 보고서**: Markdown/HTML/PDF(WeasyPrint 설치 시) 리포트를 `data/outputs/`에 저장.

---

## 🧠 Agents (LangGraph Nodes)

| Node (Edge 순서)          | 역할 요약 |
|---------------------------|-----------|
| `company_loader` (`graph/nodes/company_profile.py`) | 회사 프로필 및 노트 정규화 |
| `reference_loader` (`graph/nodes/reference_loader.py`) | 용어집 등 참고 리소스 주입 |
| `market_assessment` (`graph/nodes/country_market_research.py`) | 국가별 시장/거시 정보 수집 |
| `competition_assessment` (`graph/nodes/competition_analyzer.py`) | 경쟁사 및 증거 스니펫 추출 |
| `strategy_planner` (`graph/nodes/entry_strategy.py`) | 진입 모드 적합도 스코어링 |
| `partner_mapper` (`graph/nodes/partner_sourcing.py`) | 잠재 파트너/투자자 하이라이트 |
| `decision_router` (`graph/nodes/decision_flow_controller.py`) | 시나리오 A/B 및 재검증 조건 |
| `report_builder` (`graph/nodes/report_writer.py`) | 프롬프트+템플릿 기반 최종 리포트 생성 |

보조 노드 (`graph/nodes/barrier_extractor.py`, `graph/nodes/insight_integrator.py` 등)는 내부 파이프라인에서 중간 산출물을 정규화하거나 통합합니다.

---

## 🧾 State Schema

`graph/state.py` 정의에 따른 주요 키:

```python
ReportState(TypedDict, total=False):
    countries: List[str]
    segment: str
    language: Literal["ko", "en"]
    firm: FirmProfile
    rules: RuleThresholds
    company: CompanyProfile
    references / market / competition / barriers / strategies / partners / decision / report: Dict[str, Any]
```

CLI 인자는 `scripts/run_report.py`에서 `ReportState`로 변환됩니다. `firm`, `rules` JSON 옵션을 통해 가중치와 임계치도 주입할 수 있습니다.

---

## ⚙️ Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows 기준
pip install -r requirements.txt
```

### 1) 인사이트 스트림 실행
```bash
.venv\Scripts\python.exe scripts/run_insights.py ^
  --countries Mongolia ^
  --segment digital_signage ^
  --company-name Unitrontech
```

### 2) 전략 보고서 생성
```bash
.venv\Scripts\python.exe scripts/run_report.py ^
  --countries Mongolia ^
  --segment digital_signage ^
  --company-name Unitrontech ^
  --company-url https://unitrontech.com/ ^
  --company-notes "AI-driven logistics and distribution startup" ^
  --lang ko
```

- `--step` 옵션을 추가하면 LangGraph 이벤트 로그를 실시간으로 볼 수 있습니다.  
- 출력물은 `data/outputs/` 아래 `report_<국가>_<세그먼트>_<타임스탬프>.{md,html,pdf}`로 저장됩니다.  
- PDF가 필요하면 WeasyPrint 및 Windows 의존성(Pango, GTK 등)을 설치하세요.

### LLM 호출 설정 (선택)
```bash
setx OPENAI_API_KEY "sk-xxxx"
setx REPORT_RENDER_MODE "llm"
```

### 참고 자료
- 용어집 파일을 `data/reference/logistics_glossary/`에 추가하면 프롬프트에서 정의를 참조합니다.

---

## 🧱 Directory Structure

```
m-medss/
├── config/
│   ├── settings.example.yaml
│   └── sources.yaml
├── data/
│   ├── cache/
│   ├── outputs/                 # 보고서 결과 (MD/HTML/PDF)
│   └── reference/
│       └── logistics_glossary/   # 용어집 PDF 등
├── graph/
│   ├── builder.py               # LangGraph 정의
│   ├── logging_utils.py
│   ├── state.py
│   └── nodes/
│       ├── barrier_extractor.py
│       ├── company_profile.py
│       ├── competition_analyzer.py
│       ├── country_market_research.py
│       ├── decision_flow_controller.py
│       ├── entry_strategy.py
│       ├── insight_integrator.py
│       ├── law_analyzer.py
│       ├── market_analyzer.py
│       ├── partner_sourcing.py
│       ├── reference_loader.py
│       └── report_writer.py
├── prompts/                     # 보고서/분석 섹션 템플릿
│   ├── ai_strategy.md
│   ├── barriers.md
│   ├── competition_analysis.md
│   ├── competition_guideline.md
│   ├── competitive_landscape.md
│   ├── decision_flow.md
│   ├── entry_assessment.md
│   ├── entry_modes.md
│   ├── entry_strategy.md
│   ├── ksf.md
│   ├── law_guideline.md
│   ├── market_guideline.md
│   ├── market_overview.md
│   ├── next_steps.md
│   └── summary.md
├── scripts/
│   ├── run_insights.py          # 파이프라인 요약 실행
│   └── run_report.py            # 전체 보고서 생성 CLI
├── templates/
│   ├── report.html              # HTML/PDF 템플릿
│   └── styles.css
├── tests/
│   ├── __init__.py
│   ├── test_barrier_extractor.py
│   ├── test_decision_flow.py
│   ├── test_integrator.py
│   ├── test_parsing.py
│   └── test_scoring.py
├── tools/
│   ├── company_profile.py
│   ├── export.py
│   ├── fetchers.py
│   ├── llm.py
│   ├── parsing.py
│   ├── reference_loader.py
│   ├── scoring.py
│   ├── templating.py
│   └── web_search.py
├── pyproject.toml
├── requirements.txt
└── README.md (현재 문서)
```

---

## 🧪 Tests

```bash
.venv\Scripts\python.exe -m pytest
```

`tests/` 디렉터리는 파서, 스코어링, 의사결정 컨트롤러 등 핵심 모듈에 대한 단위 테스트를 포함합니다. 실제 데이터 소스로 확장할 경우 새 시나리오에 맞는 fixture를 추가하는 것이 좋습니다.

---

## 📌 Roadmap Hints

- `tools/fetchers.py`, `tools/web_search.py`를 실제 데이터 소스로 교체.  
- `tools/scoring.py`에서 세그먼트/국가별 점수 가중치를 세분화.  
- LangGraph Checkpointer를 도입해 긴 실행을 복구 가능하게 개선.  
- FastAPI 등 외부 인터페이스와 연계하려면 `scripts/` CLI 로직을 API 엔드포인트로 래핑.

---

문의 또는 개선 사항은 이 문서를 참고해 구조를 파악한 뒤, 관련 프롬프트/노드/툴 파일을 수정하면 됩니다. 즐거운 해커톤 되세요! 🚀
