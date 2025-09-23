
import requests

# 1. API URL
url = "https://jsonplaceholder.typicode.com/posts"

# 2. 보낼 데이터
payload = {
    "title": "Test Post",
    "body": "This is a test post using Python requests.",
    "userId": 101
}

# 3. POST 요청
response = requests.post(url, json=payload)

# 4. 응답 처리
if response.status_code == 201:
    print("데이터 전송 성공!")
    print("서버 응답 JSON:", response.json())
else:
    print(f"데이터 전송 실패! 상태 코드: {response.status_code}")

