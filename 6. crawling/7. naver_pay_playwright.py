# 비동기 프로그래밍을 위한 asyncio 모듈 임포트
import asyncio
import platform
# Playwright의 비동기 API 임포트
from playwright.async_api import async_playwright
# BeautifulSoup 임포트 (selenium 코드와 동일한 방식 사용)
from bs4 import BeautifulSoup

# Playwright를 사용하여 네이버 페이 데이터를 수집하는 함수
async def naver_pay_crawler(playwright):
    # 크롬 브라우저를 헤드리스 모드로 실행 (GUI 없이 백그라운드에서 실행)
    browser = await playwright.chromium.launch(headless=False)  # 로그인을 위해 headless=False로 설정
    # 새로운 컨텍스트 생성(독립적인 세션 운영을 위함)
    context = await browser.new_context() 
    # 새로운 페이지(탭) 생성
    page = await context.new_page()
    
    try:
        # 1. 네이버 메인 페이지로 이동
        print("네이버 메인 페이지로 이동중...")
        await page.goto('http://www.naver.com')
        await page.wait_for_load_state('networkidle')
        
        # 2. 로그인 버튼 클릭
        print("로그인 버튼 찾는 중...")
        # 로그인 버튼 클릭 (클래스명이 변경될 수 있으므로 텍스트로도 찾기)
        try:
            login_btn = await page.wait_for_selector('a.MyView-module__link_login___HpHMW', timeout=5000)
            await login_btn.click()
        except:
            # 클래스명으로 찾지 못할 경우 텍스트로 찾기
            await page.click('text=로그인')
        
        await page.wait_for_load_state('networkidle')
        print("로그인 페이지로 이동 완료")
        
        # 3. 로그인 정보 입력 (실제 사용시 본인 계정 정보 입력 필요)
        # 보안상 실제 계정 정보는 주석 처리
        user_id = ""  # 실제 네이버 아이디로 변경 필요
        user_pw = ""  # 실제 네이버 비밀번호로 변경 필요
        
        print("아이디 입력 중...")
        # 아이디 입력 필드 찾기 및 입력
        id_input = await page.wait_for_selector('#id')
        await id_input.click()
        await id_input.fill(user_id)
        
        print("비밀번호 입력 중...")
        # 비밀번호 입력 필드 찾기 및 입력
        pw_input = await page.wait_for_selector('#pw')
        await pw_input.click()
        await pw_input.fill(user_pw)
        
        # 4. 로그인 버튼 클릭
        print("로그인 시도 중...")
        login_submit_btn = await page.wait_for_selector('#log\\.login')
        await login_submit_btn.click()
        
        # 로그인 완료 대기 (네이버 메인 페이지로 리다이렉트)
        await page.wait_for_load_state('networkidle')
        
        # 수동 로그인을 위한 대기 시간 (실제 사용시에는 이 부분을 주석처리하고 위의 자동 로그인 코드 사용)
        print("수동으로 로그인을 완료한 후 엔터를 눌러주세요...")
        input("로그인 완료 후 엔터를 눌러주세요: ")
        
        # 5. 네이버 페이 페이지로 이동
        print("네이버 페이 페이지로 이동 중...")
        await page.goto('https://order.pay.naver.com/home')
        await page.wait_for_load_state('networkidle')
        
        # 6. 상품명 데이터 수집 (selenium 코드와 동일한 방식 사용)
        print("상품 정보 수집 중...")
        
        # selenium 코드와 동일하게 page_source를 가져와서 BeautifulSoup으로 파싱
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # selenium 코드와 동일한 방식으로 상품명 찾기
        notices = soup.find_all("span", class_="ProductName_article__zaafE")
        
        products = []
        if notices:
            print(f"ProductName_article__zaafE 클래스로 {len(notices)}개 상품 발견!")
            for n in notices:
                product_name = n.get_text().strip()
                if product_name:
                    products.append(product_name)
        
        # 7. 결과 출력
        if products:
            print("\n=== 네이버 페이 상품 목록 ===")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product}")
        else:
            print("상품 정보를 찾을 수 없습니다.")
            # 페이지 내용 확인을 위해 HTML 출력 (디버깅용)
            html_content = await page.content()
            print("페이지 HTML 일부:")
            print(html_content[:1000] + "...")
            
            # 페이지 스크린샷 저장 (디버깅용)
            await page.screenshot(path='naver_pay_debug.png')
            print("디버깅용 스크린샷을 'naver_pay_debug.png'로 저장했습니다.")
    
    except Exception as e:
        print(f"오류 발생: {e}")
        # 오류 발생시 스크린샷 저장
        await page.screenshot(path='error_screenshot.png')
        print("오류 스크린샷을 'error_screenshot.png'로 저장했습니다.")
    
    finally:
        # 브라우저 종료 (리소스 해제)
        await browser.close()
        print("브라우저가 종료되었습니다.")

# 메인 실행 함수
async def main():
    print("네이버 페이 크롤러를 시작합니다...")
    # Playwright 컨텍스트 매니저를 사용하여 안전하게 실행
    async with async_playwright() as playwright:
        await naver_pay_crawler(playwright)

# 프로그램 진입점
if __name__ == "__main__":
    # 비동기 메인 함수 실행
    asyncio.run(main())