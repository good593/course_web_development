## requests + BeautifulSoup 문제

---
### 문제 1. 웹 페이지 제목 가져오기
- requests와 BeautifulSoup를 사용하여 Python 공식 홈페이지의 페이지 제목(title 태그)을 가져오세요.
- 요청 URL:
  ```shell
  "https://www.python.org/"
  ```

---
### 문제 2. 실시간 뉴스 헤드라인 추출
- 다음 URL에서 실시간 뉴스 헤드라인을 5개 가져오세요.
- 조건:
  - 뉴스 제목만 추출
  - 상위 5개 출력
- 요청 URL:
  ```shell
  "https://news.ycombinator.com/"
  ```

---
### 문제 3. 크롤링 + 예외 처리 + 데이터 저장
- 다음 URL에서 Python 공식 홈페이지의 이벤트 정보(Upcoming Events)를 추출하고, CSV 파일로 저장하세요.
- 추출 항목:
  - 이벤트 제목
  - 날짜
  - 위치
- 결과를 events.csv 파일로 저장
- 요청 URL:
  ```shell
  "https://www.python.org/events/python-events/"
  ```

