import json

from services.groq_client import stream_groq
from services.openapi_spec import format_spec_for_prompt
from services.storage import extract_json
from settings import (
    COLLECTION_MAX_TOKENS,
    DIFF_MAX_TOKENS,
    DOCS_MAX_TOKENS,
    README_MAX_TOKENS,
)


def generate_api_docs(spec: dict) -> str:
    """OpenAPI 스펙을 개발자용 마크다운 문서로 바꾸도록 Groq에 요청합니다."""
    # 전체 OpenAPI JSON은 길기 때문에, 프롬프트에 필요한 핵심 정보만 압축합니다.
    spec_text = format_spec_for_prompt(spec)
    prompt = f"""다음 OpenAPI 스펙을 분석해서 개발자용 API 문서를 마크다운으로 작성해줘.

[포함할 내용]
1. API 개요 — 제목, 설명, 버전, 베이스 URL
2. 인증 방법 설명
3. 엔드포인트 요약 표 (메서드 | 경로 | 설명)
4. 각 엔드포인트 상세:
   - 메서드 + 경로 (H3 헤더)
   - 기능 설명
   - 요청 파라미터 표 (이름 | 위치 | 타입 | 필수 | 설명)
   - 요청 예시 (curl 코드 블록)
   - 성공 응답 예시 (JSON 코드 블록)
   - 에러 응답 목록 (코드 | 설명)
5. 공통 에러 코드 표

[OpenAPI 스펙]
{spec_text}
"""
    return stream_groq(prompt, max_tokens=DOCS_MAX_TOKENS, reasoning_effort="medium")


def generate_postman_collection(spec: dict) -> str:
    """OpenAPI 스펙을 Postman Collection JSON으로 바꾸도록 Groq에 요청합니다."""
    spec_text = format_spec_for_prompt(spec)
    prompt = f"""다음 OpenAPI 스펙을 Postman Collection v2.1 JSON으로 변환해줘.

[요구사항]
1. collection.info.name은 API 제목 사용
2. 모든 엔드포인트 포함
3. URL에 {{{{base_url}}}} 변수 사용 (예: {{{{base_url}}}}/products)
4. Content-Type: application/json 헤더 추가
5. POST/PATCH/PUT은 스펙 기반 request body 예시 포함
6. 각 요청에 Tests 스크립트 포함:
   - 상태 코드 검증 (성공: 200 또는 201, 에러: 4xx)
   - 응답 시간 500ms 미만
   - 핵심 필드 존재 여부
7. 태그별 폴더(item) 그룹화
8. 에러 케이스 요청도 각 폴더에 포함 (예: [에러] 존재하지 않는 ID)

JSON만 출력해줘 (설명 없이). ```json ... ``` 블록으로 감싸줘.

[OpenAPI 스펙]
{spec_text}
"""
    raw = stream_groq(prompt, max_tokens=COLLECTION_MAX_TOKENS, reasoning_effort="low")
    # 모델이 ```json 코드블록으로 감싸서 응답해도 실제 JSON 문자열만 저장합니다.
    return extract_json(raw)


def generate_readme(spec: dict) -> str:
    """OpenAPI 스펙을 GitHub README 초안으로 바꾸도록 Groq에 요청합니다."""
    spec_text = format_spec_for_prompt(spec)
    prompt = f"""다음 OpenAPI 스펙을 기반으로 GitHub README.md를 한국어로 작성해줘.

[포함할 섹션]
1. 프로젝트 제목 (H1) + 한 줄 설명
2. 주요 기능 (불릿 목록)
3. 기술 스택 표
4. 빠른 시작
   - 요구 사항
   - 설치 명령어 (코드 블록)
   - 서버 실행 명령어
5. API 엔드포인트 요약 표
6. 환경 변수 목록 표
7. 라이선스

[OpenAPI 스펙]
{spec_text}
"""
    return stream_groq(prompt, max_tokens=README_MAX_TOKENS, reasoning_effort="medium")


def generate_diff_docs(changes: list[dict]) -> str:
    """변경된 엔드포인트 목록만 전달해 변경 문서를 생성합니다."""
    if not changes:
        return ""

    # ensure_ascii=False를 사용하면 한글 설명이 \uXXXX 형태로 바뀌지 않습니다.
    changes_text = json.dumps(changes, ensure_ascii=False, separators=(",", ":"))
    prompt = f"""다음 API 변경사항에 대한 마크다운 문서를 작성해줘.

[포함할 내용]
- 변경 요약 (추가/수정/삭제 건수)
- 각 변경 엔드포인트 상세 (신규/수정/삭제 구분)
- curl 예시 및 응답 예시 (신규/수정 항목만)

[변경사항]
{changes_text}
"""
    return stream_groq(prompt, max_tokens=DIFF_MAX_TOKENS, reasoning_effort="medium")
