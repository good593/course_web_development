import json
from typing import Any

import httpx

from settings import DEFAULT_OPENAPI_URL


class OpenAPISpecError(RuntimeError):
    """OpenAPI 스펙을 가져올 수 없을 때 사용하는 예외."""


def compact_schema(schema: Any, components: dict[str, Any], seen: set[str] | None = None) -> Any:
    """프롬프트용으로 JSON Schema의 핵심 정보만 남깁니다."""
    if not isinstance(schema, dict):
        return schema

    seen = seen or set()

    # OpenAPI의 $ref는 components/schemas에 있는 실제 스키마를 가리키는 별칭입니다.
    # 엔드포인트마다 같은 스키마를 계속 펼치면 프롬프트가 너무 커지므로 이름만 남깁니다.
    if "$ref" in schema:
        ref = schema["$ref"]
        name = ref.rsplit("/", 1)[-1]
        return {"ref": name}

    # LLM 프롬프트에 꼭 필요한 검증 조건과 설명만 남겨 토큰 사용량을 줄입니다.
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
        # 객체의 각 필드도 같은 방식으로 재귀적으로 압축합니다.
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
    """requestBody 또는 response content에서 JSON 예시와 스키마만 추립니다."""
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
    """경로/쿼리 파라미터에서 문서 생성에 필요한 정보만 추립니다."""
    compact = {
        key: parameter[key]
        for key in ("name", "in", "required", "description", "example", "examples")
        if key in parameter
    }
    if "schema" in parameter:
        compact["schema"] = compact_schema(parameter["schema"], components)
    return compact


def compact_component_schemas(components: dict[str, Any]) -> dict[str, Any]:
    """중복 확장을 줄이기 위해 Pydantic 스키마 정의를 한 번만 모읍니다."""
    skipped = {"HTTPValidationError", "ValidationError"}
    return {
        name: compact_schema(schema, components)
        for name, schema in components.items()
        if name not in skipped
    }


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
    if components:
        compact["schemas"] = compact_component_schemas(components)

    for path, methods in spec.get("paths", {}).items():
        compact["paths"][path] = {}
        for method, operation in methods.items():
            # Swagger 내부용 메서드가 섞여도 실제 HTTP 메서드만 문서화합니다.
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue

            op = {
                key: operation[key]
                for key in ("tags", "summary", "description")
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
    """압축한 OpenAPI 스펙을 줄바꿈 없는 JSON 문자열로 만들어 토큰을 절약합니다."""
    compact = compact_openapi_spec(spec)
    return json.dumps(compact, ensure_ascii=False, separators=(",", ":"))


def build_openapi_url(base_or_spec_url: str) -> str:
    """서버 기본 URL 또는 openapi.json 전체 URL을 모두 허용합니다."""
    url = base_or_spec_url.rstrip("/")
    if url.endswith("/openapi.json"):
        return url
    return f"{url}/openapi.json"


def fetch_openapi_spec(url: str = DEFAULT_OPENAPI_URL) -> dict:
    """서버의 /openapi.json을 HTTP로 요청해 파이썬 dict로 반환합니다."""
    spec_url = build_openapi_url(url)
    try:
        response = httpx.get(spec_url, timeout=5)
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError as error:
        raise OpenAPISpecError(f"서버에 연결할 수 없습니다: {spec_url}") from error
    except httpx.RequestError as error:
        raise OpenAPISpecError(f"OpenAPI 스펙 요청 중 오류가 발생했습니다: {error}") from error
    except httpx.HTTPStatusError as error:
        raise OpenAPISpecError(
            f"OpenAPI 스펙 요청 실패: {error.response.status_code} {spec_url}"
        ) from error
    except ValueError as error:
        raise OpenAPISpecError(f"OpenAPI 스펙이 JSON 형식이 아닙니다: {spec_url}") from error
