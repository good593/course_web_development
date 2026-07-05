"""
Streamlit 화면에서 사용하는 기본 설정입니다.
"""

import os

from dotenv import load_dotenv

# 프론트도 같은 `.env`를 읽어서 FastAPI 주소 기본값을 가져옵니다.
load_dotenv()

PAGE_TITLE = "Chatbot with FastAPI"
DEFAULT_API_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8001")

# 슬라이더의 초기값입니다. 실제 요청 때 사용자가 화면에서 바꿀 수 있습니다.
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 800

# requests timeout은 (연결 대기 시간, 응답 대기 시간) 순서입니다.
REQUEST_TIMEOUT = (5, 120)
