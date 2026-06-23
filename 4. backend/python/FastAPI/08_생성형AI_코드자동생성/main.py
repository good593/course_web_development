"""
생성형 AI를 활용한 FastAPI 코드 자동 생성기

실행 전 Ollama를 설치하고 gemma4 모델을 내려받으세요.

    ollama pull gemma4:e4b
"""
from fastapi import FastAPI

from routers.generate import router as generate_router

app = FastAPI(
    title="FastAPI 코드 자동 생성기",
    description="Ollama gemma4로 FastAPI/Pydantic 코드 초안을 생성합니다.",
    version="0.1.0",
)

app.include_router(generate_router)


if __name__ == "__main__":
    from cli import main

    main()
