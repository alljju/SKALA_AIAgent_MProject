# SKALA_AIAgent_MProject
목적: 해외 특정 국가 × 산업 진출 의사결정을 위한 의사결정 지도(Decision Map) 자동 생성

MVP 범위: 국가 US | Vietnam 중 택1, 산업 IT/Software | E-commerce 중 택1

핵심 기능:

시장 매력도 요약 → 2) 전략 옵션 후보(직접투자/JV/라이선싱 등)

핵심 규제·장벽(Blocker) 식별 → 4) If-Then 시나리오 기반 전략 확정

방법: LangGraph 기반 Multi-Agent, Geo-fencing + RAG(국가/산업별 인덱스 분리), Evidence-first 보고서 생성
