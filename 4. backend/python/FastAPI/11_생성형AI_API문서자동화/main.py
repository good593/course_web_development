"""
생성형 AI를 활용한 API 문서 자동화

실행 전 .env 파일에 ANTHROPIC_API_KEY를 설정하고,
09_Swagger_API문서화 서버를 먼저 실행하세요.

사용법:
  python main.py pipeline    # 전체 파이프라인 (문서 + Collection + README)
  python main.py docs        # 마크다운 API 문서만
  python main.py collection  # Postman Collection만
  python main.py readme      # README만
  python main.py diff        # 이전 스펙과 비교해 변경분만 업데이트
"""
import re
import sys
import json
from pathlib import Path

import httpx
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()
OUTPUT_DIR = Path("output")
DEFAULT_OPENAPI_URL = "http://localhost:8000/openapi.json"


# ── 유틸 ──────────────────────────────────────────────────────────────────────

def _stream(prompt: str, max_tokens: int = 8192, use_thinking: bool = True) -> str:
    kwargs = {}
    if use_thinking:
        kwargs["thinking"] = {"type": "adaptive"}

    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
        **kwargs,
    ) as stream:
        parts = []
        for text in stream.text_stream:
            print(text, end="", flush=True)
            parts.append(text)
    print()
    return "".join(parts)


def _save(content: str, filename: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / filename
    path.write_text(content, encoding="utf-8")
    print(f"저장 완료: {path}")
    return path


def _extract_json(text: str) -> str:
    """마크다운 코드 블록에서 JSON 추출."""
    match = re.search(r"```(?:json)?\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def build_openapi_url(base_or_spec_url: str) -> str:
    """서버 기본 URL 또는 openapi.json 전체 URL을 모두 허용합니다."""
    url = base_or_spec_url.rstrip("/")
    if url.endswith("/openapi.json"):
        return url
    return f"{url}/openapi.json"


# ── 스펙 수집 ─────────────────────────────────────────────────────────────────

def fetch_openapi_spec(url: str = DEFAULT_OPENAPI_URL) -> dict:
    spec_url = build_openapi_url(url)
    try:
        response = httpx.get(spec_url, timeout=5)
        response.raise_for_status()
        spec = response.json()
        path_count = sum(len(v) for v in spec.get("paths", {}).values())
        print(f"스펙 수집 완료 - 엔드포인트 {path_count}개")
        return spec
    except httpx.ConnectError:
        print(f"서버에 연결할 수 없습니다: {spec_url}")
        print("09_Swagger_API문서화 폴더에서 서버를 먼저 실행하세요.")
        print("  uvicorn main:app --reload")
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"OpenAPI 스펙 요청 중 오류가 발생했습니다: {e}")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        print(f"OpenAPI 스펙 요청 실패: {e.response.status_code} {spec_url}")
        sys.exit(1)
    except ValueError:
        print(f"OpenAPI 스펙이 JSON 형식이 아닙니다: {spec_url}")
        sys.exit(1)


def save_spec_snapshot(spec: dict):
    """변경 감지를 위해 현재 스펙을 저장합니다."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "_spec_snapshot.json").write_text(
        json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_spec_snapshot() -> dict | None:
    path = OUTPUT_DIR / "_spec_snapshot.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


# ── 문서 생성 함수 ────────────────────────────────────────────────────────────

def generate_api_docs(spec: dict) -> str:
    spec_text = json.dumps(spec, ensure_ascii=False, indent=2)
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
    print("\n[마크다운 API 문서 생성 중...]\n")
    return _stream(prompt, max_tokens=8192)


def generate_postman_collection(spec: dict) -> str:
    spec_text = json.dumps(spec, ensure_ascii=False, indent=2)
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
    print("\n[Postman Collection 생성 중...]\n")
    raw = _stream(prompt, max_tokens=16000, use_thinking=False)
    return _extract_json(raw)


def generate_readme(spec: dict) -> str:
    spec_text = json.dumps(spec, ensure_ascii=False, indent=2)
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
    print("\n[README 생성 중...]\n")
    return _stream(prompt, max_tokens=4096)


# ── 증분 업데이트 ─────────────────────────────────────────────────────────────

def get_changed_endpoints(old_spec: dict, new_spec: dict) -> list[dict]:
    changes = []
    old_paths = old_spec.get("paths", {})
    new_paths = new_spec.get("paths", {})

    for path, methods in new_paths.items():
        for method, details in methods.items():
            old_details = old_paths.get(path, {}).get(method)
            if old_details != details:
                changes.append({
                    "path": path,
                    "method": method.upper(),
                    "is_new": old_details is None,
                    "details": details,
                })

    # 삭제된 엔드포인트
    for path, methods in old_paths.items():
        for method in methods:
            if method not in new_paths.get(path, {}):
                changes.append({"path": path, "method": method.upper(), "is_deleted": True})

    return changes


def generate_diff_docs(changes: list[dict]) -> str:
    if not changes:
        print("변경된 엔드포인트가 없습니다.")
        return ""

    changes_text = json.dumps(changes, ensure_ascii=False, indent=2)
    prompt = f"""다음 API 변경사항에 대한 마크다운 문서를 작성해줘.

[포함할 내용]
- 변경 요약 (추가/수정/삭제 건수)
- 각 변경 엔드포인트 상세 (신규/수정/삭제 구분)
- curl 예시 및 응답 예시 (신규/수정 항목만)

[변경사항]
{changes_text}
"""
    print(f"\n[변경된 엔드포인트 {len(changes)}개 문서화 중...]\n")
    return _stream(prompt, max_tokens=4096)


# ── 파이프라인 ────────────────────────────────────────────────────────────────

def run_pipeline(server_url: str = "http://localhost:8000"):
    print("=" * 60)
    print("API 문서 자동화 파이프라인")
    print("=" * 60)

    spec = fetch_openapi_spec(server_url)

    docs = generate_api_docs(spec)
    _save(docs, "API_DOCS.md")

    collection_json = generate_postman_collection(spec)
    try:
        parsed = json.loads(collection_json)
        _save(json.dumps(parsed, ensure_ascii=False, indent=2), "collection.json")
    except json.JSONDecodeError:
        _save(collection_json, "collection.json")

    readme = generate_readme(spec)
    _save(readme, "README.md")

    save_spec_snapshot(spec)

    print("\n" + "=" * 60)
    print(f"완료! {OUTPUT_DIR}/ 폴더를 확인하세요.")
    print("  API_DOCS.md    - 개발자용 API 문서")
    print("  collection.json - Postman에서 Import 가능")
    print("  README.md       - GitHub 프로젝트 README")
    print("=" * 60)


def run_diff(server_url: str = "http://localhost:8000"):
    old_spec = load_spec_snapshot()
    if old_spec is None:
        print("이전 스냅샷이 없습니다. 전체 파이프라인을 먼저 실행하세요.")
        print("  python main.py pipeline")
        return

    new_spec = fetch_openapi_spec(server_url)
    changes = get_changed_endpoints(old_spec, new_spec)

    if not changes:
        print("변경된 엔드포인트가 없습니다. 문서는 최신 상태입니다.")
        return

    diff_docs = generate_diff_docs(changes)
    _save(diff_docs, "API_CHANGES.md")
    save_spec_snapshot(new_spec)


# ── 진입점 ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "pipeline"
    server_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"

    spec = None

    if command == "pipeline":
        run_pipeline(server_url)

    elif command == "docs":
        spec = fetch_openapi_spec(server_url)
        docs = generate_api_docs(spec)
        _save(docs, "API_DOCS.md")

    elif command == "collection":
        spec = fetch_openapi_spec(server_url)
        raw = generate_postman_collection(spec)
        try:
            parsed = json.loads(raw)
            _save(json.dumps(parsed, ensure_ascii=False, indent=2), "collection.json")
        except json.JSONDecodeError:
            _save(raw, "collection.json")

    elif command == "readme":
        spec = fetch_openapi_spec(server_url)
        readme = generate_readme(spec)
        _save(readme, "README.md")

    elif command == "diff":
        run_diff(server_url)

    else:
        print(__doc__)
