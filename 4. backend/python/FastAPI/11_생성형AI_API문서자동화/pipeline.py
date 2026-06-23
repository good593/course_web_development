import json

from services.document_generator import (
    generate_api_docs,
    generate_diff_docs,
    generate_postman_collection,
    generate_readme,
)
from services.openapi_spec import fetch_openapi_spec
from services.storage import load_spec_snapshot, save_output, save_spec_snapshot
from settings import OUTPUT_DIR


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

    for path, methods in old_paths.items():
        for method in methods:
            if method not in new_paths.get(path, {}):
                changes.append({"path": path, "method": method.upper(), "is_deleted": True})

    return changes


def save_collection(raw: str) -> None:
    try:
        parsed = json.loads(raw)
        save_output(json.dumps(parsed, ensure_ascii=False, indent=2), "collection.json")
    except json.JSONDecodeError:
        save_output(raw, "collection.json")


def run_pipeline(server_url: str = "http://localhost:8001") -> None:
    print("=" * 60)
    print("API 문서 자동화 파이프라인")
    print("=" * 60)

    spec = fetch_openapi_spec(server_url)

    docs = generate_api_docs(spec)
    save_output(docs, "API_DOCS.md")

    collection_json = generate_postman_collection(spec)
    save_collection(collection_json)

    readme = generate_readme(spec)
    save_output(readme, "README.md")

    save_spec_snapshot(spec)

    print("\n" + "=" * 60)
    print(f"완료! {OUTPUT_DIR}/ 폴더를 확인하세요.")
    print("  API_DOCS.md    - 개발자용 API 문서")
    print("  collection.json - Postman에서 Import 가능")
    print("  README.md       - GitHub 프로젝트 README")
    print("=" * 60)


def run_diff(server_url: str = "http://localhost:8001") -> None:
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
    save_output(diff_docs, "API_CHANGES.md")
    save_spec_snapshot(new_spec)
