
import requests
from bs4 import BeautifulSoup

# 1. URL 정의
url = "https://www.python.org/"

# 2. HTML 요청
response = requests.get(url)

# 3. 상태 코드 확인
if response.status_code == 200:
    # 4. BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 5. 제목 추출
    title = soup.title.text
    print(f"페이지 제목: {title}")
else:
    print(f"요청 실패! 상태 코드: {response.status_code}")
