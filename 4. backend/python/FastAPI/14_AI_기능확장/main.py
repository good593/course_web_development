"""
14교시: AI 기반 기능 확장

13교시 블로그 API에 Claude AI 기능을 추가합니다.
(DB 없이 인메모리로 실행 가능한 독립 예제)

실행 전 .env 파일에 ANTHROPIC_API_KEY 설정 필요.
  cp .env.example .env
  # .env에 실제 키 입력

실행: uvicorn main:app --reload
"""
import asyncio
import json
import re
import threading
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

load_dotenv()

app = FastAPI(title="블로그 API — AI 기능 확장", version="2.0.0")
client = anthropic.Anthropic()


# ── 인메모리 저장소 (12교시와 동일 구조) ──────────────────────────────────────

class Post:
    def __init__(self, id: int, title: str, content: str):
        self.id = id
        self.title = title
        self.content = content
        self.summary: str | None = None
        self.tags: list[str] = []
        self.published = True
        self.created_at = datetime.utcnow()

class Comment:
    def __init__(self, id: int, post_id: int, content: str, author: str):
        self.id = id
        self.post_id = post_id
        self.content = content
        self.author = author
        self.is_flagged = False
        self.created_at = datetime.utcnow()

posts: dict[int, Post] = {}
comments: dict[int, Comment] = {}
_post_seq = 0
_comment_seq = 0


def _next_post_id() -> int:
    global _post_seq
    _post_seq += 1
    return _post_seq

def _next_comment_id() -> int:
    global _comment_seq
    _comment_seq += 1
    return _comment_seq

def get_post_or_404(post_id: int) -> Post:
    p = posts.get(post_id)
    if not p:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
    return p

def get_comment_or_404(comment_id: int) -> Comment:
    c = comments.get(comment_id)
    if not c:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다")
    return c


# ── Pydantic 스키마 ───────────────────────────────────────────────────────────

class PostCreate(BaseModel):
    title: str
    content: str

class CommentCreate(BaseModel):
    content: str
    author: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: str | None
    tags: list[str]
    published: bool
    created_at: datetime

class CommentResponse(BaseModel):
    id: int
    post_id: int
    content: str
    author: str
    is_flagged: bool
    created_at: datetime

class TagSuggestionResponse(BaseModel):
    post_id: int
    tags: list[str]

class ModerationResult(BaseModel):
    comment_id: int
    is_spam: bool
    is_inappropriate: bool
    confidence: float
    reason: str

class PostReviewResponse(BaseModel):
    post_id: int
    score: int = Field(..., ge=1, le=10)
    strengths: list[str]
    improvements: list[str]
    overall: str

class FeatureRequest(BaseModel):
    feature: str = Field(..., description="추가할 기능 설명")
    context: str | None = Field(None, description="추가 컨텍스트")

class FeatureCodeResponse(BaseModel):
    feature: str
    generated_code: str


# ── Claude 호출 유틸 ──────────────────────────────────────────────────────────

async def call_claude(
    prompt: str,
    max_tokens: int = 1024,
    use_thinking: bool = True,
) -> str:
    """동기 Anthropic SDK를 비동기 컨텍스트에서 안전하게 호출."""
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
        # thinking 블록 제외 — TextBlock만 수집
        return "".join(b.text for b in resp.content if b.type == "text")

    try:
        return await asyncio.to_thread(_call)
    except anthropic.APIStatusError as e:
        raise HTTPException(status_code=503, detail=f"AI 서비스 오류: {e.message}")
    except anthropic.APITimeoutError:
        raise HTTPException(status_code=504, detail="AI 응답 시간 초과")


def _extract_json(text: str) -> dict:
    """응답 텍스트에서 JSON 객체를 추출."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise HTTPException(status_code=500, detail="AI 응답에서 JSON을 파싱할 수 없습니다")
    return json.loads(match.group())


# ── 기본 CRUD 엔드포인트 ──────────────────────────────────────────────────────

@app.get("/posts", response_model=list[PostResponse], tags=["Posts"])
def list_posts():
    return list(posts.values())

@app.get("/posts/{post_id}", response_model=PostResponse, tags=["Posts"])
def get_post(post_id: int):
    return get_post_or_404(post_id)

@app.post("/posts", response_model=PostResponse, status_code=201, tags=["Posts"])
def create_post(data: PostCreate):
    post = Post(id=_next_post_id(), title=data.title, content=data.content)
    posts[post.id] = post
    return post

@app.get("/posts/{post_id}/comments", response_model=list[CommentResponse], tags=["Comments"])
def list_comments(post_id: int):
    get_post_or_404(post_id)
    return [c for c in comments.values() if c.post_id == post_id]

@app.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=201, tags=["Comments"])
def add_comment(post_id: int, data: CommentCreate):
    get_post_or_404(post_id)
    comment = Comment(id=_next_comment_id(), post_id=post_id, **data.model_dump())
    comments[comment.id] = comment
    return comment


# ── AI 기능 엔드포인트 ────────────────────────────────────────────────────────

@app.post(
    "/posts/{post_id}/ai/summarize",
    response_model=PostResponse,
    tags=["AI Features"],
    summary="게시글 요약 자동 생성",
    description="Claude가 게시글 내용을 분석해 2~3문장으로 요약하고 summary 필드에 저장합니다.",
)
async def ai_summarize_post(post_id: int, force: bool = False):
    post = get_post_or_404(post_id)

    if post.summary and not force:
        return post

    prompt = f"""다음 블로그 게시글을 2~3문장으로 요약해줘.
요약문만 출력하고 다른 말은 하지 마.

제목: {post.title}
내용:
{post.content}"""

    summary = await call_claude(prompt, max_tokens=256)
    post.summary = summary.strip()
    return post


@app.post(
    "/posts/{post_id}/ai/tags",
    response_model=TagSuggestionResponse,
    tags=["AI Features"],
    summary="태그 자동 추천",
    description="Claude가 게시글 내용을 분석해 관련 태그 5개를 추천합니다.",
)
async def ai_suggest_tags(post_id: int, save: bool = False):
    post = get_post_or_404(post_id)

    prompt = f"""다음 블로그 게시글에 어울리는 태그를 5개 추천해줘.
반드시 아래 JSON 형식으로만 출력해:
{{"tags": ["태그1", "태그2", "태그3", "태그4", "태그5"]}}

제목: {post.title}
내용: {post.content[:1000]}"""

    raw = await call_claude(prompt, max_tokens=256, use_thinking=False)
    data = _extract_json(raw)
    tags = data.get("tags", [])

    if save:
        post.tags = tags

    return TagSuggestionResponse(post_id=post_id, tags=tags)


@app.post(
    "/posts/{post_id}/ai/review",
    response_model=PostReviewResponse,
    tags=["AI Features"],
    summary="글쓰기 품질 리뷰",
    description="Claude가 게시글의 구조, 명확성, 가독성을 1~10점으로 평가하고 개선점을 제안합니다.",
)
async def ai_review_post(post_id: int):
    post = get_post_or_404(post_id)

    prompt = f"""다음 블로그 게시글을 글쓰기 관점에서 평가해줘.
반드시 아래 JSON 형식으로만 출력해:
{{
  "score": 1~10 (전체 품질 점수),
  "strengths": ["잘된 점1", "잘된 점2"],
  "improvements": ["개선할 점1", "개선할 점2"],
  "overall": "전반적인 한 줄 평가"
}}

제목: {post.title}
내용:
{post.content}"""

    raw = await call_claude(prompt, max_tokens=512)
    data = _extract_json(raw)

    return PostReviewResponse(
        post_id=post_id,
        score=data.get("score", 5),
        strengths=data.get("strengths", []),
        improvements=data.get("improvements", []),
        overall=data.get("overall", ""),
    )


@app.post(
    "/comments/{comment_id}/ai/moderate",
    response_model=ModerationResult,
    tags=["AI Features"],
    summary="댓글 스팸/부적절 내용 감지",
    description="Claude가 댓글의 스팸 여부와 부적절한 내용을 감지합니다.",
)
async def ai_moderate_comment(comment_id: int, auto_flag: bool = True):
    comment = get_comment_or_404(comment_id)

    prompt = f"""다음 댓글이 스팸이거나 부적절한 내용인지 판단해줘.
반드시 아래 JSON 형식으로만 출력해:
{{
  "is_spam": true/false,
  "is_inappropriate": true/false,
  "confidence": 0.0~1.0,
  "reason": "판단 이유를 한 문장으로"
}}

댓글 내용: {comment.content}"""

    raw = await call_claude(prompt, max_tokens=256, use_thinking=False)
    data = _extract_json(raw)

    is_spam = data.get("is_spam", False)
    is_inappropriate = data.get("is_inappropriate", False)

    if auto_flag and (is_spam or is_inappropriate):
        comment.is_flagged = True

    return ModerationResult(
        comment_id=comment_id,
        is_spam=is_spam,
        is_inappropriate=is_inappropriate,
        confidence=data.get("confidence", 0.0),
        reason=data.get("reason", ""),
    )


@app.post(
    "/posts/{post_id}/ai/analyze/stream",
    tags=["AI Features"],
    summary="게시글 분석 (스트리밍)",
    description="Claude가 게시글을 분석하며 생성 즉시 텍스트를 스트리밍 전달합니다 (SSE).",
    response_class=StreamingResponse,
)
async def ai_analyze_stream(post_id: int):
    post = get_post_or_404(post_id)

    prompt = f"""다음 블로그 게시글을 심층 분석해줘:
1. 주제 및 핵심 메시지
2. 대상 독자
3. 논리적 구조 평가
4. 기술적 정확성 (해당 시)
5. 독자에게 미치는 영향

제목: {post.title}
내용:
{post.content}"""

    async def event_stream():
        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def producer():
            try:
                with client.messages.stream(
                    model="claude-opus-4-8",
                    max_tokens=2048,
                    messages=[{"role": "user", "content": prompt}],
                ) as stream:
                    for chunk in stream.text_stream:
                        asyncio.run_coroutine_threadsafe(queue.put(("data", chunk)), loop)
            except anthropic.APIStatusError as e:
                asyncio.run_coroutine_threadsafe(
                    queue.put(("error", f"AI 서비스 오류: {e.message}")),
                    loop,
                )
            except Exception as e:
                asyncio.run_coroutine_threadsafe(
                    queue.put(("error", f"스트리밍 오류: {type(e).__name__}")),
                    loop,
                )
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(("done", None)), loop)

        t = threading.Thread(target=producer, daemon=True)
        t.start()

        while True:
            kind, chunk = await queue.get()
            if kind == "done":
                break
            if kind == "error":
                yield f"event: error\ndata: {chunk}\n\n"
                continue
            escaped = chunk.replace("\n", "\\n")
            yield f"data: {escaped}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post(
    "/ai/generate-feature",
    response_model=FeatureCodeResponse,
    tags=["AI Features"],
    summary="Feature Request → 코드 자동 생성",
    description="기능 요청을 자연어로 입력하면 Claude가 FastAPI 엔드포인트 코드를 생성합니다.",
)
async def ai_generate_feature(request: FeatureRequest):
    current_code = Path(__file__).read_text(encoding="utf-8")

    prompt = f"""현재 FastAPI 블로그 API 코드를 참고해서 새 기능을 구현해줘.

[새 기능 요청]
{request.feature}

[추가 컨텍스트]
{request.context or "없음"}

[현재 코드 구조 요약]
{current_code[:2000]}

[출력 지침]
- 추가할 Pydantic 스키마 코드 (```python 블록)
- 추가할 엔드포인트 코드 (```python 블록)
- 사용 방법 간단 설명"""

    generated = await call_claude(prompt, max_tokens=4096)

    return FeatureCodeResponse(
        feature=request.feature,
        generated_code=generated,
    )


# ── 초기 데이터 ───────────────────────────────────────────────────────────────

@app.on_event("startup")
def seed_data():
    p1 = Post(
        id=_next_post_id(),
        title="FastAPI와 SQLAlchemy로 REST API 만들기",
        content="""FastAPI는 Python으로 고성능 REST API를 빠르게 개발할 수 있는 프레임워크입니다.

Pydantic v2를 기반으로 입출력 데이터 검증이 자동으로 이루어지며,
OpenAPI(Swagger) 문서가 자동 생성되어 팀원과 API 스펙을 쉽게 공유할 수 있습니다.

SQLAlchemy와 결합하면 ORM을 통해 데이터베이스를 Python 코드로 자연스럽게 다룰 수 있습니다.
이번 강의에서는 Repository/Service 패턴을 적용해 유지보수하기 쉬운 구조를 설계합니다.""",
    )
    p1.published = True
    posts[p1.id] = p1

    p2 = Post(
        id=_next_post_id(),
        title="Claude API로 AI 기능 추가하기",
        content="""Anthropic의 Claude API를 사용하면 기존 서비스에 AI 기능을 손쉽게 추가할 수 있습니다.

텍스트 요약, 태그 추천, 감정 분석, 코드 생성 등 다양한 기능을 프롬프트 엔지니어링만으로 구현할 수 있습니다.
Adaptive Thinking 기능을 활용하면 복잡한 분석 작업에서 더욱 정확한 결과를 얻을 수 있습니다.

스트리밍 API를 통해 AI 응답을 실시간으로 사용자에게 전달하면 UX를 크게 개선할 수 있습니다.""",
    )
    p2.published = True
    posts[p2.id] = p2

    c1 = Comment(id=_next_comment_id(), post_id=1, content="정말 유익한 글이에요!", author="독자1")
    c2 = Comment(id=_next_comment_id(), post_id=1, content="지금 바로 무료로 받아가세요! bit.ly/spam123", author="스패머")
    comments[c1.id] = c1
    comments[c2.id] = c2
