from google import genai

from core.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)
