import json
from pathlib import Path

from services.document_generator import (
    generate_api_docs,
    generate_diff_docs,
    generate_postman_collection,
    generate_readme,
)
from services.openapi_spec import fetch_openapi_spec
from services.storage import load_spec_snapshot, save_output, save_spec_snapshot
from settings import DEFAULT_OPENAPI_URL


class MissingSnapshotError(RuntimeError):
    """변경 문서화를 위한 이전 OpenAPI 스냅샷이 없을 때 사용하는 예외."""


def count_endpoints(spec: dict) -> int:
    """OpenAPI paths 아래의 HTTP 메서드 개수를 세어 엔드포인트 수로 사용합니다."""
    return sum(len(methods) for methods in spec.get("paths", {}).values())


def to_file_info(path: Path, description: str) -> dict:
    """파일 저장 결과를 API 응답에 넣기 좋은 딕셔너리로 바꿉니다."""
    return {
        "filename": path.name,
        "path": str(path),
        "description": description,
    }


def save_collection(raw: str) -> Path:
    """AI가 만든 Collection 문자열을 가능하면 예쁜 JSON으로 정리해 저장합니다."""
    try:
        parsed = json.loads(raw)
        content = json.dumps(parsed, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        content = raw
    return save_output(content, "collection.json")


def get_changed_endpoints(old_spec: dict, new_spec: dict) -> list[dict]:
    """이전 OpenAPI 스펙과 현재 스펙을 비교해 추가/수정/삭제된 엔드포인트를 찾습니다."""
    changes = []
    old_paths = old_spec.get("paths", {})
    new_paths = new_spec.get("paths", {})

    for path, methods in new_paths.items():
        for method, details in methods.items():
            old_details = old_paths.get(path, {}).get(method)
            # 새 스펙의 내용이 이전과 다르면 신규 또는 수정된 엔드포인트입니다.
            if old_details != details:
                changes.append(
                    {
                        "path": path,
                        "method": method.upper(),
                        "is_new": old_details is None,
                        "details": details,
                    }
                )

    for path, methods in old_paths.items():
        for method in methods:
            # 이전에는 있었지만 새 스펙에 없으면 삭제된 엔드포인트입니다.
            if method not in new_paths.get(path, {}):
                changes.append({"path": path, "method": method.upper(), "is_deleted": True})

    return changes


def create_api_docs(server_url: str = DEFAULT_OPENAPI_URL) -> dict:
    """OpenAPI 스펙을 가져와 개발자용 API 문서를 생성하고 저장합니다."""
    spec = fetch_openapi_spec(server_url)
    content = generate_api_docs(spec)
    path = save_output(content, "API_DOCS.md")
    return {
        "endpoint_count": count_endpoints(spec),
        "filename": path.name,
        "path": str(path),
        "content": content,
    }


def create_postman_collection(server_url: str = DEFAULT_OPENAPI_URL) -> dict:
    """OpenAPI 스펙을 가져와 Postman Collection 파일을 생성하고 저장합니다."""
    spec = fetch_openapi_spec(server_url)
    content = generate_postman_collection(spec)
    path = save_collection(content)
    return {
        "endpoint_count": count_endpoints(spec),
        "filename": path.name,
        "path": str(path),
        "content": content,
    }


def create_readme(server_url: str = DEFAULT_OPENAPI_URL) -> dict:
    """OpenAPI 스펙을 가져와 README 초안을 생성하고 저장합니다."""
    spec = fetch_openapi_spec(server_url)
    content = generate_readme(spec)
    path = save_output(content, "README.md")
    return {
        "endpoint_count": count_endpoints(spec),
        "filename": path.name,
        "path": str(path),
        "content": content,
    }


def create_all_documents(server_url: str = DEFAULT_OPENAPI_URL) -> dict:
    """세 종류의 문서를 한 번에 만들고, 다음 비교를 위해 스냅샷도 저장합니다."""
    spec = fetch_openapi_spec(server_url)

    docs_path = save_output(generate_api_docs(spec), "API_DOCS.md")
    collection_path = save_collection(generate_postman_collection(spec))
    readme_path = save_output(generate_readme(spec), "README.md")
    save_spec_snapshot(spec)

    return {
        "endpoint_count": count_endpoints(spec),
        "files": [
            to_file_info(docs_path, "개발자용 API 문서"),
            to_file_info(collection_path, "Postman Import용 Collection"),
            to_file_info(readme_path, "GitHub README 초안"),
        ],
        "message": "문서 생성이 완료되었습니다.",
    }


def create_change_docs(server_url: str = DEFAULT_OPENAPI_URL) -> dict:
    """저장된 스냅샷과 현재 스펙의 차이만 문서화합니다."""
    old_spec = load_spec_snapshot()
    if old_spec is None:
        raise MissingSnapshotError("이전 스냅샷이 없습니다. 먼저 /ai-docs/generate-all을 실행하세요.")

    new_spec = fetch_openapi_spec(server_url)
    changes = get_changed_endpoints(old_spec, new_spec)

    if not changes:
        save_spec_snapshot(new_spec)
        return {
            "endpoint_count": count_endpoints(new_spec),
            "filename": None,
            "path": None,
            "content": "변경된 엔드포인트가 없습니다. 문서는 최신 상태입니다.",
        }

    content = generate_diff_docs(changes)
    path = save_output(content, "API_CHANGES.md")
    save_spec_snapshot(new_spec)
    return {
        "endpoint_count": count_endpoints(new_spec),
        "filename": path.name,
        "path": str(path),
        "content": content,
    }
