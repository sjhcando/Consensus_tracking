import os
from pypdf import PdfReader

def main():
    pdf = "naver_reports/반도체/260528_반도체_P E의 시대, 재평가의 본격화_SK증권.pdf"
    txt = "naver_reports/반도체/260528_SK_semi.txt"
    try:
        reader = PdfReader(pdf)
        text = ""
        for i, page in enumerate(reader.pages):
            text += f"\n--- Page {i+1} ---\n"
            page_text = page.extract_text()
            if page_text:
                text += page_text
        with open(txt, 'w', encoding='utf-8') as f:
            f.write(text)
        print("Success converting SK semi report")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
