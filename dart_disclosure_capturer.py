import os
import sys
import json
import argparse
import urllib.request
import urllib.parse
import zipfile
import io
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd

def get_dart_corp_codes(api_key, target_stock_codes):
    """
    Downloads the DART corporate code list ZIP, parses the XML,
    and returns a mapping of stock_code -> DART corp_code.
    """
    url = f"https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={api_key}"
    print("Downloading DART corporate code lookup zip...")
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            zip_data = response.read()
    except Exception as e:
        print(f"Failed to download corporate code map from DART: {e}")
        sys.exit(1)
        
    print("Parsing CORPCODE.xml...")
    try:
        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            xml_content = z.read("CORPCODE.xml")
        root = ET.fromstring(xml_content)
    except Exception as e:
        print(f"Failed to extract and parse CORPCODE.xml: {e}")
        sys.exit(1)
        
    code_map = {}
    for entry in root.findall("list"):
        stock_code = entry.find("stock_code").text
        corp_code = entry.find("corp_code").text
        corp_name = entry.find("corp_name").text
        
        if stock_code and stock_code.strip() in target_stock_codes:
            code_map[stock_code.strip()] = {
                "corp_code": corp_code.strip(),
                "corp_name": corp_name.strip()
            }
            
    return code_map

def fetch_disclosures(api_key, corp_code, bgn_de, end_de):
    """
    Queries the DART list API for a corporate code within a date range.
    """
    url = "https://opendart.fss.or.kr/api/list.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bgn_de": bgn_de,
        "end_de": end_de,
        "page_no": "1",
        "page_count": "100"
    }
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    
    req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read().decode("utf-8")
            result = json.loads(res_data)
            
            if result.get("status") == "000":
                return result.get("list", [])
            elif result.get("status") == "013":
                # status 013 is 'No data found', which is expected for some periods
                return []
            else:
                print(f"DART API Error ({corp_code}): {result.get('message')} (status: {result.get('status')})")
                return []
    except Exception as e:
        print(f"Request failed for corp_code {corp_code}: {e}")
        return []

def load_kr_stocks():
    """
    Loads Korean stock tickers from Stocks_Valuation.json.
    """
    stocks_path = "Stocks_Valuation.json"
    if not os.path.exists(stocks_path):
        # Fallback to hardcoded list if settings file is not found
        return {"005930": "삼성전자", "009150": "삼성전기"}
        
    with open(stocks_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    kr_stocks = {}
    for sector, stocks in data.items():
        for stock in stocks:
            # We filter for Korean stocks (country is KR, or ticker is numeric 6-digits)
            ticker = stock.get("ticker", "")
            name = stock.get("name", "")
            country = stock.get("country", "")
            
            # Clean ticker if needed
            if ticker.startswith("A") and len(ticker) == 7:
                ticker = ticker[1:]
                
            if country == "KR" or (ticker.isdigit() and len(ticker) == 6):
                kr_stocks[ticker] = name
                
    return kr_stocks

def main():
    parser = argparse.ArgumentParser(description="Open DART 공시 정보 수집 프로그램")
    parser.add_argument("--apikey", type=str, default="bde08001b22df5e4333cb9b0a7453377d3afffe4", help="DART API 인증키")
    parser.add_argument("--start", type=str, default="20260501", help="검색 시작일 (YYYYMMDD, 기본값: 20260501)")
    parser.add_argument("--end", type=str, default="20260531", help="검색 종료일 (YYYYMMDD, 기본값: 20260531)")
    parser.add_argument("--all-stocks", action="store_true", help="Stocks_Valuation.json에 등록된 모든 국내 종목 수집")
    args = parser.parse_args()
    
    # Target stock selection
    if args.all-stocks:
        target_stocks = load_kr_stocks()
        print(f"Loaded {len(target_stocks)} KR stocks from Stocks_Valuation.json")
    else:
        # Default target list as requested
        target_stocks = {
            "005930": "삼성전자",
            "009150": "삼성전기"
        }
    
    # 1. Get DART 8-digit corporate codes
    code_map = get_dart_corp_codes(args.apikey, list(target_stocks.keys()))
    
    all_disclosures = []
    
    # 2. Fetch disclosures
    for stock_code, info in code_map.items():
        corp_code = info["corp_code"]
        corp_name = info["corp_name"]
        print(f"\nFetching disclosures: {corp_name} ({stock_code}) from {args.start} to {args.end}...")
        
        list_data = fetch_disclosures(args.apikey, corp_code, args.start, args.end)
        for item in list_data:
            raw_date = item.get("rcept_dt", "")
            formatted_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}" if len(raw_date) == 8 else raw_date
            
            all_disclosures.append({
                "기업명": item.get("corp_name", corp_name),
                "접수일자": formatted_date,
                "보고서명": item.get("report_nm", "")
            })
            
    # 3. Create DataFrame and Output Excel
    df = pd.DataFrame(all_disclosures)
    
    if df.empty:
        print("\nNo disclosures found for the selected period.")
        df = pd.DataFrame(columns=["기업명", "접수일자", "보고서명"])
        
    df = df[["기업명", "접수일자", "보고서명"]]
    
    output_dir = "컨센서스"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "DART_Disclosures.xlsx")
    
    # Write to Excel
    df.to_excel(output_path, index=False)
    print(f"\nSuccess! Saved {len(df)} disclosures to: {output_path}")

if __name__ == "__main__":
    main()
