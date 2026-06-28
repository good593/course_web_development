"""README 실습에서 공통으로 사용하는 Ollama 모델과 프롬프트 설정입니다."""

# README의 모델 다운로드 실습과 맞춰 둔 기본 코드 생성 모델입니다.
CODE_MODEL = "gemma4:e4b"

# thinking 모드는 system prompt 앞에 이 토큰을 붙여서 켭니다.
THINKING_TOKEN = "<|think|>"

# Ollama gemma4 페이지의 권장 샘플링 설정입니다.
# temperature/top_p/top_k는 생성 결과의 다양성을 조절하고, num_predict는 호출 지점에서 따로 덮어씁니다.
DEFAULT_OPTIONS = {
    "temperature": 1.0,
    "top_p": 0.95,
    "top_k": 64,
}

# 모델에게 "FastAPI 코드 생성기" 역할과 출력 규칙을 알려 주는 system prompt입니다.
# README의 좋은 프롬프트 예시처럼 Pydantic v2, HTTPException, 한국어 주석을 명시합니다.
SYSTEM_PROMPT = """당신은 FastAPI 전문가입니다.
사용자의 API 요구사항을 받아 완성된 FastAPI 코드를 생성합니다.

다음 규칙을 반드시 따르세요:
1. Python 타입 힌트를 사용하세요
2. Pydantic v2 BaseModel로 입출력 스키마를 분리하세요 (Create / Update / Response)
3. HTTPException으로 404, 400, 409 등 적절한 에러를 반환하세요
4. 인메모리 dict를 DB로 사용하세요 (SQLAlchemy 사용 금지)
5. 한국어 주석을 포함하세요
6. 코드는 반드시 ```python ... ``` 블록으로 감싸세요
7. 실행 가능한 완성된 코드를 생성하세요
"""
