import json
import time
from datetime import datetime
import pandas as pd
from playwright.sync_api import sync_playwright

def load_sectors():
    with open('stocks.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    sectors = {}
    for sector, stocks in data.items():
        sectors[sector] = [(stock['name'], stock['ticker']) for stock in stocks]
    return sectors

def extract_table(page, index):
    return page.evaluate(f'''(index) => {{
        const tables = document.querySelectorAll('table');
        if (tables.length <= index) return null;
        const table = tables[index];
        const result = [];
        table.querySelectorAll('tr').forEach(tr => {{
            const row = [];
            tr.querySelectorAll('th, td').forEach(td => {{
                let text = td.innerText.trim().replace(/\\n/g, ' ');
                row.push(text);
            }});
            if (row.length > 0) result.push(row);
        }});
        return result;
    }}''', index)

def format_df(raw_data, stock_name):
    if not raw_data or len(raw_data) < 2:
        return None
        
    df = pd.DataFrame(raw_data)
    df = df.dropna(how='all')
    
    if len(df) > 1:
        cols = []
        for i in range(len(df.columns)):
            col = df.iloc[0, i] if pd.notna(df.iloc[0, i]) else ""
            if i == 0:
                cols.append("항목")
            else:
                cols.append(col)
        
        df = df[1:].copy()
        df.columns = cols
        
        # Add stock name as the first column
        df.insert(0, "종목명", stock_name)
        
        # Convert numeric strings to actual numbers
        for col in df.columns[2:]:
            orig_col = df[col].copy()
            df[col] = df[col].astype(str).str.replace(',', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(orig_col)
            
        # Calculate % difference vs 1개월전
        # The columns are ['종목명', '항목', '2026/05/22', '1개월전', '3개월전', '6개월전', '1년전']
        if "1개월전" in df.columns:
            current_col = df.columns[2]
            prev_1m_col = "1개월전"
            
            def calc_diff(row):
                try:
                    curr = float(row[current_col])
                    prev = float(row[prev_1m_col])
                    if prev == 0:
                        return None
                    return (curr - prev) / abs(prev) * 100
                except:
                    return None
                    
            df["1개월전 대비 증감율(%)"] = df.apply(calc_diff, axis=1)
            
    return df

def get_consensus_data(ticker, stock_name, page):
    url = f"https://comp.fnguide.com/SVO2/ASP/SVD_Consensus.asp?pGB=1&gicode={ticker}&cID=&MenuYn=Y&ReportGB=&NewMenuID=108&stkGb=701"
    
    annual_df = None
    quarter_df = None

    page.goto(url, wait_until="networkidle")
    time.sleep(3)
    
    # Extract Annual Data
    raw_annual = extract_table(page, 1)
    annual_df = format_df(raw_annual, stock_name)
    
    # Click Quarterly
    try:
        buttons = page.locator("a:has-text('분기')").all()
        if len(buttons) >= 2:
            buttons[1].click()
        elif len(buttons) == 1:
            buttons[0].click()
            
        time.sleep(2)
        raw_quarter = extract_table(page, 1)
        quarter_df = format_df(raw_quarter, stock_name)
        
    except Exception as e:
        print(f"Error extracting quarter data for {stock_name}: {e}")
            
    return annual_df, quarter_df

def main():
    sectors_dict = load_sectors()
    sector_results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for sector, stocks in sectors_dict.items():
            annual_dfs = []
            quarter_dfs = []
            
            for stock_name, ticker in stocks:
                print(f"Fetching data for {stock_name} ({ticker})...")
                annual, quarterly = get_consensus_data(ticker, stock_name, page)
                
                if annual is not None and not annual.empty:
                    annual_dfs.append(annual)
                if quarterly is not None and not quarterly.empty:
                    quarter_dfs.append(quarterly)
                    
            sector_results[f"{sector}_연간"] = pd.concat(annual_dfs, ignore_index=True) if annual_dfs else None
            sector_results[f"{sector}_분기"] = pd.concat(quarter_dfs, ignore_index=True) if quarter_dfs else None

        browser.close()
        
    yymmdd = datetime.now().strftime("%y%m%d")
    filename = f"{yymmdd}_Sector_consensus.xlsx"
    with pd.ExcelWriter(filename) as writer:
        wrote_any = False
        for sheet_name, df in sector_results.items():
            if df is not None and not df.empty:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"{sheet_name} data saved to Excel.")
                wrote_any = True
                
        if not wrote_any:
            pd.DataFrame(["No data found"]).to_excel(writer, sheet_name="Empty", index=False)

    print(f"Done. Saved to {filename}")
    
    # Save to Markdown
    def filter_for_md(df):
        if df is None or df.empty:
            return None
        # 행 기준 필터링
        filtered = df[df['항목'].isin(['매출액', '영업이익'])].copy()
        
        # 열 기준 필터링
        if len(df.columns) > 2 and "1개월전" in df.columns and "1개월전 대비 증감율(%)" in df.columns:
            current_date_col = df.columns[2]
            cols_to_keep = ['종목명', '항목', current_date_col, '1개월전', '1개월전 대비 증감율(%)']
            filtered = filtered[[c for c in cols_to_keep if c in filtered.columns]]
            
            # 숫자 포맷팅 (소수점 2자리 및 천단위 콤마)
            if "1개월전 대비 증감율(%)" in filtered.columns:
                filtered["1개월전 대비 증감율(%)"] = filtered["1개월전 대비 증감율(%)"].apply(
                    lambda x: f"{x:.2f}%" if pd.notna(x) and isinstance(x, (int, float)) else x
                )
                
            for col in [current_date_col, '1개월전']:
                if col in filtered.columns:
                    filtered[col] = filtered[col].apply(
                        lambda x: f"{x:,.0f}" if pd.notna(x) and isinstance(x, (int, float)) else x
                    )
            
        return filtered

    for sector in sectors_dict.keys():
        md_filename = f"{yymmdd}_{sector}_consensus.md"
        with open(md_filename, "w", encoding="utf-8") as md_file:
            md_file.write(f"# {sector} 컨센서스 요약 ({yymmdd})\n\n")
            
            annual_df = filter_for_md(sector_results.get(f"{sector}_연간"))
            if annual_df is not None and not annual_df.empty:
                md_file.write("## 연간 (Annual)\n\n")
                md_file.write(annual_df.to_markdown(index=False) + "\n\n")
                
            quarter_df = filter_for_md(sector_results.get(f"{sector}_분기"))
            if quarter_df is not None and not quarter_df.empty:
                md_file.write("## 분기 (Quarterly)\n\n")
                md_file.write(quarter_df.to_markdown(index=False) + "\n\n")
                
        print(f"Saved markdown to {md_filename}")

if __name__ == "__main__":
    main()
