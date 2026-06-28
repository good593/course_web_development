"""
생성형 AI를 활용한 FastAPI 코드 자동 생성기

실행 전 Ollama를 설치하고 gemma4 모델을 내려받으세요.

    ollama pull gemma4:e4b
"""
from fastapi import FastAPI

from routers.generate import router as generate_router

# README의 "서버 실행 및 Swagger 실습"에서 사용하는 FastAPI 앱 객체입니다.
# uvicorn은 이 파일의 app 변수를 찾아서 웹 서버를 시작합니다.
app = FastAPI(
    title="FastAPI 코드 자동 생성기",
    description="Ollama gemma4로 FastAPI/Pydantic 코드 초안을 생성합니다.",
    version="0.1.0",
)

# 라우터에는 Swagger에서 확인하는 GET /, POST /generate 엔드포인트가 들어 있습니다.
app.include_router(generate_router)
