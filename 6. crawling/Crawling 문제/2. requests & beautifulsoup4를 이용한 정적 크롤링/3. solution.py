import requests
from bs4 import BeautifulSoup
import csv

# 1. URL
url = "https://www.python.org/events/python-events/"

try:
    # 2. HTML 요청
    response = requests.get(url, timeout=5)
    response.raise_for_status()  # 상태 코드가 200이 아니면 예외 발생

    # 3. BeautifulSoup 파싱
    soup = BeautifulSoup(response.text, "html.parser")

    # 4. 이벤트 리스트 찾기
    events = soup.select("ul.list-recent-events.menu li")

    # 5. 결과 데이터 저장용 리스트
    event_data = []

    for event in events:
        title = event.find("h3").text.strip()  # 이벤트 제목
        date = event.find("time").text.strip() # 이벤트 날짜
        location = event.find("span", class_="event-location").text.strip() # 이벤트 위치
        
        event_data.append([title, date, location])

    # 6. CSV 파일 저장
    with open("events.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["제목", "날짜", "위치"])  # 헤더
        writer.writerows(event_data)
    
    print("CSV 파일 저장 완료! (events.csv)")

except requests.exceptions.Timeout:
    print("요청이 타임아웃되었습니다.")
except requests.exceptions.RequestException as e:
    print(f"요청 중 오류 발생: {e}")
