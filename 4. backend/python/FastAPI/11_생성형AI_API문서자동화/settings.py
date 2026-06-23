from pathlib import Path
from typing import Literal

ReasoningEffort = Literal["low", "medium", "high"]

MODEL = "openai/gpt-oss-120b"
OUTPUT_DIR = Path("output")
DEFAULT_OPENAPI_URL = "http://localhost:8001/openapi.json"

GROQ_TPM_SAFE_LIMIT = 7600
DOCS_MAX_TOKENS = 3072
COLLECTION_MAX_TOKENS = 4096
README_MAX_TOKENS = 2048
DIFF_MAX_TOKENS = 2048
