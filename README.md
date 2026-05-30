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
   * 네이버 증권 리서치 게시판에서 지정한 주간 범위의 리포트를 자동 검색하여 섹터별 폴더로 PDF를 자동 정리합니다.
   * `pypdf` 라이브러리를 활용하여 다운로드된 최신 PDF를 프로그램으로 파싱 가능한 **텍스트(`.txt`) 파일로 자동 일괄 변환**합니다. (AI 분석의 정성 데이터로 즉시 활용 가능)

4. **마스터 룰북 및 요약 가이드** (`Consensus_Tracking_Master_Rule.md`)
   * AI 에이전트 분석용 통합 가이드라인입니다. 5개 핵심 섹터별 상세 모니터링 변수와 결과물 양식(YYMMDD_섹터_update.md) 템플릿을 명확하게 정의하고 있습니다.

---

## 📂 파일 구조 (Directory Structure)

```text
📦 Consensus_tracking
 ┣ 📜 run_pipeline.py                 # 🚀 통합 자동화 파이프라인 스크립트
 ┣ 📜 track_consensus.py             # 주간 컨센서스 크롤링 스크립트
 ┣ 📜 download_naver_research.py     # 네이버 증권 PDF 리포트 다운로드 스크립트
 ┣ 📜 compare_consensus.py           # 주간 컨센서스 변동 추출 및 비교 스크립트
 ┣ 📜 Consensus_Tracking_Master_Rule.md # 📕 통합 분석 가이드 & 마스터 룰북
 ┣ 📜 stocks.json                    # 모니터링 대상 5개 섹터 및 종목코드 리스트
 ┣ 📜 README.md                      # 프로그램 사용 설명서
 ┣ 📜 .gitignore                     # Git 제외 설정 (대용량 PDF 폴더 등 제외)
 ┣ 📜 Consensus_Diff_[날짜]_[날짜].md # 주간 컨센서스 변동량 결과 분석표 (자동 생성)
 ┣ 📜 [YYMMDD]_[섹터]_consensus.md   # 이번 주 섹터별 최종 수집 데이터 요약 (자동 생성)
 ┣ 📜 [YYMMDD]_[섹터]_update.md      # 최종 발행된 섹터별 종합 투자 분석 보고서
 ┗ 📂 naver_reports                  # 다운로드된 PDF 및 변환된 TXT 리포트 (Git 제외)
```

---

## 💻 사용 방법 (Usage)

### 1. 최초 환경 구성 (데스크탑/노트북 공통)
필요한 라이브러리를 설치하고 브라우저 바이너리를 설치합니다.
```bash
pip install pandas beautifulsoup4 requests openpyxl playwright pypdf
playwright install
```

### 2. 자동화 파이프라인 원클릭 실행
매주 주말, 아래 명령어를 실행하여 크롤링부터 리포트 텍스트 변환 및 깃허브 업로드까지 논스톱으로 처리합니다.
```bash
# 기본 실행 (과거 5일간의 리포트 다운로드 및 Git 업로드 자동 진행)
python run_pipeline.py

# 특정 주간 날짜를 직접 설정하여 다운로드할 때 (YYMMDD)
python run_pipeline.py --start 260525 --end 260530

# Git 원격 푸시 단계를 건너뛰고 싶을 때
python run_pipeline.py --skip-git
```

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
3. **용량 관련 안내**: `.gitignore` 설정으로 무거운 PDF 폴더(`naver_reports/`)는 GitHub에 올라가지 않고 로컬에만 보존됩니다. 따라서 가벼운 코드와 최종 마크다운 보고서 위주로 연동되어 속도가 매우 빠릅니다.

