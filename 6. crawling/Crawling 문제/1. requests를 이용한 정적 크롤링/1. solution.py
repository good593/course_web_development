import requests

# 1. API URL
url = "https://jsonplaceholder.typicode.com/posts"

# 2. GET 요청 보내기
response = requests.get(url)

# 3. 응답 상태 코드 확인
if response.status_code == 200:
    posts = response.json()  # JSON -> Python list
    # 4. userId가 1인 게시글만 출력
    for post in posts:
        if post['userId'] == 1:
            print(f"[{post['id']}] {post['title']}")
else:
    print(f"요청 실패! 상태 코드: {response.status_code}")
