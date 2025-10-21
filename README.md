# SKALA_AIAgent_MProject

## TITLE
AI 물류/유통 스타트업에 특화된 다국적 시장 진출 의사결정 지원 서비스입니다.

## Overview

- **Objective**: 물류 및 유통 스타트업을 위해 다국적 시장 진출 의사결정을 지원하는 **AI 기반 의사결정 시스템**을 구축하여, 기업들이 각 국가의 시장 특성에 맞는 최적의 진입 전략을 수립할 수 있도록 돕습니다. 이 시스템은 규제, 시장 매력도, 경쟁 분석 등 복잡한 변수를 통합하여 사용자가 효과적인 전략을 선택할 수 있도록 안내합니다.
  
- **Methods**:  
  1. **다중 에이전트 시스템(MAS)** - 각 국가와 산업에 특화된 데이터를 수집하고 분석하여 의사결정을 지원하는 여러 개의 전문 에이전트가 협업합니다.
  2. **Geo-fencing 및 RAG** - 선택된 국가와 산업에만 집중하여 데이터 수집 및 분석을 정확하게 제한하고, 최신의 검색된 정보를 바탕으로 의사결정을 시뮬레이션합니다.

- **Tools**:  
  1. **LangGraph** - 다중 에이전트의 워크플로우와 의사결정 흐름을 조정하고 최적화하는 오케스트레이션 도구입니다.
  2. **FastAPI** - 사용자 인터페이스를 통해 요청을 받고, 처리된 결과를 리포트 형식으로 제공합니다.
  3. **pgvector** - 벡터 데이터베이스를 사용하여 국가 및 산업별 정보를 색인화하고, 이를 기반으로 빠르고 정확한 검색을 지원합니다.

## Features

- **다국적 시장 분석**: 다양한 국가와 산업에 대한 시장 분석을 제공하여, 기업들이 진입할 시장의 매력도를 평가할 수 있습니다.
- **법적/규제 분석**: 각 국가별 법적 요구사항과 규제 장벽을 분석하고, 이에 대한 대응 전략을 제공합니다.
- **If-Then 시나리오 생성**: 실시간 데이터를 기반으로 전략적 결정을 내릴 수 있는 'If-Then' 시나리오를 제시하여, 최적의 시장 진입 경로를 안내합니다.

## Agents

### 1. 국가별 시장 조사 에이전트
- **목표**: 미국과 몽골의 시장 규모, 규제 요건, 경쟁사 조사
- **기능**: 해당 국가의 물류/유통 시장 규모, 주요 기업, 경쟁 분석 데이터 제공
  - **작업**: 
    - 국가별 시장의 규모 및 성장 전망 조사
    - 주요 기업 및 경쟁사 분석
    - 규제 요건 및 법적 장벽 분석

### 2. 경쟁 분석 에이전트
- **목표**: 물류/유통 산업 내 경쟁사의 변동 및 시장 차별화 포인트 도출
- **기능**: 주요 경쟁사의 기술, 전략, 시장 점유율 등 분석
  - **작업**: 
    - 경쟁사 분석(시장 점유율, 전략)
    - 경쟁사의 기술적 차별화 요소 분석
    - 시장의 경쟁 구도 및 주요 경쟁자 특징 도출

### 3. 진출 전략 제안 에이전트
- **목표**: 미국과 몽골 시장에 대한 진출 방식(직접 진출, 파트너십 등)을 제시
- **기능**: 두 국가에 적합한 진출 방법과 파트너십 옵션 제시
  - **작업**: 
    - 각 시장에 대한 진출 전략 제안(직접 진출, JV, 라이선싱 등)
    - 시장 상황에 맞는 진출 방식 분석

### 4. 파트너 후보 추천 에이전트
- **목표**: 파트너 후보를 탐색하고 추천
- **기능**: 현지 협력사, 투자자, 컨설턴트 추천
  - **작업**:
    - 각 시장에서 협력할 수 있는 파트너 후보 탐색
    - 잠재적인 투자자 및 컨설턴트 추천
    - 파트너십 모델에 맞는 후보자 선별

### 5. 전략 보고서 작성 에이전트
- **목표**: 최종 전략 요약 및 보고서 형식으로 제공
- **기능**: 전체 전략을 요약하고, 보고서 형태로 정리
  - **작업**:
    - 의사결정 흐름을 요약하여 보고서 형식으로 정리
    - 전략적 권고 사항을 제시
    - 보고서의 결론 및 실행 계획 제시

## State

- **country**: 사용자가 선택한 진출 목표 국가 (예: 미국, 몽골)
- **industry**: 진출하려는 산업 (예: 물류/소프트웨어, 이커머스)
- **decision_points**: 사용자가 선택한 시장에 진입하기 위한 주요 의사결정 지점 (예: 현지 서버 구축, 법인 설립 형태)
- **regulatory_barriers**: 각 국가 및 산업별 주요 법적 장벽 및 규제 요구사항
- **strategies**: 각 의사결정 지점에 따른 전략 옵션 (예: 100% 직접 투자, JV, 라이선싱 등)
  
## Tech Stack 

| Category   | Details                      |
|------------|------------------------------|
| Framework  | LangGraph, LangChain, Python |
| LLM        | GPT-4o-mini via OpenAI API   |
| Retrieval  | FAISS, Chroma                |
| Embedding  | OpenAIEmbedding, Mistral...  |


## Architecture

<img width="2491" height="1952" alt="Untitled diagram-2025-10-21-081953" src="https://github.com/user-attachments/assets/a4bdd6a3-4280-4902-a117-8eb0f7ab8ca5" />


## Directory Structure
m-medss/
├── apps/
│  └── api/
│     ├── main.py                 # FastAPI 엔트리
│     ├── deps.py                 # DI/세션/검증
│     ├── routes/
│     │  ├── report.py            # /v1/decision-map/report 엔드포인트
│     │  └── health.py            # 서비스 헬스 체크
│     └── schemas/
│        ├── state.py             # Pydantic 모델 (State 모델 정의)
│        └── io.py                # 요청/응답 데이터 구조 정의
├── graph/
│  ├── builder.py                 # StateGraph 정의 및 구축
│  ├── nodes/
│  │  ├── router.py               # Query Analyst & Router (사용자 쿼리 분석 및 라우팅)
│  │  ├── collector_market.py     # Market Sub-Agent (시장 데이터 수집)
│  │  ├── collector_legal.py      # Legal Sub-Agent (법률/규제 데이터 수집)
│  │  ├── strategy_generator.py   # Strategy Option Generator (전략 옵션 생성)
│  │  ├── decision_architect.py   # Decision-Flow Architect (If-Then 시나리오 구성)
│  │  └── report_generator.py     # Report Generator (결과 보고서 생성)
│  └── policies/
│     ├── scoring.py              # 전략 점수/가중치 계산
│     └── rules.py                # If-Then 규칙 템플릿 정의
├── tools/
│  ├── market_data.py             # MarketDataTool (시장 분석 데이터 수집)
│  ├── legal_db.py                # LegalDB (법률/규제 DB 검색)
│  ├── geofence.py                # GeoFence (국가/산업별 Geo-fencing 기능)
│  ├── rag.py                     # RAG.retrieve (검색 및 증강된 생성)
│  ├── cost_model.py              # CAPEX/OPEX 계산을 위한 비용 모델
│  └── partner_db.py              # Partner lookup (모의 파트너 DB, JV 탐색용)
├── data/
│  ├── seeds/                     # 초기 규칙/테이블 데이터 (기본값 설정)
│  └── index/                     # 벡터 인덱스 (국가×산업 분리된 인덱스 저장)
├── prompts/
│  ├── market_brief.md            # 시장 요약 프롬프트 템플릿
│  ├── legal_brief.md             # 법률/규제 요약 프롬프트 템플릿
│  ├── strategy_options.md        # 전략 옵션 생성 프롬프트 템플릿
│  └── decision_flow.md           # 의사결정 흐름 생성 프롬프트 템플릿
├── configs/
│  ├── app.yaml                  # FastAPI 설정 파일
│  └── rag.yaml                   # RAG 설정 파일 (검색 및 생성 파라미터)
├── tests/
│  ├── test_graph.py              # 그래프 로직 및 에이전트 통합 테스트
│  ├── test_tools.py              # 도구 관련 기능 테스트
│  └── fixtures/                  # 테스트 고정 데이터
└── README.md


