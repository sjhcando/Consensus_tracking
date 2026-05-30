import pandas as pd
import sys
import os

def filter_for_md(df):
    if df is None or df.empty:
        return None
    # Filter rows where the item is '매출액' or '영업이익'
    filtered = df[df['항목'].isin(['매출액', '영업이익'])].copy()
    
    # Filter columns and format
    if len(df.columns) > 2 and "1개월전" in df.columns:
        current_date_col = df.columns[2]
        cols_to_keep = ['종목명', '항목', current_date_col, '전주 Consensus', '전주 대비 증감율(%)', '1개월전', '1개월전 대비 증감율(%)']
        filtered = filtered[[c for c in cols_to_keep if c in filtered.columns]]
        
        # Format percentages and numbers
        for diff_col in ["전주 대비 증감율(%)", "1개월전 대비 증감율(%)"]:
            if diff_col in filtered.columns:
                filtered[diff_col] = filtered[diff_col].apply(
                    lambda x: f"{x:+.2f}%" if pd.notna(x) and isinstance(x, (int, float)) else ("" if pd.isna(x) else str(x))
                )
            
        for col in [current_date_col, '전주 Consensus', '1개월전']:
            if col in filtered.columns:
                filtered[col] = filtered[col].apply(
                    lambda x: f"{x:,.0f}" if pd.notna(x) and isinstance(x, (int, float)) else ("" if pd.isna(x) else str(x))
                )
        
    return filtered

def main():
    xl_file = "260530_Sector_consensus.xlsx"
    if not os.path.exists(xl_file):
        print(f"File {xl_file} not found.")
        sys.exit(1)
        
    xl = pd.ExcelFile(xl_file)
    sheets = xl.sheet_names
    
    # Group sheets by sector
    sectors = {}
    for s in sheets:
        if s == "Empty":
            continue
        parts = s.split('_')
        if len(parts) == 2:
            sector, period = parts
            if sector not in sectors:
                sectors[sector] = {}
            sectors[sector][period] = s
            
    for sector, sheet_map in sectors.items():
        md_filename = f"260530_{sector}_consensus.md"
        print(f"Writing to {md_filename}...")
        
        with open(md_filename, "w", encoding="utf-8") as md_file:
            md_file.write(f"# {sector} 컨센서스 요약 (260530)\n\n")
            
            if '연간' in sheet_map:
                df_annual = pd.read_excel(xl, sheet_name=sheet_map['연간'])
                df_annual_filtered = filter_for_md(df_annual)
                if df_annual_filtered is not None and not df_annual_filtered.empty:
                    md_file.write("## 연간 (Annual)\n\n")
                    md_file.write(df_annual_filtered.to_markdown(index=False) + "\n\n")
                    
            if '분기' in sheet_map:
                df_quarter = pd.read_excel(xl, sheet_name=sheet_map['분기'])
                df_quarter_filtered = filter_for_md(df_quarter)
                if df_quarter_filtered is not None and not df_quarter_filtered.empty:
                    md_file.write("## 분기 (Quarterly)\n\n")
                    md_file.write(df_quarter_filtered.to_markdown(index=False) + "\n\n")
                    
    print("Done!")

if __name__ == "__main__":
    main()
