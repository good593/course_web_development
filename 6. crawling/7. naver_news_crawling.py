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


def get_article_links(SECTION_URL, page, MAX_ARTICLES):
    """
    네이버 뉴스 섹션 페이지에서
    네이버 뉴스 기사 링크 수집
    """

    page.goto(
        SECTION_URL,
        wait_until="domcontentloaded",
        timeout=30000
    )

    # 동적 콘텐츠 로딩 대기
    page.wait_for_timeout(2000)

    links = page.locator('a[href*="/article/"]').evaluate_all(
        """
        elements => elements.map(element => element.href)
        """
    )

    # 중복 제거
    result = []

    for link in links:
        if link not in result:
            result.append(link)

    return result[:MAX_ARTICLES]


def get_article(page, url):
    """기사 상세 정보 수집"""

    try:
        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        # 기사 본문 등장할 때까지 대기
        page.wait_for_selector(
            "#dic_area",
            timeout=10000
        )

        # -------------------------
        # 제목
        # -------------------------
        title_locator = page.locator("#title_area")

        title = ""

        if title_locator.count() > 0:
            title = clean_text(
                title_locator.first.inner_text()
            )

        # -------------------------
        # 본문
        # -------------------------
        content_locator = page.locator("#dic_area")

        content = ""

        if content_locator.count() > 0:
            content = clean_text(
                content_locator.first.inner_text()
            )

        # -------------------------
        # 언론사
        # -------------------------
        company = ""

        # 가장 일반적인 언론사 로고
        press_logo = page.locator(
            ".media_end_head_top_logo img"
        )

        if press_logo.count() > 0:

            company = (
                press_logo.first.get_attribute("alt")
                or press_logo.first.get_attribute("title")
                or ""
            )

        # alt/title이 없는 경우 보조 selector
        if not company:

            press = page.locator(
                ".media_end_linked_more_point"
            )

            if press.count() > 0:
                company = clean_text(
                    press.first.inner_text()
                )

        return {
            "company": company,
            "title": title,
            "content": content,
            "url": url
        }

    except Exception as e:

        print(f"[ERROR] {url}")
        print(e)

        return None


def save_csv(data):

    with open(
        "naver_news.csv",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "company",
                "title",
                "content",
                "url"
            ]
        )

        writer.writeheader()
        writer.writerows(data)


def main(SECTION_URL, MAX_ARTICLES):

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

        # 1. 기사 URL 수집
        article_links = get_article_links(SECTION_URL, page, MAX_ARTICLES)

        print(f"수집된 기사 URL: {len(article_links)}개")

        results = []

        # 2. 기사 상세 페이지 순회
        for index, url in enumerate(article_links, start=1):

            print(
                f"[{index}/{len(article_links)}] "
                f"{url}"
            )

            article = get_article(page, url)

            if article:
                results.append(article)

                print(
                    f"언론사 : {article['company']}"
                )
                print(
                    f"제목   : {article['title']}"
                )
                print(
                    f"본문   : {article['content'][:100]}..."
                )
                print("-" * 80)

            # 너무 빠르게 요청하지 않도록 간격
            time.sleep(1)

        # 3. CSV 저장
        save_csv(results)

        print()
        print(f"최종 수집 건수: {len(results)}")
        print("naver_news.csv 저장 완료")

        browser.close()


if __name__ == "__main__":
    SECTION_URL = "https://news.naver.com/section/105"
    MAX_ARTICLES = 20
    main(SECTION_URL, MAX_ARTICLES)