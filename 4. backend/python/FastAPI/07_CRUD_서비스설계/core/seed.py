import sqlite3

import schemas
from core.database import DATABASE_PATH
from services import CategoryService, PostService


def seed_data() -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")

        category_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        if category_count > 0:
            return

        cat_svc = CategoryService(conn)
        post_svc = PostService(conn)

        tech = cat_svc.create_category(
            schemas.CategoryCreate(name="기술", description="개발 관련 글")
        )
        cat_svc.create_category(
            schemas.CategoryCreate(name="일상", description="일상 이야기")
        )

        p1 = post_svc.create_post(
            schemas.PostCreate(
                title="FastAPI 시작하기",
                content="FastAPI는 Python으로 REST API를 빠르게 만들 수 있는 프레임워크입니다.",
                category_id=tech["id"],
            )
        )
        post_svc.publish_post(p1["id"])

        post_svc.create_post(
            schemas.PostCreate(
                title="SQLite로 CRUD 만들기",
                content="SQLite를 사용하면 별도 DB 서버 없이도 실제 저장되는 CRUD를 연습할 수 있습니다.",
                category_id=tech["id"],
            )
        )
        post_svc.add_comment(
            p1["id"],
            schemas.CommentCreate(content="좋은 글 감사합니다!", author="독자1"),
        )
        post_svc.add_comment(
            p1["id"],
            schemas.CommentCreate(content="많은 도움이 됐어요.", author="독자2"),
        )
