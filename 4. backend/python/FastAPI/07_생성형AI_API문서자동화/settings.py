"""수업 예제 전체에서 함께 쓰는 설정값을 모아 둔 파일입니다."""

from pathlib import Path
from typing import Literal

# Groq 모델이 사용할 추론 강도를 제한된 문자열 중 하나로 받기 위한 타입입니다.
ReasoningEffort = Literal["low", "medium", "high"]

# 문서 생성에 사용할 모델명과 생성 파일을 저장할 폴더입니다.
MODEL = "openai/gpt-oss-120b"
OUTPUT_DIR = Path("output")

# README의 uvicorn 실행 포트와 DocumentGenerationRequest 기본값을 맞춥니다.
DEFAULT_OPENAPI_URL = "http://localhost:8001"

# 실습 계정의 토큰 한도를 넘기지 않도록 응답별 최대 토큰 수를 작게 나눕니다.
GROQ_TPM_SAFE_LIMIT = 7600
DOCS_MAX_TOKENS = 3072
COLLECTION_MAX_TOKENS = 4096
README_MAX_TOKENS = 2048
DIFF_MAX_TOKENS = 2048
