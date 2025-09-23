
import requests

# 1. API URL
url = "https://httpbin.org/delay/5"

try:
    # 2. 타임아웃 2초 설정
    response = requests.get(url, timeout=2)

    # 3. 상태 코드 확인
    if response.status_code == 200:
        print("응답 성공!")
        print("응답 데이터:", response.json())
    else:
        print(f"요청 실패! 상태 코드: {response.status_code}")

except requests.exceptions.Timeout:
    print("요청이 타임아웃되었습니다.")
except requests.exceptions.RequestException as e:
    print(f"요청 중 오류 발생: {e}")
