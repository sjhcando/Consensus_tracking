---
date: 2026-07-24
type: process
scope: process
ticker:
sector:
status: active
stance: monitor
delta: unchanged
conviction: mid
next_trigger:
source_from:
tags:
---

# Consensus Tracking

투자 종목 및 섹터에 대한 컨센서스(실적 전망치)의 변화를 추출하고, 이러한 컨센서스 변화의 원인을 심층 분석할 수 있도록 증권사 리서치 리포트를 자동 추출 및 텍스트 변환하여 종합 보고서를 작성하는 자동화 프로그램입니다.

데스크탑과 노트북 등 여러 기기를 오가며 원활하게 협업하고 분석 작업을 자동화할 수 있는 파이프라인이 포함되어 있습니다.

---

## 🚀 주요 기능 (Features)

1. **통합 파이프라인 자동 실행** (`run_pipeline.py`)
   * 크롤링, 리포트 수집, PDF 본문 텍스트 추출, 주간 변동성 비교표 작성을 단 하나의 명령어로 오케스트레이션합니다.
   * 실행 완료 시 결과물을 GitHub 원격 저장소에 자동으로 커밋 및 푸시하여 여러 기기 간의 실시간 동기화를 지원합니다.

2. **주간 컨센서스 데이터 추출 및 격차 분석** (`track_consensus.py` & `compare_consensus.py`)
   * 에프앤가이드(FnGuide)를 크롤링하여 `stocks.json`에 등록된 5개 섹터(반도체, 방산, 전기전자, 조선, 전력기기)의 실적 전망치를 수집합니다.
   * 지난주 데이터와 이번 주 데이터를 자동 대조하여 **주간 변동률(%) 및 1개월 전 대비 증감율**을 계산하고, 핵심 변동 요약 문서(`Consensus_Diff_*.md`)를 생성합니다.

3. **증권사 리포트 수집 및 자동 텍스트 변환** (`download_naver_research.py` & `run_pipeline.py` 내 내장 변환기)
   * 네이버 증권 리서치 게시판에서 지정한 주간 범위의 리포트를 자동 검색하여 `research/섹터/reports/`에 PDF를 자동 정리합니다.
   * `pypdf` 라이브러리를 활용하여 다운로드된 최신 PDF를 프로그램으로 파싱 가능한 **텍스트(`.txt`) 파일로 자동 일괄 변환**합니다. (AI 분석의 정성 데이터로 즉시 활용 가능)

4. **[NEW] 밸류에이션 비교 테이블 자동화** (`valuation_capturer.py`)
   * Valley.town 사이트에 로그인하여 지정한 밸류에이션 지표(PER, PBR, PSR, P/FCF 등) 차트 카드를 정확히 크롭(Crop) 캡쳐합니다.
   * `Stocks_Valuation.json`에 설정된 섹터 분류를 토대로 **엑셀 워크북(`Stocks_Valuation.xlsx`) 내에 시트별로 분리 및 생성**하여 날짜별로 이미지를 차례대로 자동 삽입합니다. (동적 컬럼 매핑 지원)
   * direct URL 접속 실패 시 검색 및 자동완성 탐색으로 자동 리다이렉트하는 **Fallback 탐색 로직**을 내장하여 안전성이 뛰어납니다.

5. **마스터 룰북 및 요약 가이드** (`Consensus_Tracking_Master_Rule.md`)
   * AI 에이전트 분석용 통합 가이드라인입니다. 5개 핵심 섹터별 상세 모니터링 변수와 결과물 양식(YYMMDD_섹터_update.md) 템플릿을 명확하게 정의하고 있습니다.

---

## 📂 파일 구조 (Directory Structure)

```text
📦 Consensus_tracking
 ┣ 📜 run_pipeline.py                 # 🚀 통합 자동화 파이프라인 스크립트
 ┣ 📜 track_consensus.py             # 주간 컨센서스 크롤링 스크립트
 ┣ 📜 download_naver_research.py     # 네이버 증권 PDF 리포트 다운로드 스크립트
 ┣ 📜 compare_consensus.py           # 주간 컨센서스 변동 추출 및 비교 스크립트
 ┣ 📜 valuation_capturer.py          # 📊 [NEW] 밸류에이션 차트 자동 캡쳐 및 엑셀 삽입 스크립트
 ┣ 📜 dart_disclosure_capturer.py    # 🏢 [NEW] Open DART 기업 공시 취합 및 엑셀 저장 스크립트
 ┣ 📜 Consensus_Tracking_Master_Rule.md # 📕 통합 분석 가이드 & 마스터 룰북
 ┣ 📜 stocks.json                    # 모니터링 대상 5개 섹터 및 종목코드 리스트
 ┣ 📜 Stocks_Valuation.json          # 📊 [NEW] 밸류에이션 수집 대상 섹터 및 종목 리스트
 ┣ 📜 credentials.json               # 🔑 [NEW] Valley AI 로그인 계정 정보 (Git 제외)
 ┣ 📜 README.md                      # 프로그램 사용 설명서
 ┣ 📜 .gitignore                     # Git 제외 설정 (엑셀 파일, 개인 정보, 대용량 PDF 등)
 ┣ 📂 data                            # 수집 원본 데이터
 ┃ ┣ 📂 consensus                     # 컨센서스 Excel 원본
 ┃ ┃ ┗ 📂 diffs                       # 주간 컨센서스 변화 Markdown
 ┃ ┣ 📂 market                        # 주간 가격 스냅샷 CSV
 ┃ ┗ 📂 reference                     # DART, 밸류에이션 Excel
 ┣ 📂 research                        # 섹터별 리서치 산출물
 ┃ ┗ 📂 [섹터]
 ┃   ┣ 📂 reports                     # 다운로드 PDF 및 변환 TXT (Git 제외)
 ┃   ┣ 📂 consensus                   # 섹터별 컨센서스 Markdown
 ┃   ┗ 📂 updates                     # 최종 주간 업데이트 Markdown
 ┣ 📂 templates                       # 업데이트 문서 템플릿
 ┗ 📜 project_paths.py                # 저장 경로 단일 정의
```

---

## 💻 사용 방법 (Usage)

### 1. 최초 환경 구성 (데스크탑/노트북 공통)
필요한 라이브러리를 설치하고 브라우저 바이너리를 설치합니다.
```bash
pip install pandas beautifulsoup4 requests openpyxl playwright pypdf pykrx
playwright install
```

### 2. [NEW] Valley.town 로그인 정보 구성
`credentials.json` 파일을 작업 경로 루트에 만들고 로그인 정보를 기입합니다. (이 파일은 `.gitignore`에 등록되어 GitHub에 절대 올라가지 않습니다.)
```json
{
  "email": "YOUR_VALLEY_TOWN_EMAIL",
  "password": "YOUR_VALLEY_TOWN_PASSWORD"
}
```

### 3. 밸류에이션 차트 수집 실행
아래 명령어를 통해 밸류에이션 지표 차트들을 시트별로 수집해 엑셀로 자동 정리합니다.
```bash
# 기본 실행 (PER 지표 캡쳐 진행)
python valuation_capturer.py

# 특정 다른 지표(PBR, PSR, P/FCF 등)를 골라 캡쳐할 때
python valuation_capturer.py --metric PBR

# 브라우저 실행 화면을 직접 모니터링하며 작동시키고 싶을 때 (디버그용)
python valuation_capturer.py --metric PSR --headed
```

### 4. [NEW] Open DART 기업 공시 수집 실행
공시 시스템(Open DART)에서 국내 특정 기업들의 공시 기록 목록을 수집하여 엑셀 파일(`data/reference/DART_Disclosures.xlsx`)로 저장합니다.
```bash
# 기본 실행 (삼성전자, 삼성전기의 2026년 5월 공시 목록 수집)
python dart_disclosure_capturer.py

# 특정 날짜 범위를 직접 지정해 수집할 때 (YYYYMMDD)
python dart_disclosure_capturer.py --start 20260501 --end 20260531

# Stocks_Valuation.json에 등록된 모든 국내(KR) 기업의 공시를 수집할 때
python dart_disclosure_capturer.py --all-stocks

# 특정 Open DART API Key를 입력해 실행할 때
python dart_disclosure_capturer.py --apikey YOUR_API_KEY
```

### 5. 주간 업데이트 워크플로우
주간 업데이트는 수집, 분석·작성, 검증·배포의 세 단계로 나뉩니다. 출력 양식의 단일 기준은 `변수 변화 추적 프롬프트_V1.md`이며, 작성 시 `templates/weekly_sector_update_template.md`의 1~5번 구조를 유지합니다. 마켓데이터는 `3-1. 주간 시황 및 가격 해석`에만 추가합니다.

먼저 수집 단계만 실행합니다.
```bash
# 특정 주간의 컨센서스, 리포트, PDF 텍스트, 비교표, 마켓데이터 수집
python run_pipeline.py --start 260720 --end 260726 --skip-git
```

그 다음 AI 에이전트가 `AGENTS.md`의 필수 입력 순서에 따라 섹터별 `YYMMDD_섹터_update.md`를 작성합니다. 마지막으로 검증을 통과한 경우에만 배포합니다.
```bash
# 모든 섹터 업데이트의 고정 양식과 source_from 검증
python validate_weekly_updates.py --date 260726

# 재수집 없이 검증, 커밋, 푸시: 검증 실패 시 커밋과 푸시가 중단됨
python run_pipeline.py --publish-only --end 260726
```

주간 업데이트의 `tags`는 [Google Drive Tags 규칙](https://drive.google.com/file/d/1fdex_lDKHT2Q-xyuxYalC0l8G6jDhOKp)을 기준으로 하며, 로컬 검증용 매핑은 `tag_rules.json`에 보관합니다. 태그 규칙을 변경하면 이 파일도 함께 갱신해야 합니다.

### 6. 주간 시황 및 가격 스냅샷 수집
추적 종목의 주가 수익률, 벤치마크 대비 초과수익률, 52주 고점 대비 하락률, 거래대금 과열 여부를 수집합니다. 결과는 `data/market/` 폴더에 저장됩니다.
```bash
# 오늘 기준 수집
python collect_market_snapshot.py

# 특정 기준일 수집 (YYMMDD)
python collect_market_snapshot.py --date 260724
```

생성 파일:
```text
data/market/YYMMDD_market_snapshot.csv
data/market/YYMMDD_sector_market_summary.csv
```

`price_signal`은 가격 국면을 단순 규칙으로 분류합니다. `overheated`는 매도 신호가 아니라 컨센서스 개선 대비 가격 선반영 가능성을 별도로 점검해야 한다는 의미입니다.

참고: pykrx 지수 API가 환경에 따라 실패할 수 있어, 벤치마크 수익률은 필요 시 ETF 프록시를 사용합니다. KOSPI는 `KODEX 200(069500)`, KOSDAQ은 `KODEX 코스닥150(229200)`을 사용하며 CSV의 `benchmark` 컬럼에 프록시 여부가 표시됩니다.

---

## 🔄 데스크탑 & 노트북 교대 작업 워크플로우 (Multi-Device Git Flow)

두 대의 기기를 번갈아 가며 작업할 때는 아래의 규칙을 필수로 준수해야 코드가 꼬이는 것을 방지할 수 있습니다.

1. **작업 시작 전**: 무조건 원격 GitHub의 최신 변경 내용을 로컬로 반영합니다.
   ```bash
   git pull origin main
   ```
2. **작업 및 파이프라인 실행**:
   * `python run_pipeline.py`를 실행하면 데이터 수집 후 결과물이 자동으로 GitHub에 업로드(Push)됩니다.
   * 만약 스크립트를 돌리지 않고 코드를 손으로 직접 고쳤다면, 아래 깃 명령어로 GitHub에 올려주어야 합니다.
     ```bash
     git add .
     git commit -m "작업 내용 요약"
     git push origin main
     ```
3. **용량 및 보안 안내**: `.gitignore` 설정으로 무거운 PDF 폴더(`naver_reports/`), 로그인 인증 정보(`credentials.json`), 차트가 삽입된 엑셀(`*.xlsx`) 등은 GitHub에 올라가지 않고 로컬에만 보존됩니다. 따라서 가벼운 코드와 최종 마크다운 보고서 위주로 연동되어 속도가 매우 빠르고 안전합니다.

