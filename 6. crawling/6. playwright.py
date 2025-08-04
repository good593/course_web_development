# 비동기 프로그래밍을 위한 asyncio 모듈 임포트
import asyncio
# Playwright의 비동기 API 임포트
from playwright.async_api import async_playwright

# Playwright를 사용하여 웹페이지에서 데이터를 수집하는 함수
async def run(playwright):
    # 크롬 브라우저를 헤드리스 모드로 실행 (GUI 없이 백그라운드에서 실행)
    browser = await playwright.chromium.launch(headless=True)
    # 새로운 컨텍스트 생성(독립적인 세션 운영을 위함)
    context = await browser.new_context() 
    # 새로운 페이지(탭) 생성
    page = await context.new_page()
    # 지정된 URL로 이동
    await page.goto('https://example.com')
    # 페이지의 제목 가져오기
    title = await page.title()
    # 제목 출력
    print(title)
    # 브라우저 종료 (리소스 해제)
    await browser.close()

# 메인 실행 함수
async def main():
    # Playwright 컨텍스트 매니저를 사용하여 안전하게 실행
    async with async_playwright() as playwright:
        await run(playwright)

# 비동기 메인 함수 실행
asyncio.run(main())