"""Swagger UI와 OpenAPI 문서에 표시할 기본 정보를 정의합니다."""

import os

API_VERSION = "1.0.0"

# 긴 설명은 Swagger UI 상단과 /openapi.json의 info.description에 들어갑니다.
API_DESCRIPTION = """
## 개요

이 API는 FastAPI가 만든 OpenAPI 스펙을 생성형 AI에 전달해
API 문서, Postman Collection, README 초안을 자동 생성하는 실습용 서버입니다.

쇼핑몰 상품·주문·회원 엔드포인트는 문서화 대상이 되는 예제 API이고,
`/ai-docs` 엔드포인트는 Groq API를 호출해 문서를 생성하는 기능입니다.

## 인증

보호된 엔드포인트는 `Authorization: Bearer <token>` 헤더가 필요합니다.
실습용 관리자 토큰은 `demo-admin-token`입니다.

## 환경 변수

생성형 AI 문서 생성 기능을 사용하려면 `.env` 파일에 `GROQ_API_KEY`를 설정해야 합니다.

## 에러 응답 형식

```json
{
    "detail": "사람이 읽을 수 있는 오류 설명"
}
```

"""

# 태그는 Swagger UI에서 엔드포인트를 주제별로 묶는 기준입니다.
TAGS_METADATA = [
    {"name": "AI Documents", "description": "OpenAPI 스펙 기반 생성형 AI 문서 자동화"},
    {"name": "Products", "description": "상품 조회, 등록, 수정, 삭제"},
    {"name": "Orders", "description": "주문 생성 및 상태 관리"},
    {"name": "Users", "description": "회원 가입 및 정보 관리"},
    {"name": "Health", "description": "서버 상태 확인"},
]


def is_production() -> bool:
    """ENV=production이면 문서 화면을 숨기기 위해 True를 반환합니다."""
    return os.getenv("ENV", "development") == "production"
