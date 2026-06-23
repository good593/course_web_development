from fastapi import FastAPI

from routers import conversations, messages, users

# FastAPI 애플리케이션을 생성합니다. 아래 정보는 /docs와 OpenAPI 문서에도 표시됩니다.
app = FastAPI(
    title="Pydantic + Repository 패턴",
    description="Field 검증과 Repository 패턴으로 코드를 구조화합니다.",
    version="1.0.0",
)

# 기능별로 나뉜 라우터를 앱에 등록합니다.
app.include_router(users.router)
app.include_router(conversations.router)
app.include_router(messages.router)


# GET / 요청을 애플리케이션의 기본 안내 응답과 연결합니다.
@app.get("/")
def root():
    # 대화형 API 문서는 /docs에서 확인할 수 있습니다.
    return {"message": "Pydantic + Repository 패턴", "docs": "/docs"}
