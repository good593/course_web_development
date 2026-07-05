import os

from dotenv import load_dotenv

load_dotenv()

PAGE_TITLE = "Chatbot with FastAPI"
DEFAULT_API_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8001")
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 800
REQUEST_TIMEOUT = (5, 120)
