from fastapi import FastAPI

from routers import auth, me

app = FastAPI(
    title="JWT 인증과 Supabase Auth",
    description="회원가입, 로그인, Bearer 토큰 검증을 실습합니다.",
    version="1.0.0",
)

# 기능별로 나뉜 라우터를 앱에 등록합니다.
app.include_router(auth.router)
app.include_router(me.router)


@app.get("/")
def root():
    """서버 동작 여부와 Swagger UI 경로를 간단히 안내합니다."""

    return {"message": "JWT 인증과 Supabase Auth", "docs": "/docs"}
