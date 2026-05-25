# Consensus Tracking

투자 종목 및 섹터에 대한 컨센서스(실적 전망치)의 변화를 추출하고, 이러한 컨센서스 변화의 원인을 심층 분석할 수 있도록 증권사 리서치 리포트를 자동 추출하는 프로그램입니다.

## 기능 (Features)

1. **섹터별 컨센서스 데이터 추출** (`track_consensus.py`)
   * 에프앤가이드(FnGuide) 웹페이지를 크롤링하여 `stocks.json`에 등록된 섹터/종목들의 연간 및 분기별 실적 컨센서스(매출액, 영업이익) 변화 추출
   * 현재 시점과 1개월 전의 컨센서스를 비교하여 **증감률(%)**을 자동 계산
   * 결과를 엑셀(.xlsx) 파일 및 가독성 높은 마크다운(.md) 파일로 요약 출력

2. **네이버 증권 리포트(PDF) 자동 다운로드** (`download_naver_research.py`)
   * 네이버 증권 리서치(산업분석/종목분석) 게시판에서 설정한 기간(예: 최근 1달)의 리포트를 자동 검색
   * 분석 대상 섹터명 및 종목명 기반으로 필터링하여 원본 PDF 리포트 일괄 다운로드
   * 섹터별 폴더 생성 및 직관적인 파일명(`YYMMDD_분류_제목_증권사.pdf`)으로 자동 정리

3. **관심 종목 및 섹터 관리** (`stocks.json`)
   * 추적하고자 하는 섹터명과 소속 종목(기업명, 종목코드)을 구조화하여 관리하는 JSON 파일

## 파일 구조 (Directory Structure)

```text
📦 Consensus_tracking
 ┣ 📜 track_consensus.py          # 컨센서스 추적 및 요약 스크립트
 ┣ 📜 download_naver_research.py  # 네이버 증권 리포트 다운로드 스크립트
 ┣ 📜 stocks.json                 # 타겟 섹터 및 종목 리스트
 ┣ 📜 README.md                   # 프로그램 설명서
 ┣ 📜 .gitignore                  # Git 제외 파일 설정
 ┣ 📜 [YYMMDD]_[섹터]_consensus.md # 생성된 섹터별 컨센서스 요약 파일 (예시)
 ┣ 📜 [YYMMDD]_[섹터]_update.md    # 생성된 섹터 투자 분석 종합 결과 (예시)
 ┗ 📂 naver_reports               # 다운로드된 증권사 PDF 리포트 폴더 (Git 제외 권장)
```

## 사용 방법 (Usage)

1. **환경 설정**: Python 환경에 필수 라이브러리(`playwright`, `pandas`, `requests`, `beautifulsoup4` 등)를 설치합니다.
   * `playwright`의 경우 설치 후 `playwright install` 명령어를 통해 브라우저 바이너리를 설치해야 합니다.
2. **종목 설정**: `stocks.json` 파일을 열어 추적할 섹터와 종목코드(티커)를 수정합니다.
3. **컨센서스 추출**: `python track_consensus.py`를 실행하여 최근 컨센서스 수치와 변화율을 파악합니다.
4. **리포트 수집**: `python download_naver_research.py`를 실행하여 해당 섹터의 최근 증권사 리포트(PDF)들을 수집합니다.
5. **분석 및 종합**: 요약된 컨센서스 마크다운 파일과 수집된 PDF 원문을 기반으로, 실적 상향/하향의 근거와 향후 추적해야 할 핵심 변수를 종합 분석할 수 있습니다. (LLM 도구를 결합하여 자동 요약을 수행할 수 있습니다.)
