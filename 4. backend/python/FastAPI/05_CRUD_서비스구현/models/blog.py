from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import schemas

DB_PATH = Path(__file__).resolve().parents[1] / "blog.db"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    if "published" in data:
        data["published"] = bool(data["published"])
    return data


def init_db() -> None:
    with closing(_connect()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TEXT NOT NULL
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
            """
        )
        conn.commit()


class BlogDB:
    def list_categories(self) -> list[dict[str, Any]]:
        with closing(_connect()) as conn:
            rows = conn.execute(
                """
                SELECT c.id, c.name, c.description, c.created_at,
                       COUNT(p.id) AS post_count
                FROM categories AS c
                LEFT JOIN posts AS p ON p.category_id = c.id
                GROUP BY c.id
                ORDER BY c.id ASC
                """
            ).fetchall()
            return [dict(row) for row in rows]

    def get_category(self, category_id: int) -> dict[str, Any] | None:
        with closing(_connect()) as conn:
            row = conn.execute(
                "SELECT * FROM categories WHERE id = ?",
                (category_id,),
            ).fetchone()
            return _row_to_dict(row)

    def get_category_by_name(self, name: str) -> dict[str, Any] | None:
        with closing(_connect()) as conn:
            row = conn.execute(
                "SELECT * FROM categories WHERE name = ?",
                (name,),
            ).fetchone()
            return _row_to_dict(row)

    def create_category(self, data: schemas.CategoryCreate) -> dict[str, Any]:
        now = _now()
        with closing(_connect()) as conn:
            cursor = conn.execute(
                """
                INSERT INTO categories (name, description, created_at)
                VALUES (?, ?, ?)
                """,
                (data.name, data.description, now),
            )
            conn.commit()
            return self.get_category(cursor.lastrowid)  # type: ignore[arg-type]

    def update_category(
        self,
        category_id: int,
        data: schemas.CategoryUpdate,
    ) -> dict[str, Any] | None:
        payload = data.model_dump(exclude_unset=True)
        if not payload:
            return self.get_category(category_id)

        fields: list[str] = []
        values: list[Any] = []
        for field in ("name", "description"):
            if field in payload:
                fields.append(f"{field} = ?")
                values.append(payload[field])
        values.append(category_id)

        with closing(_connect()) as conn:
            conn.execute(
                f"UPDATE categories SET {', '.join(fields)} WHERE id = ?",
                values,
            )
            conn.commit()
            return self.get_category(category_id)

    def delete_category(self, category_id: int) -> bool:
        with closing(_connect()) as conn:
            cursor = conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            conn.commit()
            return cursor.rowcount > 0

    def _post_filters(
        self,
        category_id: int | None,
        published_only: bool,
        search: str | None,
    ) -> tuple[str, list[Any]]:
        clauses: list[str] = []
        params: list[Any] = []

        if category_id is not None:
            clauses.append("category_id = ?")
            params.append(category_id)

        if published_only:
            clauses.append("published = 1")

        if search:
            keyword = f"%{search}%"
            clauses.append("(title LIKE ? OR content LIKE ?)")
            params.extend([keyword, keyword])

        where_sql = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        return where_sql, params

    def list_posts(
        self,
        skip: int = 0,
        limit: int = 10,
        category_id: int | None = None,
        published_only: bool = False,
        search: str | None = None,
    ) -> dict[str, Any]:
        where_sql, params = self._post_filters(category_id, published_only, search)

        with closing(_connect()) as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM posts{where_sql}",
                params,
            ).fetchone()[0]
            rows = conn.execute(
                f"""
                SELECT *
                FROM posts
                {where_sql}
                ORDER BY id DESC
                LIMIT ? OFFSET ?
                """,
                [*params, limit, skip],
            ).fetchall()

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": [_row_to_dict(row) for row in rows],
        }

    def get_post(self, post_id: int) -> dict[str, Any] | None:
        with closing(_connect()) as conn:
            row = conn.execute(
                "SELECT * FROM posts WHERE id = ?",
                (post_id,),
            ).fetchone()
            return _row_to_dict(row)

    def create_post(self, data: schemas.PostCreate) -> dict[str, Any]:
        now = _now()
        payload = data.model_dump()

        with closing(_connect()) as conn:
            cursor = conn.execute(
                """
                INSERT INTO posts (
                    title, content, summary, published,
                    category_id, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["title"],
                    payload["content"],
                    payload["summary"],
                    int(payload["published"]),
                    payload["category_id"],
                    now,
                    now,
                ),
            )
            conn.commit()
            return self.get_post(cursor.lastrowid)  # type: ignore[arg-type]

    def update_post(
        self,
        post_id: int,
        data: schemas.PostUpdate,
    ) -> dict[str, Any] | None:
        payload = data.model_dump(exclude_unset=True)
        if not payload:
            return self.get_post(post_id)

        fields: list[str] = []
        values: list[Any] = []
        for field in ("title", "content", "summary", "published", "category_id"):
            if field in payload:
                fields.append(f"{field} = ?")
                value = payload[field]
                values.append(int(value) if field == "published" else value)

        fields.append("updated_at = ?")
        values.append(_now())
        values.append(post_id)

        with closing(_connect()) as conn:
            conn.execute(
                f"UPDATE posts SET {', '.join(fields)} WHERE id = ?",
                values,
            )
            conn.commit()
            return self.get_post(post_id)

    def delete_post(self, post_id: int) -> bool:
        with closing(_connect()) as conn:
            cursor = conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
            conn.commit()
            return cursor.rowcount > 0


blog_db = BlogDB()

