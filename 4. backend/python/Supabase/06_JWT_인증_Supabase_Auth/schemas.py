from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    # EmailStr은 이메일 형식을, Field는 문자열 길이를 엔드포인트 실행 전에 검증합니다.
    # 검증에 실패하면 FastAPI가 자동으로 422 응답을 반환합니다.
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    # 현재 예제에서는 입력값만 검증하며 profiles 테이블에는 아직 저장하지 않습니다.
    display_name: str = Field(..., min_length=1, max_length=50)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class AuthTokenResponse(BaseModel):
    """회원가입과 로그인이 공통으로 사용하는 인증 응답 형식입니다."""

    user_id: str
    email: str
    # 이메일 확인이 필요한 회원가입에서는 세션이 없어 두 토큰이 None일 수 있습니다.
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    email_confirm_required: bool = False


class CurrentUser(BaseModel):
    """검증된 JWT에서 얻은 현재 사용자의 최소 정보입니다."""

    id: str
    email: str
