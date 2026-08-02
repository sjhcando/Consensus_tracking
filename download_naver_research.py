import os
import re
import json
import requests
import urllib.parse
from bs4 import BeautifulSoup
from project_paths import sector_reports_dir

def clean_filename(filename):
    # 특수문자 제거 및 공백 정리
    return re.sub(r'[\\/*?:"<>|]', " ", filename).strip()

def download_reports(start_date="260501", end_date="260524"):
    # stocks.json에서 섹터(산업분류) 목록 읽어오기
    with open('stocks.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # 네이버 증권 업종명 매핑 (없으면 원래 이름 사용)
    NAVER_UPJONG_MAP = {
        "방산": "기타",
        "전력기기": "기계"
    }
        
    targets = []
    
    # 1. 산업분석 리포트 대상 추가
    for sector, stocks in data.items():
        query_sector = NAVER_UPJONG_MAP.get(sector, sector)
        encoded_sector = urllib.parse.quote(query_sector.encode('euc-kr'))
        url = f"https://finance.naver.com/research/industry_list.naver?searchType=upjong&upjong={encoded_sector}"
        
        strict_filter = (query_sector != sector)
        keywords = [sector] + [s['name'] for s in stocks]
        
        targets.append({
            "name": f"{sector} (산업분석)", 
            "url": url,
            "strict_filter": strict_filter,
            "keywords": keywords,
            "sector_dir": sector
        })
        
        # 2. 종목분석 리포트 대상 추가
        for stock in stocks:
            stock_name = stock['name']
            ticker = stock['ticker']
            
            # 티커 포맷 (예: A005930)에서 맨 앞 영문자 제외한 6자리 추출
            item_code = ticker[1:] if ticker[0].isalpha() else ticker
            
            company_url = f"https://finance.naver.com/research/company_list.naver?searchType=itemCode&itemCode={item_code}"
            
            targets.append({
                "name": f"{stock_name} (종목분석)",
                "url": company_url,
                "strict_filter": False,
                "keywords": [],
                "sector_dir": sector
            })
        
    for target in targets:
        print(f"--- Fetching for {target['name']} ---")
        
        # 섹터명 하위 폴더 생성
        sector_path = sector_reports_dir(target["sector_dir"])
        os.makedirs(sector_path, exist_ok=True)
        
        page = 1
        keep_going = True
        
        while keep_going:
            url = f"{target['url']}&page={page}"
            r = requests.get(url)
            r.encoding = 'euc-kr'
            soup = BeautifulSoup(r.text, 'html.parser')
            
            table = soup.select_one("table.type_1")
            if not table:
                print("No table found")
                break
                
            rows = table.find_all("tr")
            found_any = False
            for row in rows:
                cols = row.find_all("td")
                # 정상적인 데이터 행은 td가 6개(분류, 제목, 증권사, 첨부, 작성일, 조회수) 존재합니다.
                if len(cols) < 5:
                    continue
                    
                cat = cols[0].text.strip()
                title_elem = cols[1].find("a")
                title = title_elem.text.strip() if title_elem else cols[1].text.strip()
                broker = cols[2].text.strip()
                
                # '기타' 처럼 넓은 범위의 업종으로 검색한 경우, 제목에 키워드(섹터명 또는 종목명)가 있는지 필터링
                if target['strict_filter']:
                    if not any(kw in title for kw in target['keywords']):
                        continue
                
                found_any = True
                
                pdf_link_elem = cols[3].find("a")
                pdf_url = pdf_link_elem['href'] if pdf_link_elem else None
                
                date_str = cols[4].text.strip() # e.g. "26.05.20"
                yymmdd = date_str.replace(".", "")
                
                # 날짜 조건 필터링 (내림차순 정렬 가정)
                if yymmdd > end_date:
                    # 종료일(가장 최신)보다 더 나중의 글이면 스킵
                    continue
                if yymmdd < start_date:
                    # 시작일(가장 과거)보다 이전 글로 넘어갔으면 더 이상 탐색할 필요 없음
                    keep_going = False
                    break
                
                if not pdf_url:
                    continue
                    
                # 파일명 생성 포맷: YYMMDD_분류_제목_증권사.pdf
                clean_title = clean_filename(title)
                clean_cat = clean_filename(cat)
                clean_broker = clean_filename(broker)
                
                filename = f"{yymmdd}_{clean_cat}_{clean_title}_{clean_broker}.pdf"
                filepath = os.path.join(str(sector_path), filename)
                
                if not os.path.exists(filepath):
                    print(f"Downloading: {filename}")
                    try:
                        pdf_resp = requests.get(pdf_url, stream=True)
                        with open(filepath, 'wb') as f:
                            for chunk in pdf_resp.iter_content(chunk_size=8192):
                                f.write(chunk)
                    except Exception as e:
                        print(f"Failed to download {pdf_url}: {e}")
                else:
                    print(f"Already exists: {filename}")
            
            # 한 페이지에 데이터가 없거나, 이전 달로 넘어갔으면 다음 섹터로
            if not found_any or not keep_going:
                break
                
            page += 1

if __name__ == "__main__":
    # 다운로드 받을 기간 설정 (YYMMDD 형식)
    START_DATE = "260525"
    END_DATE = "260530"
    print(f"다운로드 기간: {START_DATE} ~ {END_DATE}")
    download_reports(start_date=START_DATE, end_date=END_DATE)
