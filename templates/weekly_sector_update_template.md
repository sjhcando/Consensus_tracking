---
date: YYYY-MM-DD
type: update
scope: sector
ticker:
sector: {{SECTOR}}
status: active
stance: monitor
delta: stable
conviction: mid
next_trigger: {{NEXT_TRIGGER}}
source_from: {{CONSENSUS_FILE}}; {{MARKET_SNAPSHOT_FILE}}; {{SECTOR_MARKET_SUMMARY_FILE}}; {{REPORT_FILES}}
tags:
  - "{{SECTOR_TAG_LEVEL_2}}"
  - "{{SECTOR_TAG_LEVEL_3_UPDATE}}"
  - "#Stocks/{{COMPANY_A}}"
  - "#Stocks/{{COMPANY_B}}"
---

# {{YYMMDD}} {{SECTOR}} 섹터 주간 업데이트

이번 주 업데이트는 `{{CONSENSUS_FILE}}`, 당주 섹터 리포트와 마켓데이터를 기반으로 작성했다. 뉴스 요약이 아니라 기존 시장 기대 대비 변화량만 기록한다.

---

### 1. 실적 추정치 모니터링 결과
* **{{COMPANY_A}}**: 연간 및 분기 매출/영업이익의 WoW, MoM 변화를 기록한다.
* **{{COMPANY_B}}**: 연간 및 분기 매출/영업이익의 WoW, MoM 변화를 기록한다.
* **실적 추정치 변화의 근거**: 상향, 하향 또는 유지의 근거를 리포트와 연결해 기록한다.

### 2. 핵심 모니터링 항목
* **{{DELTA_POINT_1}}**: 시장 기대 대비 바뀐 사실과 방향을 기록한다.
* **{{DELTA_POINT_2}}**: 시장 기대 대비 바뀐 사실과 방향을 기록한다.

### 3. 시장 해석
* **기존 컨센서스 대비 무엇이 변했는가**: 변화량을 한 문단으로 정리한다.
* **업황 단계 판정**: **{{ACCELERATION | DECELERATION | STABLE | RISK_INCREASE}}**
  * 판정 근거를 1~2문장으로 기록한다.

#### 3-1. 주간 시황 및 가격 해석
| 지표 | 값 | 해석 |
| --- | ---: | --- |
| 섹터 1주 수익률 | {{SECTOR_RET_1W}} | {{INTERPRETATION}} |
| 섹터 1개월 수익률 | {{SECTOR_RET_1M}} | {{INTERPRETATION}} |
| KOSPI 대비 1주 초과수익률 | {{SECTOR_EXCESS_RET_1W}} | {{INTERPRETATION}} |
| 52주 고점 대비 평균 낙폭 | {{SECTOR_DRAWDOWN_52W}} | {{INTERPRETATION}} |
| 섹터 가격 신호 | {{SECTOR_PRICE_SIGNAL}} | {{INTERPRETATION}} |

가격 신호가 컨센서스 변화와 일치하는지 또는 괴리되는지만 해석한다. 가격 자체를 업황 판정의 유일한 근거로 사용하지 않는다.

### 4. 관련 기업
* **{{COMPANY_A}}**: 수혜 또는 위험의 핵심 연결고리를 기록한다.
* **{{COMPANY_B}}**: 수혜 또는 위험의 핵심 연결고리를 기록한다.

### 5. 한줄 결론
> **"{{ONE_LINE_CONCLUSION}}"**
