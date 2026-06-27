import json
import re
from pathlib import Path

from settings import OUTPUT_DIR


def save_output(content: str, filename: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / filename
    path.write_text(content, encoding="utf-8")
    print(f"저장 완료: {path}")
    return path


def extract_json(text: str) -> str:
    """마크다운 코드 블록에서 JSON 추출."""
    match = re.search(r"```(?:json)?\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def save_spec_snapshot(spec: dict) -> None:
    """변경 감지를 위해 현재 스펙을 저장합니다."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "_spec_snapshot.json").write_text(
        json.dumps(spec, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_spec_snapshot() -> dict | None:
    path = OUTPUT_DIR / "_spec_snapshot.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None
