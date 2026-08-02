import pandas as pd
import glob
import sys
import os
from project_paths import CONSENSUS_DATA_DIR, CONSENSUS_DIFF_DIR

def compare_excel(old_file, new_file):
    print(f"비교: {old_file} vs {new_file}")
    
    old_xls = pd.ExcelFile(old_file)
    new_xls = pd.ExcelFile(new_file)
    
    sheets = set(old_xls.sheet_names).intersection(set(new_xls.sheet_names))
    
    changes = []
    
    for sheet in sheets:
        if sheet == "Empty":
            continue
            
        df_old = pd.read_excel(old_xls, sheet_name=sheet)
        df_new = pd.read_excel(new_xls, sheet_name=sheet)
        
        if df_old.empty or df_new.empty:
            continue
            
        # 3번째 컬럼이 최신 컨센서스 값(예: 2026/05/22)
        old_val_col = df_old.columns[2]
        new_val_col = df_new.columns[2]
        
        col_name_jongmok = df_old.columns[0]
        col_name_item = df_old.columns[1]
        
        merged = pd.merge(df_old, df_new, on=[col_name_jongmok, col_name_item], suffixes=('_old', '_new'))
        
        for _, row in merged.iterrows():
            item = row[col_name_item]
            if item not in ["매출액", "영업이익"]:
                continue
                
            old_val = row.get(f"{old_val_col}_old", row.get(old_val_col))
            new_val = row.get(f"{new_val_col}_new", row.get(new_val_col))
            
            try:
                old_val_float = float(str(old_val).replace(',', ''))
                new_val_float = float(str(new_val).replace(',', ''))
                
                # 값에 변화가 있는 경우 추출
                if old_val_float != new_val_float:
                    diff_pct = (new_val_float - old_val_float) / abs(old_val_float) * 100 if old_val_float != 0 else 0
                    changes.append({
                        "섹터(시트)": sheet,
                        "종목명": row[col_name_jongmok],
                        "항목": item,
                        "이전값": old_val_float,
                        "최신값": new_val_float,
                        "주간 변화율(%)": diff_pct
                    })
            except Exception as e:
                pass
                
    if not changes:
        print("컨센서스 변화가 있는 종목이 없습니다.")
        return pd.DataFrame()
        
    df_changes = pd.DataFrame(changes)
    df_changes['abs_diff'] = df_changes['주간 변화율(%)'].abs()
    df_changes = df_changes.sort_values(by=['섹터(시트)', '종목명', 'abs_diff'], ascending=[True, True, False]).drop(columns=['abs_diff'])
    
    return df_changes

if __name__ == "__main__":
    # 가장 최근 2개의 _Sector_consensus.xlsx 파일을 자동으로 찾아 비교
    files = sorted(
        str(path)
        for path in CONSENSUS_DATA_DIR.glob("*_Sector_consensus.xlsx")
        if not path.name.startswith("~$")
    )
    if len(files) < 2:
        print("비교할 파일이 2개 이상 필요합니다.")
        sys.exit(1)
        
    old_file = files[-2]
    new_file = files[-1]
    
    df_diff = compare_excel(old_file, new_file)
    if not df_diff.empty:
        old_base = os.path.basename(old_file)
        new_base = os.path.basename(new_file)
        CONSENSUS_DIFF_DIR.mkdir(parents=True, exist_ok=True)
        md_file = CONSENSUS_DIFF_DIR / f"Consensus_Diff_{old_base.split('_')[0]}_to_{new_base.split('_')[0]}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            end_date = new_base.split("_")[0]
            f.write(
                "---\n"
                f"date: 20{end_date[:2]}-{end_date[2:4]}-{end_date[4:6]}\n"
                "type: consensus\n"
                "scope: sector\n"
                "status: active\n"
                "tags:\n"
                "  - \"#Consensus/Diff\"\n"
                "---\n\n"
                f"# 컨센서스 주간 변화 종목 추출 ({old_file} vs {new_file})\n\n"
            )
            
            df_diff_md = df_diff.copy()
            df_diff_md['이전값'] = df_diff_md['이전값'].apply(lambda x: f"{x:,.0f}")
            df_diff_md['최신값'] = df_diff_md['최신값'].apply(lambda x: f"{x:,.0f}")
            df_diff_md['주간 변화율(%)'] = df_diff_md['주간 변화율(%)'].apply(lambda x: f"{x:+.2f}%")
            
            f.write(df_diff_md.to_markdown(index=False))
            print(f"\n결과가 {md_file} 에 저장되었습니다.")
            print(df_diff_md.to_markdown(index=False))
