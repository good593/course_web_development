import json
import sys
from typing import Any

import httpx

from settings import DEFAULT_OPENAPI_URL


def compact_schema(schema: Any, components: dict[str, Any], seen: set[str] | None = None) -> Any:
    """프롬프트용으로 JSON Schema의 핵심 정보만 남깁니다."""
    if not isinstance(schema, dict):
        return schema

    seen = seen or set()

    if "$ref" in schema:
        ref = schema["$ref"]
        name = ref.rsplit("/", 1)[-1]
        if name in seen:
            return {"ref": name}
        target = components.get(name)
        if target is None:
            return {"ref": name}
        compact = compact_schema(target, components, seen | {name})
        if isinstance(compact, dict):
            compact.setdefault("name", name)
        return compact

    keep_keys = {
        "type",
        "format",
        "description",
        "enum",
        "default",
        "example",
        "examples",
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "minLength",
        "maxLength",
        "minItems",
        "maxItems",
        "required",
    }
    compact = {key: schema[key] for key in keep_keys if key in schema}

    if "properties" in schema:
        compact["properties"] = {
            name: compact_schema(value, components, seen)
            for name, value in schema["properties"].items()
        }

    if "items" in schema:
        compact["items"] = compact_schema(schema["items"], components, seen)

    for key in ("anyOf", "oneOf", "allOf"):
        if key in schema:
            compact[key] = [compact_schema(item, components, seen) for item in schema[key]]

    return compact


def compact_content(content: dict[str, Any] | None, components: dict[str, Any]) -> dict[str, Any] | None:
    if not content:
        return None

    media = content.get("application/json") or next(iter(content.values()), None)
    if not isinstance(media, dict):
        return None

    compact: dict[str, Any] = {}
    if "schema" in media:
        compact["schema"] = compact_schema(media["schema"], components)
    for key in ("example", "examples"):
        if key in media:
            compact[key] = media[key]
    return compact or None


def compact_parameter(parameter: dict[str, Any], components: dict[str, Any]) -> dict[str, Any]:
    compact = {
        key: parameter[key]
        for key in ("name", "in", "required", "description", "example", "examples")
        if key in parameter
    }
    if "schema" in parameter:
        compact["schema"] = compact_schema(parameter["schema"], components)
    return compact


def compact_openapi_spec(spec: dict) -> dict:
    """LLM 프롬프트에 필요한 OpenAPI 정보만 추립니다."""
    components = spec.get("components", {}).get("schemas", {})
    security_schemes = spec.get("components", {}).get("securitySchemes", {})
    compact: dict[str, Any] = {
        "info": {
            key: spec.get("info", {}).get(key)
            for key in ("title", "summary", "description", "version")
            if spec.get("info", {}).get(key)
        },
        "paths": {},
    }

    if spec.get("servers"):
        compact["servers"] = spec["servers"]
    if security_schemes:
        compact["securitySchemes"] = security_schemes

    for path, methods in spec.get("paths", {}).items():
        compact["paths"][path] = {}
        for method, operation in methods.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue

            op = {
                key: operation[key]
                for key in ("tags", "summary", "description", "operationId")
                if key in operation
            }

            if operation.get("parameters"):
                op["parameters"] = [
                    compact_parameter(parameter, components)
                    for parameter in operation["parameters"]
                ]

            request_body = operation.get("requestBody", {})
            request_content = compact_content(request_body.get("content"), components)
            if request_content:
                op["requestBody"] = {
                    "required": request_body.get("required", False),
                    "content": request_content,
                }

            responses: dict[str, Any] = {}
            for status, response in operation.get("responses", {}).items():
                response_info: dict[str, Any] = {
                    "description": response.get("description", "")
                }
                response_content = compact_content(response.get("content"), components)
                if response_content and status != "422":
                    response_info["content"] = response_content
                responses[status] = response_info
            if responses:
                op["responses"] = responses

            if operation.get("security"):
                op["security"] = operation["security"]

            compact["paths"][path][method] = op

    return compact


def format_spec_for_prompt(spec: dict) -> str:
    compact = compact_openapi_spec(spec)
    return json.dumps(compact, ensure_ascii=False, separators=(",", ":"))


def build_openapi_url(base_or_spec_url: str) -> str:
    """서버 기본 URL 또는 openapi.json 전체 URL을 모두 허용합니다."""
    url = base_or_spec_url.rstrip("/")
    if url.endswith("/openapi.json"):
        return url
    return f"{url}/openapi.json"


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
        print("api_server.py FastAPI 서버를 먼저 실행하세요.")
        print("  uvicorn api_server:app --reload --port 8001")
        sys.exit(1)
    except httpx.RequestError as error:
        print(f"OpenAPI 스펙 요청 중 오류가 발생했습니다: {error}")
        sys.exit(1)
    except httpx.HTTPStatusError as error:
        print(f"OpenAPI 스펙 요청 실패: {error.response.status_code} {spec_url}")
        sys.exit(1)
    except ValueError:
        print(f"OpenAPI 스펙이 JSON 형식이 아닙니다: {spec_url}")
        sys.exit(1)
