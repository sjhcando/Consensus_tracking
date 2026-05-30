import os
import sys
from pypdf import PdfReader

def pdf_to_txt(pdf_path, txt_path):
    print(f"Extracting {pdf_path} -> {txt_path}")
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for i, page in enumerate(reader.pages):
            text += f"\n--- Page {i+1} ---\n"
            page_text = page.extract_text()
            if page_text:
                text += page_text
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("Success")
    except Exception as e:
        print(f"Error: {e}")

def main():
    target_pdfs = [
        # Semiconductor
        ("naver_reports/반도체/260527_SK하이닉스_밸류에이션 대기권 돌파_미래에셋증권.pdf", "naver_reports/반도체/260527_SK하이닉스_미래.txt"),
        ("naver_reports/반도체/260527_삼성전자_밸류에이션 집중 추격 구간_미래에셋증권.pdf", "naver_reports/반도체/260527_삼성전자_미래.txt"),
        ("naver_reports/반도체/260526_반도체_메모리 가격 상승을 견인하는 Nvidia_하나증권.pdf", "naver_reports/반도체/260526_반도체_메모리가격_하나.txt"),
        
        # Defense
        ("naver_reports/방산/260528_기타_K방산_인뎁스_지금 놓치면 후회한다_DS투자증권.pdf", "naver_reports/방산/260528_기타_K방산_인뎁스_DS.txt"),
        
        # Electrical/Electronics
        ("naver_reports/전기전자/260526_삼성전기_글로벌 1등 부품 기업 멀티플_SK증권.pdf", "naver_reports/전기전자/260526_삼성전기_SK.txt"),
        ("naver_reports/전기전자/260526_전기전자_인뎁스_패키지기판과 MLCC, 미래 공급을 예약하는 시.._iM증권.pdf", "naver_reports/전기전자/260526_전기전자_인뎁스_iM.txt"),
        
        # Shipbuilding
        ("naver_reports/조선/260526_삼성중공업_이제부터가 진짜_한화투자증권.pdf", "naver_reports/조선/260526_삼성중공업_한화.txt"),
        ("naver_reports/조선/260526_조선_대기만성_대신증권.pdf", "naver_reports/조선/260526_조선_대기만성_대신.txt"),
        ("naver_reports/조선/260528_조선_MASGA의 조선&데이터센터의 엔진_SK증권.pdf", "naver_reports/조선/260528_조선_MASGA_SK.txt")
    ]
    
    for pdf, txt in target_pdfs:
        if os.path.exists(pdf):
            pdf_to_txt(pdf, txt)
        else:
            print(f"File not found: {pdf}")

if __name__ == "__main__":
    main()
