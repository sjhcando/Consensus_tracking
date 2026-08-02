import os
import sys
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from pypdf import PdfReader
from project_paths import (
    CONSENSUS_DIFF_DIR,
    MARKET_DATA_DIR,
    sector_consensus_dir,
    sector_reports_dir,
    sector_updates_dir,
)

def get_date_range(days=6):
    today = datetime.now()
    end_date = today.strftime("%y%m%d")
    start_date = (today - timedelta(days=days)).strftime("%y%m%d")
    return start_date, end_date

def run_command(args_list):
    print(f"\n[Running Command] {' '.join(args_list)}...")
    try:
        res = subprocess.run(args_list, check=True, capture_output=True, text=True, errors='replace')
        print(res.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def load_sectors():
    import json

    with open("stocks.json", "r", encoding="utf-8") as f:
        return list(json.load(f).keys())


def stage_weekly_outputs(end_date, sectors):
    print("Weekly outputs are stored in Google Drive and are not staged in this repository.")
    return True


def publish_weekly_outputs(end_date):
    print("\n[Publish] 주간 업데이트 형식 검증...")
    if not run_command([sys.executable, "validate_weekly_updates.py", "--date", end_date]):
        print("검증 실패: 업데이트 파일을 수정한 뒤 다시 실행하십시오. Git 커밋과 푸시는 수행하지 않습니다.")
        return False

    stage_weekly_outputs(end_date, load_sectors())
    print("Validation passed. Google Drive sync is the publication mechanism for weekly outputs.")
    return True

def convert_new_pdfs(start_date, end_date):
    print("\n[Converting New PDFs to TXT]...")
    converted_count = 0
    
    # Read sectors from stocks.json to find their respective folders
    import json
    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            sectors = list(json.load(f).keys())
    except Exception:
        sectors = ["반도체", "방산", "전력기기", "조선", "전기전자"]
        
    for sector in sectors:
        reports_dir = sector_reports_dir(sector)
        if not reports_dir.exists():
            continue
        for root, _, files in os.walk(reports_dir):
            for f in files:
                if f.endswith(".pdf"):
                    file_date = f[:6]
                    if start_date <= file_date <= end_date:
                        pdf_path = os.path.join(root, f)
                        txt_name = f.replace(".pdf", ".txt")
                        txt_path = os.path.join(root, txt_name)
                    
                        if not os.path.exists(txt_path):
                            print(f"Converting: {f} -> {txt_name}")
                            try:
                                reader = PdfReader(pdf_path)
                                text = ""
                                for i, page in enumerate(reader.pages):
                                    text += f"\n--- Page {i+1} ---\n"
                                    page_text = page.extract_text()
                                    if page_text:
                                        text += page_text
                                with open(txt_path, 'w', encoding='utf-8') as tf:
                                    tf.write(text)
                                converted_count += 1
                            except Exception as e:
                                print(f"Failed to convert {f}: {e}")
                        else:
                            print(f"Already converted: {txt_name}")
                        
    print(f"PDF to TXT conversion completed. Total converted: {converted_count}")

def main():
    parser = argparse.ArgumentParser(description="투자 종목 주간 Consensus Tracking 자동화 파이프라인")
    parser.add_argument("--days", type=int, default=5, help="네이버 리포트 다운로드 기간 (오늘 기준 과거 일수, 기본값: 5일)")
    parser.add_argument("--start", type=str, default=None, help="리포트 다운로드 시작일 (YYMMDD)")
    parser.add_argument("--end", type=str, default=None, help="리포트 다운로드 종료일 (YYMMDD)")
    parser.add_argument("--skip-market-data", action="store_true", help="마켓데이터 수집 단계 건너뛰기")
    parser.add_argument("--skip-git", action="store_true", help="Legacy option; weekly outputs are stored in Google Drive")
    parser.add_argument("--publish-only", action="store_true", help="수집 없이 Google Drive 주간 업데이트 검증")
    
    args = parser.parse_args()
    
    if args.publish_only:
        if not args.end:
            parser.error("--publish-only requires --end in YYMMDD format")
        end_date = args.end
        if not publish_weekly_outputs(end_date):
            sys.exit(1)
        print(f"\n{end_date} 주간 업데이트 배포 완료!")
        return

    # 1. 날짜 범위 결정
    if args.start and args.end:
        start_date = args.start
        end_date = args.end
    elif args.start or args.end:
        parser.error("--start and --end must be provided together during collection")
    else:
        start_date, end_date = get_date_range(args.days)
        
    print("=" * 60)
    print(f"주간 Consensus Tracking 파이프라인 시작")
    print(f"분석 기간: {start_date} ~ {end_date}")
    print("=" * 60)
    
    # 2. Step 1: 컨센서스 데이터 추출
    print("\n[Step 1] 주간 컨센서스 데이터 크롤링 및 엑셀/마크다운 생성...")
    if not run_command([sys.executable, "track_consensus.py", "--date", end_date]):
        print("Step 1 실패. 파이프라인을 종료합니다.")
        sys.exit(1)
        
    # 3. Step 2: 네이버 애널리스트 리포트 다운로드
    print(f"\n[Step 2] 네이버 애널리스트 리포트 다운로드 ({start_date} ~ {end_date})...")
    # download_naver_research.py의 download_reports를 subprocess로 실행
    # 코드의 메인 실행 블록을 호출하기 위해 subprocess 인자로 전달
    # download_naver_research.py는 직접 실행 시 START_DATE, END_DATE 상수를 참조하므로 임시 환경변수나 인자로 전달하거나,
    # python 코드를 문자열로 전달해 실행합니다.
    python_code = f"""
import download_naver_research
download_naver_research.download_reports(start_date='{start_date}', end_date='{end_date}')
"""
    if not run_command([sys.executable, "-c", python_code]):
        print("Step 2 실패. 파이프라인을 종료합니다.")
        sys.exit(1)
        
    # 4. Step 3: PDF 파일 자동 텍스트 변환
    convert_new_pdfs(start_date, end_date)
    
    # 5. Step 4: 컨센서스 변화 비교 분석표 생성
    print("\n[Step 4] 주간 컨센서스 변화율 비교 마크다운 생성...")
    if not run_command([sys.executable, "compare_consensus.py"]):
        print("Step 4 실패. 비교 파일 생성 생략.")
        
    # 6. Step 5: Weekly market snapshot
    if not args.skip_market_data:
        print(f"\n[Step 5] 주간 시황 및 가격 스냅샷 수집 ({end_date})...")
        if not run_command([sys.executable, "collect_market_snapshot.py", "--date", end_date]):
            print("Step 5 실패. 파이프라인을 종료합니다.")
            sys.exit(1)

    # 7. Step 6: Mandatory update validation for Google Drive outputs
    if not publish_weekly_outputs(end_date):
        sys.exit(1)
        
    print("\n" + "=" * 60)
    print("파이프라인 실행 완료!")
    print(f"새로운 보고서 텍스트, 컨센서스 요약본 및 마켓데이터가 준비되었습니다.")
    if args.skip_git:
        print("업데이트 작성 후 'python validate_weekly_updates.py --date " + end_date + "'를 실행하십시오.")
    print("=" * 60)

if __name__ == "__main__":
    main()
