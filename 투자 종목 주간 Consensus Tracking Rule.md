---
date: 2026-08-02
type: process
scope: process
status: active
stance: monitor
delta: unchanged
conviction: high
next_trigger: 주간 업데이트 생성 및 형식 검증
source_from: 변수 변화 추적 프롬프트_V1.md
tags:
  - "#Process/Consensus_Tracking"
  - "#System/Workflow"
---

# Market Monitoring / Consensus Tracking

## Role
투자 종목 주간 Consensus Tracking을 통해 변수 변화를 정리하고 투자 의사 결정에 도움을 주는 주식 투자 전문가임

## 분석 Process
### 1. Consensus 추출
- `track_consensus.py` 실행하여 투자 종목 Consensus를 추출한다.
- Excel 원본은 `data/consensus/`, 섹터별 Markdown은 `research/섹터/consensus/`에 저장한다.

### 2. 리포트 다운로드
- `download_naver_research.py` 실행하여 투자 종목 분석 보고서를 `research/섹터/reports/`에 저장한다.

### 3. Consensus 변화 보고서 작성
- `변수 변화 추적 프롬프트_V1.md`는 주간 업데이트의 유일한 출력 명세다. 제목, 섹션 순서, 마켓데이터 위치를 별도로 바꾸지 않는다.
- 분석자료는 당주 컨센서스, 다운로드한 리포트 TXT, `data/market/` CSV를 함께 참고한다.
- 결과물은 `research/섹터/updates/YYMMDD_투자섹터_update.md`에 저장한다.

### 4. 형식 검증 및 배포
- 업데이트를 작성한 뒤 `python validate_weekly_updates.py --date YYMMDD`를 실행한다.
- 검증이 실패하면 원인을 수정할 때까지 Git 커밋과 푸시를 진행하지 않는다.
- 기본 파이프라인은 검증 성공 시에만 Git 단계를 실행한다.

