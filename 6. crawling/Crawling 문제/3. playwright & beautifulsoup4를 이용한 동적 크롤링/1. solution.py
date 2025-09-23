from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # 브라우저 실행
    page = browser.new_page()
    page.goto("https://www.python.org/")       # 페이지 이동
    html = page.content()                       # 렌더링된 HTML 가져오기
    
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.text.strip()
    print(f"페이지 제목: {title}")
    
    browser.close()
