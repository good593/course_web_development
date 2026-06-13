"""
15교시: AI 기반 코드 리뷰

Claude를 사용한 자동화 코드 리뷰 도구입니다.
FastAPI 서버와 CLI 두 가지 방식으로 실행할 수 있습니다.

실행 전 .env 파일에 ANTHROPIC_API_KEY 설정 필요.

[FastAPI 서버 모드]
  uvicorn main:app --reload

[CLI 모드]
  python main.py review main.py               # 파일 리뷰
  python main.py project main.py models.py    # 프로젝트 리뷰
  python main.py pr [base_branch]             # PR diff 리뷰
  python main.py pr-file changes.diff         # diff 파일 리뷰
"""
import asyncio
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(title="AI 코드 리뷰 서버", version="1.0.0")
client = anthropic.Anthropic()

# 최근 리뷰 기록 (인메모리)
review_history: list[dict] = []


# ── Pydantic 스키마 ───────────────────────────────────────────────────────────

class ReviewIssue(BaseModel):
    category: str = Field(..., description="security|performance|architecture|readability")
    severity: str = Field(..., description="critical|warning|info")
    line: int | None = None
    description: str
    suggestion: str

class ReviewResult(BaseModel):
    file_path: str
    score: int = Field(..., ge=1, le=10)
    summary: str
    issues: list[ReviewIssue]
    positives: list[str]
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectReviewResult(BaseModel):
    files: list[str]
    architecture_score: int = Field(..., ge=1, le=10)
    consistency_issues: list[str]
    security_issues: list[str]
    duplicate_code: list[str]
    recommendations: list[str]
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)

class PRReviewResult(BaseModel):
    approve: bool
    summary: str
    issues: list[dict]
    test_suggestions: list[str]
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)

class FileReviewRequest(BaseModel):
    file_path: str | None = None
    code: str | None = None
    focus: list[str] = Field(
        default=["security", "performance", "architecture", "readability"]
    )

class ProjectReviewRequest(BaseModel):
    file_paths: list[str]

class DiffReviewRequest(BaseModel):
    diff: str
    context: str | None = None


# ── Claude 호출 유틸 ──────────────────────────────────────────────────────────

async def call_claude(
    prompt: str,
    max_tokens: int = 4096,
    use_thinking: bool = True,
) -> str:
    def _call():
        kwargs = {}
        if use_thinking:
            kwargs["thinking"] = {"type": "adaptive"}

        resp = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return "".join(b.text for b in resp.content if b.type == "text")

    try:
        return await asyncio.to_thread(_call)
    except anthropic.APIStatusError as e:
        raise HTTPException(status_code=503, detail=f"AI 서비스 오류: {e.message}")


def _extract_json(text: str) -> dict:
    """텍스트에서 가장 큰 JSON 객체 추출."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise HTTPException(status_code=500, detail="AI 응답에서 JSON을 파싱할 수 없습니다")
    try:
        return json.loads(match.group())
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"JSON 파싱 실패: {e}")


# ── 핵심 리뷰 함수 ────────────────────────────────────────────────────────────

async def review_code(
    code: str,
    file_label: str,
    focus: list[str] | None = None,
) -> ReviewResult:
    focus_str = ", ".join(focus) if focus else "security, performance, architecture, readability"
    focus_ko = focus_str.replace("security", "보안").replace("performance", "성능") \
                        .replace("architecture", "아키텍처").replace("readability", "가독성")

    prompt = f"""다음 Python 코드를 [{focus_ko}] 관점에서 상세히 리뷰해줘.

반드시 아래 JSON 형식으로만 출력해:
{{
  "score": 1~10,
  "summary": "전반적인 코드 품질 한 줄 요약",
  "issues": [
    {{
      "category": "security|performance|architecture|readability",
      "severity": "critical|warning|info",
      "line": 줄번호_또는_null,
      "description": "이슈 설명",
      "suggestion": "구체적인 개선 방법"
    }}
  ],
  "positives": ["잘 구현된 점1", "잘 구현된 점2"]
}}

[파일: {file_label}]
```python
{code[:4000]}
```"""

    raw = await call_claude(prompt, max_tokens=4096)
    data = _extract_json(raw)

    issues = [ReviewIssue(**i) for i in data.get("issues", [])]
    result = ReviewResult(
        file_path=file_label,
        score=data.get("score", 5),
        summary=data.get("summary", ""),
        issues=issues,
        positives=data.get("positives", []),
    )
    review_history.append(result.model_dump(mode="json"))
    return result


async def review_project_files(file_paths: list[str]) -> ProjectReviewResult:
    files_content = []
    valid_files = []
    for path in file_paths:
        p = Path(path)
        if p.exists():
            code = p.read_text(encoding="utf-8")
            files_content.append(f"=== {path} ===\n{code[:2000]}")
            valid_files.append(path)
        else:
            files_content.append(f"=== {path} === [파일 없음]")

    combined = "\n\n".join(files_content)

    prompt = f"""다음 FastAPI 프로젝트의 여러 파일을 종합적으로 리뷰해줘.

[검토 관점]
1. 파일 간 의존성 방향 (Repository ← Service ← Router 원칙)
2. 스키마 일관성 (Create/Update/Response 분리)
3. 에러 처리 일관성
4. 중복 코드
5. 보안 취약점

반드시 아래 JSON 형식으로만 출력해:
{{
  "architecture_score": 1~10,
  "consistency_issues": ["이슈1", "이슈2"],
  "security_issues": ["보안이슈1"],
  "duplicate_code": ["중복패턴1"],
  "recommendations": ["개선제안1", "개선제안2"]
}}

[프로젝트 파일들]
{combined}"""

    raw = await call_claude(prompt, max_tokens=4096)
    data = _extract_json(raw)

    return ProjectReviewResult(
        files=valid_files,
        architecture_score=data.get("architecture_score", 5),
        consistency_issues=data.get("consistency_issues", []),
        security_issues=data.get("security_issues", []),
        duplicate_code=data.get("duplicate_code", []),
        recommendations=data.get("recommendations", []),
    )


async def review_diff(diff: str, context: str | None = None) -> PRReviewResult:
    if not diff.strip():
        return PRReviewResult(
            approve=True,
            summary="변경된 Python 파일이 없습니다.",
            issues=[],
            test_suggestions=[],
        )

    context_section = f"\n[컨텍스트]\n{context}" if context else ""

    prompt = f"""다음 Git diff를 PR 코드 리뷰 관점에서 검토해줘.
추가된 코드(+로 시작하는 줄)를 중심으로 분석하되, 제거된 코드(-)의 맥락도 참고해.
{context_section}

반드시 아래 JSON 형식으로만 출력해:
{{
  "approve": true/false,
  "summary": "변경사항 2~3줄 요약",
  "issues": [
    {{
      "severity": "critical|warning|info",
      "description": "이슈 설명",
      "line_hint": "관련 코드 힌트"
    }}
  ],
  "test_suggestions": ["추가하면 좋을 테스트케이스1", "테스트케이스2"]
}}

[Git Diff]
{diff[:5000]}"""

    raw = await call_claude(prompt, max_tokens=2048)
    data = _extract_json(raw)

    return PRReviewResult(
        approve=data.get("approve", True),
        summary=data.get("summary", ""),
        issues=data.get("issues", []),
        test_suggestions=data.get("test_suggestions", []),
    )


async def generate_report(review: ReviewResult) -> str:
    """리뷰 결과를 마크다운 리포트로 변환."""
    prompt = f"""다음 코드 리뷰 결과를 마크다운 리포트로 작성해줘.

[포함할 내용]
- 점수와 요약 (헤더 포함)
- 심각도별 이슈 목록 (critical → warning → info 순)
- 각 이슈에 개선 코드 예시 (있다면)
- 잘된 점
- 우선 수정 체크리스트

[리뷰 데이터]
{json.dumps(review.model_dump(mode="json"), ensure_ascii=False, indent=2)}"""

    return await call_claude(prompt, max_tokens=4096)


# ── FastAPI 엔드포인트 ────────────────────────────────────────────────────────

@app.post(
    "/review/file",
    response_model=ReviewResult,
    tags=["Review"],
    summary="파일 코드 리뷰",
    description="파일 경로 또는 코드 텍스트를 직접 입력해 리뷰합니다.",
)
async def api_review_file(request: FileReviewRequest):
    if request.file_path:
        path = Path(request.file_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"파일을 찾을 수 없습니다: {request.file_path}")
        code = path.read_text(encoding="utf-8")
        label = request.file_path
    elif request.code:
        code = request.code
        label = "<직접 입력>"
    else:
        raise HTTPException(status_code=400, detail="file_path 또는 code 중 하나를 제공해야 합니다")

    return await review_code(code, label, request.focus)


@app.post(
    "/review/project",
    response_model=ProjectReviewResult,
    tags=["Review"],
    summary="프로젝트 종합 리뷰",
    description="여러 파일을 묶어 아키텍처와 일관성을 종합 분석합니다.",
)
async def api_review_project(request: ProjectReviewRequest):
    if not request.file_paths:
        raise HTTPException(status_code=400, detail="파일 경로 목록이 비어있습니다")
    return await review_project_files(request.file_paths)


@app.post(
    "/review/diff",
    response_model=PRReviewResult,
    tags=["Review"],
    summary="Git diff 리뷰",
    description="Git diff 텍스트를 분석해 변경사항을 검토합니다.",
)
async def api_review_diff(request: DiffReviewRequest):
    return await review_diff(request.diff, request.context)


@app.post(
    "/review/report",
    response_class=JSONResponse,
    tags=["Review"],
    summary="리뷰 결과 → 마크다운 리포트",
)
async def api_generate_report(review: ReviewResult):
    report = await generate_report(review)
    return {"report": report}


@app.get(
    "/review/history",
    tags=["Review"],
    summary="최근 리뷰 기록",
)
def api_review_history(limit: int = 10):
    return review_history[-limit:]


# ── CLI 모드 ──────────────────────────────────────────────────────────────────

def _print_review(result: ReviewResult):
    print(f"\n{'='*60}")
    print(f"파일: {result.file_path}")
    print(f"점수: {result.score}/10")
    print(f"요약: {result.summary}")

    if result.issues:
        print(f"\n[이슈 {len(result.issues)}건]")
        for issue in sorted(result.issues, key=lambda x: {"critical": 0, "warning": 1, "info": 2}[x.severity]):
            line_info = f" (line {issue.line})" if issue.line else ""
            print(f"  [{issue.severity.upper()}] [{issue.category}]{line_info}")
            print(f"    문제: {issue.description}")
            print(f"    제안: {issue.suggestion}")

    if result.positives:
        print(f"\n[잘된 점]")
        for p in result.positives:
            print(f"  [OK] {p}")
    print('='*60)


async def cli_review_file(file_path: str, focus: list[str] | None = None):
    path = Path(file_path)
    if not path.exists():
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return

    print(f"'{file_path}' 리뷰 중...")
    code = path.read_text(encoding="utf-8")
    result = await review_code(code, file_path, focus)
    _print_review(result)

    output_path = path.stem + "_REVIEW.md"
    report = await generate_report(result)
    Path(output_path).write_text(report, encoding="utf-8")
    print(f"\n리포트 저장: {output_path}")


async def cli_review_project(file_paths: list[str]):
    print(f"프로젝트 리뷰 중: {', '.join(file_paths)}")
    result = await review_project_files(file_paths)

    print(f"\n{'='*60}")
    print(f"아키텍처 점수: {result.architecture_score}/10")

    if result.security_issues:
        print(f"\n[보안 이슈]")
        for issue in result.security_issues:
            print(f"  [WARN] {issue}")

    if result.consistency_issues:
        print(f"\n[일관성 이슈]")
        for issue in result.consistency_issues:
            print(f"  ! {issue}")

    if result.recommendations:
        print(f"\n[개선 권장사항]")
        for rec in result.recommendations:
            print(f"  → {rec}")
    print('='*60)


async def cli_review_pr(base_branch: str = "main"):
    print(f"'{base_branch}' 대비 변경사항 추출 중...")
    result = subprocess.run(
        ["git", "diff", f"{base_branch}...HEAD", "--", "*.py"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"git diff 실패: {result.stderr}")
        return
    await _review_and_print_diff(result.stdout)


async def cli_review_pr_file(diff_file: str):
    path = Path(diff_file)
    if not path.exists():
        print(f"diff 파일을 찾을 수 없습니다: {diff_file}")
        return
    diff = path.read_text(encoding="utf-8")
    await _review_and_print_diff(diff)


async def _review_and_print_diff(diff: str):
    print("AI 리뷰 중...")
    result = await review_diff(diff)

    print(f"\n{'='*60}")
    print(f"승인: {'✅ APPROVE' if result.approve else '❌ REQUEST CHANGES'}")
    print(f"요약: {result.summary}")

    if result.issues:
        print(f"\n[이슈 {len(result.issues)}건]")
        for issue in result.issues:
            print(f"  [{issue['severity'].upper()}] {issue['description']}")
            if issue.get('line_hint'):
                print(f"    관련: {issue['line_hint']}")

    if result.test_suggestions:
        print(f"\n[테스트 제안]")
        for ts in result.test_suggestions:
            print(f"  → {ts}")
    print('='*60)


# ── 진입점 ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1]

    if command == "review":
        if len(sys.argv) < 3:
            print("사용법: python main.py review <파일경로>")
            sys.exit(1)
        file_path = sys.argv[2]
        focus_arg = sys.argv[3].split(",") if len(sys.argv) > 3 else None
        asyncio.run(cli_review_file(file_path, focus_arg))

    elif command == "project":
        if len(sys.argv) < 3:
            print("사용법: python main.py project <파일1> <파일2> ...")
            sys.exit(1)
        asyncio.run(cli_review_project(sys.argv[2:]))

    elif command == "pr":
        base = sys.argv[2] if len(sys.argv) > 2 else "main"
        asyncio.run(cli_review_pr(base))

    elif command == "pr-file":
        if len(sys.argv) < 3:
            print("사용법: python main.py pr-file <diff파일경로>")
            sys.exit(1)
        asyncio.run(cli_review_pr_file(sys.argv[2]))

    else:
        print(__doc__)
