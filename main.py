import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 이메일 정규식
EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

def extract_emails(url):
    """requests + BeautifulSoup + regex 로 이메일 주소 추출"""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] {url} → 요청 실패: {e}")
        return set()

    soup = BeautifulSoup(resp.text, "html.parser")
    emails = set()

    # 1) mailto 링크
    for a in soup.find_all("a", href=True):
        if a["href"].startswith("mailto:"):
            emails.add(a["href"].split(":",1)[1].strip())

    # 2) 본문 텍스트에서 정규식 매칭
    text = soup.get_text()
    for m in EMAIL_REGEX.findall(text):
        emails.add(m)

    return emails

def main():
    infile  = "브랜드_홈페이지_결과_naver_최상단.txt"
    outfile = "브랜드_이메일_결과.xlsx"

    data = []
    with open(infile, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 2:
                continue
            brand, url = parts[0], parts[1]
            print(f"▶ {brand} → {url}")
            emails = extract_emails(url)
            email_str = ", ".join(sorted(emails)) if emails else ""
            print(f"   found: {email_str}\n")
            data.append({"브랜드명": brand, "홈페이지": url, "이메일": email_str})

    # 결과를 엑셀로 저장
    df = pd.DataFrame(data)
    df.to_excel(outfile, index=False)
    print(f"\n✅ 완료! '{outfile}'에 저장되었습니다.")

if __name__ == "__main__":
    main()
