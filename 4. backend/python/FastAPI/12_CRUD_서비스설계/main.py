"""
12교시: CRUD 기반 백엔드 서비스 설계

SQLite를 사용해 실제로 데이터가 저장되는 CRUD API를 만듭니다.
Router / Service / Repository 계층을 분리해 SQL이 라우터로 새지 않게 합니다.

실행: uvicorn main:app --reload
"""
from datetime import UTC, datetime
from pathlib import Path
import sqlite3
from typing import Any, Iterator

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

DATABASE_PATH = Path("blog.db")

app = FastAPI(title="블로그 API - SQLite CRUD 데모")


# ── Pydantic 스키마 ───────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None = None


class PostCreate(BaseModel):
    title: str = Field(..., max_length=200)
    content: str
    category_id: int | None = None


class PostUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    content: str | None = None
    summary: str | None = None
    published: bool | None = None
    category_id: int | None = None


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: str | None
    published: bool
    category_id: int | None = None
    created_at: datetime
    updated_at: datetime


class PostDetailResponse(PostResponse):
    category: CategoryResponse | None = None
    comment_count: int = 0


class CommentCreate(BaseModel):
    content: str
    author: str = Field(..., max_length=100)


class CommentResponse(BaseModel):
    id: int
    content: str
    author: str
    post_id: int
    created_at: datetime


# ── SQLite 연결과 초기화 ─────────────────────────────────────────────────────

def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def dict_from_row(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None

    data = dict(row)
    if "published" in data:
        data["published"] = bool(data["published"])
    return data


def get_db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                summary TEXT,
                published INTEGER NOT NULL DEFAULT 0,
                category_id INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (category_id)
                    REFERENCES categories(id)
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                author TEXT NOT NULL,
                post_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (post_id)
                    REFERENCES posts(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_posts_category_id
                ON posts(category_id);
            CREATE INDEX IF NOT EXISTS idx_posts_created_at
                ON posts(created_at);
            CREATE INDEX IF NOT EXISTS idx_comments_post_id
                ON comments(post_id);
            """
        )


# ── Repository 계층 ───────────────────────────────────────────────────────────

class CategoryRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def get_by_id(self, category_id: int) -> dict[str, Any] | None:
        row = self.db.execute(
            "SELECT * FROM categories WHERE id = ?",
            (category_id,),
        ).fetchone()
        return dict_from_row(row)

    def get_by_name(self, name: str) -> dict[str, Any] | None:
        row = self.db.execute(
            "SELECT * FROM categories WHERE name = ?",
            (name,),
        ).fetchone()
        return dict_from_row(row)

    def get_all(self) -> list[dict[str, Any]]:
        rows = self.db.execute(
            "SELECT * FROM categories ORDER BY id",
        ).fetchall()
        return [dict_from_row(row) for row in rows if row is not None]

    def create(self, data: CategoryCreate) -> dict[str, Any]:
        cursor = self.db.execute(
            """
            INSERT INTO categories (name, description)
            VALUES (?, ?)
            """,
            (data.name, data.description),
        )
        self.db.commit()
        return self.get_by_id(cursor.lastrowid)

    def delete(self, category_id: int) -> None:
        self.db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        self.db.commit()


class PostRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def get_by_id(self, post_id: int) -> dict[str, Any] | None:
        row = self.db.execute(
            "SELECT * FROM posts WHERE id = ?",
            (post_id,),
        ).fetchone()
        return dict_from_row(row)

    def get_list(
        self,
        skip: int = 0,
        limit: int = 20,
        category_id: int | None = None,
        published_only: bool = False,
    ) -> list[dict[str, Any]]:
        where = []
        params: list[Any] = []

        if category_id is not None:
            where.append("category_id = ?")
            params.append(category_id)
        if published_only:
            where.append("published = 1")

        where_clause = f"WHERE {' AND '.join(where)}" if where else ""
        rows = self.db.execute(
            f"""
            SELECT * FROM posts
            {where_clause}
            ORDER BY created_at DESC, id DESC
            LIMIT ? OFFSET ?
            """,
            (*params, limit, skip),
        ).fetchall()
        return [dict_from_row(row) for row in rows if row is not None]

    def create(self, data: PostCreate) -> dict[str, Any]:
        created_at = now_iso()
        cursor = self.db.execute(
            """
            INSERT INTO posts (
                title, content, summary, published,
                category_id, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.title,
                data.content,
                None,
                0,
                data.category_id,
                created_at,
                created_at,
            ),
        )
        self.db.commit()
        return self.get_by_id(cursor.lastrowid)

    def update(self, post_id: int, data: PostUpdate) -> dict[str, Any]:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return self.get_by_id(post_id)

        update_data["updated_at"] = now_iso()
        columns = []
        params = []
        for field, value in update_data.items():
            columns.append(f"{field} = ?")
            params.append(int(value) if field == "published" and value is not None else value)

        params.append(post_id)
        self.db.execute(
            f"UPDATE posts SET {', '.join(columns)} WHERE id = ?",
            params,
        )
        self.db.commit()
        return self.get_by_id(post_id)

    def delete(self, post_id: int) -> None:
        self.db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        self.db.commit()


class CommentRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def get_by_post(self, post_id: int) -> list[dict[str, Any]]:
        rows = self.db.execute(
            """
            SELECT * FROM comments
            WHERE post_id = ?
            ORDER BY id
            """,
            (post_id,),
        ).fetchall()
        return [dict_from_row(row) for row in rows if row is not None]

    def create(self, post_id: int, data: CommentCreate) -> dict[str, Any]:
        cursor = self.db.execute(
            """
            INSERT INTO comments (content, author, post_id, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (data.content, data.author, post_id, now_iso()),
        )
        self.db.commit()
        row = self.db.execute(
            "SELECT * FROM comments WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        return dict_from_row(row)


# ── Service 계층 ──────────────────────────────────────────────────────────────

class CategoryService:
    def __init__(self, db: sqlite3.Connection):
        self.repo = CategoryRepository(db)

    def list_categories(self) -> list[dict[str, Any]]:
        return self.repo.get_all()

    def create_category(self, data: CategoryCreate) -> dict[str, Any]:
        if self.repo.get_by_name(data.name):
            raise HTTPException(status_code=409, detail="이미 존재하는 카테고리 이름입니다")
        return self.repo.create(data)

    def delete_category(self, category_id: int) -> None:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
        self.repo.delete(category_id)


class PostService:
    def __init__(self, db: sqlite3.Connection):
        self.repo = PostRepository(db)
        self.category_repo = CategoryRepository(db)
        self.comment_repo = CommentRepository(db)

    def _get_or_404(self, post_id: int) -> dict[str, Any]:
        post = self.repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
        return post

    def list_posts(
        self,
        skip: int = 0,
        limit: int = 20,
        category_id: int | None = None,
        published_only: bool = False,
    ) -> list[dict[str, Any]]:
        return self.repo.get_list(
            skip=skip,
            limit=limit,
            category_id=category_id,
            published_only=published_only,
        )

    def get_post(self, post_id: int) -> dict[str, Any]:
        return self._get_or_404(post_id)

    def create_post(self, data: PostCreate) -> dict[str, Any]:
        if data.category_id is not None and not self.category_repo.get_by_id(data.category_id):
            raise HTTPException(status_code=400, detail="존재하지 않는 카테고리입니다")
        return self.repo.create(data)

    def update_post(self, post_id: int, data: PostUpdate) -> dict[str, Any]:
        self._get_or_404(post_id)
        if data.category_id is not None and not self.category_repo.get_by_id(data.category_id):
            raise HTTPException(status_code=400, detail="존재하지 않는 카테고리입니다")
        return self.repo.update(post_id, data)

    def publish_post(self, post_id: int) -> dict[str, Any]:
        post = self._get_or_404(post_id)
        if post["published"]:
            raise HTTPException(status_code=400, detail="이미 공개된 게시글입니다")
        return self.repo.update(post_id, PostUpdate(published=True))

    def delete_post(self, post_id: int) -> None:
        self._get_or_404(post_id)
        self.repo.delete(post_id)

    def add_comment(self, post_id: int, data: CommentCreate) -> dict[str, Any]:
        self._get_or_404(post_id)
        return self.comment_repo.create(post_id, data)

    def list_comments(self, post_id: int) -> list[dict[str, Any]]:
        self._get_or_404(post_id)
        return self.comment_repo.get_by_post(post_id)


# ── 의존성 주입 팩토리 ──────────────────────────────────────────────────────────

def get_category_service(db: sqlite3.Connection = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


def get_post_service(db: sqlite3.Connection = Depends(get_db)) -> PostService:
    return PostService(db)


# ── 라우터 ────────────────────────────────────────────────────────────────────

@app.get("/categories", response_model=list[CategoryResponse], tags=["Categories"])
def list_categories(service: CategoryService = Depends(get_category_service)):
    return service.list_categories()


@app.post("/categories", response_model=CategoryResponse, status_code=201, tags=["Categories"])
def create_category(data: CategoryCreate, service: CategoryService = Depends(get_category_service)):
    return service.create_category(data)


@app.delete("/categories/{category_id}", status_code=204, tags=["Categories"])
def delete_category(category_id: int, service: CategoryService = Depends(get_category_service)):
    service.delete_category(category_id)


@app.get("/posts", response_model=list[PostResponse], tags=["Posts"])
def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: int | None = None,
    published_only: bool = False,
    service: PostService = Depends(get_post_service),
):
    return service.list_posts(
        skip=skip,
        limit=limit,
        category_id=category_id,
        published_only=published_only,
    )


@app.get("/posts/{post_id}", response_model=PostDetailResponse, tags=["Posts"])
def get_post(post_id: int, service: PostService = Depends(get_post_service)):
    post = service.get_post(post_id)
    category_id = post["category_id"]
    category = service.category_repo.get_by_id(category_id) if category_id else None
    comment_count = len(service.comment_repo.get_by_post(post_id))
    return {
        **post,
        "category": category,
        "comment_count": comment_count,
    }


@app.post("/posts", response_model=PostResponse, status_code=201, tags=["Posts"])
def create_post(data: PostCreate, service: PostService = Depends(get_post_service)):
    return service.create_post(data)


@app.patch("/posts/{post_id}", response_model=PostResponse, tags=["Posts"])
def update_post(post_id: int, data: PostUpdate, service: PostService = Depends(get_post_service)):
    return service.update_post(post_id, data)


@app.post("/posts/{post_id}/publish", response_model=PostResponse, tags=["Posts"])
def publish_post(post_id: int, service: PostService = Depends(get_post_service)):
    return service.publish_post(post_id)


@app.delete("/posts/{post_id}", status_code=204, tags=["Posts"])
def delete_post(post_id: int, service: PostService = Depends(get_post_service)):
    service.delete_post(post_id)


@app.get("/posts/{post_id}/comments", response_model=list[CommentResponse], tags=["Comments"])
def list_comments(post_id: int, service: PostService = Depends(get_post_service)):
    return service.list_comments(post_id)


@app.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=201, tags=["Comments"])
def add_comment(post_id: int, data: CommentCreate, service: PostService = Depends(get_post_service)):
    return service.add_comment(post_id, data)


# ── 초기 데이터 ───────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup() -> None:
    init_db()
    seed_data()


def seed_data() -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")

        category_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        if category_count > 0:
            return

        cat_svc = CategoryService(conn)
        post_svc = PostService(conn)

        tech = cat_svc.create_category(CategoryCreate(name="기술", description="개발 관련 글"))
        cat_svc.create_category(CategoryCreate(name="일상", description="일상 이야기"))

        p1 = post_svc.create_post(
            PostCreate(
                title="FastAPI 시작하기",
                content="FastAPI는 Python으로 REST API를 빠르게 만들 수 있는 프레임워크입니다.",
                category_id=tech["id"],
            )
        )
        post_svc.publish_post(p1["id"])

        post_svc.create_post(
            PostCreate(
                title="SQLite로 CRUD 만들기",
                content="SQLite를 사용하면 별도 DB 서버 없이도 실제 저장되는 CRUD를 연습할 수 있습니다.",
                category_id=tech["id"],
            )
        )
        post_svc.add_comment(
            p1["id"],
            CommentCreate(content="좋은 글 감사합니다!", author="독자1"),
        )
        post_svc.add_comment(
            p1["id"],
            CommentCreate(content="많은 도움이 됐어요.", author="독자2"),
        )
