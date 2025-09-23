import requests
from bs4 import BeautifulSoup

# 1. URL 정의
url = "https://news.ycombinator.com/"

# 2. HTML 요청
response = requests.get(url)

# 3. BeautifulSoup 파싱
if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 4. 뉴스 제목 찾기 (Hacker News 구조 분석)
    titles = soup.find_all("span", class_="titleline")
    
    # 5. 상위 5개 뉴스만 출력
    print("=== 실시간 뉴스 헤드라인 ===")
    for idx, title_tag in enumerate(titles[:5], start=1):
        news_title = title_tag.a.text  # <a> 태그 안의 텍스트 추출
        print(f"{idx}. {news_title}")
else:
    print(f"요청 실패! 상태 코드: {response.status_code}")
