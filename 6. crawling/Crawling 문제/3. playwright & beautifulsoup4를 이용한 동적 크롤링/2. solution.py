from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://news.ycombinator.com/")
    html = page.content()
    
    soup = BeautifulSoup(html, "html.parser")
    titles = soup.find_all("span", class_="titleline")
    
    print("=== 상위 5개 뉴스 제목 ===")
    for idx, span in enumerate(titles[:5], start=1):
        news_title = span.a.text.strip()
        print(f"{idx}. {news_title}")
    
    browser.close()
