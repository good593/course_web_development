from fastapi import FastAPI

from routers import conversations, messages, users

# FastAPI 애플리케이션과 Swagger 문서(/docs)에 표시할 정보를 설정합니다.
app = FastAPI(
    title="Supabase 첫 연동 실습",
    description="Supabase Python 클라이언트로 데이터를 저장하고 조회합니다.",
    version="1.0.0",
)

# 기능별로 나뉜 라우터를 앱에 등록합니다.
app.include_router(users.router)
app.include_router(conversations.router)
app.include_router(messages.router)


# @app.get/post는 함수와 HTTP 요청 경로를 연결합니다.
@app.get("/")
def root():
    # 서버 동작 여부와 API 문서 주소를 간단히 확인하는 엔드포인트입니다.
    return {"message": "Supabase 첫 연동 실습", "docs": "/docs"}
