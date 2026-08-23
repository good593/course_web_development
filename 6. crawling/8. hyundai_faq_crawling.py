from playwright.sync_api import sync_playwright
import csv
import re
import time


def clean_text(text: str) -> str:
    """불필요한 공백 정리"""
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_total_pages(page):
    """페이지네이션에서 전체 페이지 수 확인"""

    end_button = page.locator(".ui_paging button.navi.end")

    if end_button.count() > 0:
        last_page = end_button.first.get_attribute("data-page")
        return int(last_page)

    return 1


def go_to_next_page(page):
    """다음 페이지 버튼 클릭"""

    next_button = page.locator(".ui_paging button.navi.next")

    next_button.first.click()

    # 목록 갱신 대기
    page.wait_for_timeout(1500)


def get_faq_items(page):
    """현재 페이지에 로드된 FAQ 목록 수집"""

    items = []

    faq_list = page.locator(".result_area .ui_accordion dl")
    count = faq_list.count()

    for i in range(count):
        dl = faq_list.nth(i)

        # -------------------------
        # 카테고리
        # -------------------------
        category_locator = dl.locator("dt .title i")

        category = ""

        if category_locator.count() > 0:
            category = clean_text(
                category_locator.first.inner_text()
            ).strip("[] ")

        # -------------------------
        # 질문
        # -------------------------
        question_locator = dl.locator("dt .title .brief")

        question = ""

        if question_locator.count() > 0:
            question = clean_text(
                question_locator.first.inner_text()
            )

        # -------------------------
        # 답변
        # -------------------------
        answer_locator = dl.locator("dd .exp")

        answer = ""

        if answer_locator.count() > 0:
            answer = clean_text(
                answer_locator.first.inner_text()
            )

        items.append({
            "category": category,
            "question": question,
            "answer": answer
        })

    return items


def get_all_faqs(FAQ_URL, page, MAX_PAGES):
    """
    현대자동차 FAQ 페이지에서
    전체 페이지를 순회하며 FAQ 목록 수집
    """

    page.goto(
        FAQ_URL,
        wait_until="networkidle",
        timeout=30000
    )

    # 동적 콘텐츠 로딩 대기
    page.wait_for_timeout(2000)

    total_pages = get_total_pages(page)
    target_pages = min(total_pages, MAX_PAGES)

    print(f"전체 페이지: {total_pages}개 / 수집 대상: {target_pages}개")

    results = []

    for page_no in range(1, target_pages + 1):

        items = get_faq_items(page)

        print(f"[{page_no}/{target_pages}] {len(items)}개 수집")

        results.extend(items)

        if page_no < target_pages:
            go_to_next_page(page)

        # 너무 빠르게 요청하지 않도록 간격
        time.sleep(1)

    return results


def save_csv(data):

    with open(
        "hyundai_faq.csv",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "category",
                "question",
                "answer"
            ]
        )

        writer.writeheader()
        writer.writerows(data)


def main(FAQ_URL, MAX_PAGES):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        # 1. FAQ 목록 수집
        results = get_all_faqs(FAQ_URL, page, MAX_PAGES)

        # 2. CSV 저장
        save_csv(results)

        print()
        print(f"최종 수집 건수: {len(results)}")
        print("hyundai_faq.csv 저장 완료")

        browser.close()


if __name__ == "__main__":
    FAQ_URL = "https://www.hyundai.com/kr/ko/faq.html"
    MAX_PAGES = 6
    main(FAQ_URL, MAX_PAGES)
