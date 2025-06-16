import time
import re
import requests
import pandas as pd
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=false")
    return webdriver.Chrome(service=Service(), options=options)

def search_naver(driver, brand):
    try:
        q = quote_plus(f"{brand} 공식홈페이지")
        driver.get(f"https://search.naver.com/search.naver?query={q}")
        elem = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.link_tit"))
        )
        return elem.get_attribute("href")
    except:
        return ""

def search_bing(driver, brand):
    try:
        q = quote_plus(f"{brand} 공식홈페이지")
        driver.get(f"https://www.bing.com/search?q={q}")
        elem = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.b_algo h2 a"))
        )
        return elem.get_attribute("href")
    except:
        return ""

def normalize_url(u):
    parsed = requests.utils.urlparse(u)
    domain = parsed.netloc.lower().lstrip("www.")
    path = parsed.path.rstrip("/")
    return domain + path

def is_same_url(u1, u2):
    if not u1 or not u2: 
        return False
    return normalize_url(u1) == normalize_url(u2)

def extract_emails(url):
    """requests + BeautifulSoup + regex 로 이메일 추출"""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except:
        return set()
    soup = BeautifulSoup(resp.text, "html.parser")
    emails = set()

    # mailto 링크
    for a in soup.find_all("a", href=True):
        if a["href"].startswith("mailto:"):
            emails.add(a["href"].split(":",1)[1].strip())

    # 본문에서 패턴 매칭
    text = soup.get_text()
    for m in EMAIL_REGEX.findall(text):
        emails.add(m)
    return emails

def append_to_excel(filename, row):
    file_path = Path(filename)
    cols = ["브랜드명", "Naver", "Bing", "최종선택", "이메일"]
    df_new = pd.DataFrame([row], columns=cols)
    if file_path.exists():
        df = pd.read_excel(file_path)
        df = pd.concat([df, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_excel(file_path, index=False)

def main():
    driver = create_driver()
    filename = "result.xlsx"

    with open("브랜드리스트.txt", encoding="utf-8") as f:
        brands = [l.strip() for l in f if l.strip()]

    for i, brand in enumerate(brands, 1):
        print(f"[{i}/{len(brands)}] {brand} 검색 중…")
        naver = search_naver(driver, brand)
        bing  = search_bing(driver, brand)

        final = naver if is_same_url(naver, bing) else ""
        print(" ▶ Naver:", naver)
        print(" ▶ Bing :", bing)
        print(" ▶ 최종선택:", final or "없음")

        emails = ""
        if final:
            ems = extract_emails(final)
            emails = ", ".join(sorted(ems))
        print(" ▶ 이메일:", emails or "없음\n")

        append_to_excel(filename, [brand, naver, bing, final, emails])
        time.sleep(0.5)

    driver.quit()
    print("✅ 완료! ‘result.xlsx’에 저장되었습니다.")

if __name__ == "__main__":
    main()
