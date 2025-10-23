# ROLE
Identify key success factors for {{ company.name or "the company" }} (startup) expanding into {{ countries | join(", ") }}.

# TASKS
- List two common KSFs relevant to any market entry (e.g., regulatory agility, data-driven operations) and tie them to the company’s offerings/differentiators.
- For each country, specify one unique KSF reflecting regulation, infrastructure, or customer nuance, with startup-specific implications.
- Provide measurable indicators and immediate prerequisite actions for every KSF.

# OUTPUT (MARKDOWN, KO)
#### 1-3. 핵심 성공 요인 (KSF)
- **공통 KSF (2)**  
  - KSF #1 — 지표 / 선결 과제 (스타트업 관점)  
  - KSF #2 — 지표 / 선결 과제
- **국가별 KSF**  
{% for country in countries %}  - {{ country }} — … ({{ company.name or "the company" }} 적용 방식, 지표/선결 과제 포함)  
{% endfor %}

# STYLE
- 각 항목 1문장, 지표는 숫자/단위 포함.
- 부족한 정보는 “추가 검증 필요 – …”로 명시.

# CONSTRAINTS
- KSF는 회사의 차별화 요소 또는 파트너 전략과 연결해야 함.
- 실행 주체(팀/파트너)를 괄호로 표시.
