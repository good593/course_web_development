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
    return sum(len(methods) for methods in spec.get("paths", {}).values())


def to_file_info(path: Path, description: str) -> dict:
    return {
        "filename": path.name,
        "path": str(path),
        "description": description,
    }


def save_collection(raw: str) -> Path:
    try:
        parsed = json.loads(raw)
        content = json.dumps(parsed, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        content = raw
    return save_output(content, "collection.json")


def get_changed_endpoints(old_spec: dict, new_spec: dict) -> list[dict]:
    changes = []
    old_paths = old_spec.get("paths", {})
    new_paths = new_spec.get("paths", {})

    for path, methods in new_paths.items():
        for method, details in methods.items():
            old_details = old_paths.get(path, {}).get(method)
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
            if method not in new_paths.get(path, {}):
                changes.append({"path": path, "method": method.upper(), "is_deleted": True})

    return changes


def create_api_docs(server_url: str = DEFAULT_OPENAPI_URL) -> dict:
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
