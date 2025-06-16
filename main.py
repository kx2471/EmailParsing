from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def load_brands_from_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def search_official_site_naver(brand, driver):
    try:
        query = f"{brand} 공식 홈페이지"
        driver.get(f"https://search.naver.com/search.naver?query={query}")
        time.sleep(1.5)

        # 1. '사이트' 영역
        try:
            link = driver.find_element(By.CSS_SELECTOR, "div.place_section_content a.url").get_attribute("href")
            return link
        except:
            pass

        # 2. '사이트' 묶음 (보통은 공식사이트 묶음)
        try:
            link = driver.find_element(By.CSS_SELECTOR, "ul.list_site li a").get_attribute("href")
            return link
        except:
            pass

        # 3. 웹문서 상단 링크 (가장 일반적인 경우)
        try:
            link = driver.find_element(By.CSS_SELECTOR, "a.api_txt_lines.total_tit").get_attribute("href")
            return link
        except:
            pass

        # 4. 지식패널이나 뉴스 등은 무시하고, 검색결과 중 a 태그 중 유의미한 첫 링크
        try:
            all_links = driver.find_elements(By.CSS_SELECTOR, "a")
            for a in all_links:
                href = a.get_attribute("href")
                if href and href.startswith("http") and "naver.com" not in href:
                    return href
        except:
            pass

        return "❌ 실패: 링크를 찾지 못함"
    except Exception as e:
        return f"❌ 예외 발생: {str(e)}"

def main():
    brands = load_brands_from_file("브랜드리스트.txt")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    results = []

    for idx, brand in enumerate(brands, 1):
        print(f"{idx}/{len(brands)} ▶ {brand} (네이버)...")
        link = search_official_site_naver(brand, driver)
        print(f"🔗 결과: {link}")
        results.append((brand, link))

    driver.quit()

    with open("브랜드_홈페이지_결과_naver_최상단.txt", "w", encoding="utf-8") as f:
        for brand, link in results:
            f.write(f"{brand}\t{link}\n")

    print("\n✅ 네이버 최상단 링크 수집 완료!")

if __name__ == "__main__":
    main()
