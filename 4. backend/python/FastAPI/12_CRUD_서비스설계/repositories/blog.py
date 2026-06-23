import sqlite3
from typing import Any

import schemas
from core.database import dict_from_row, now_iso


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

    def create(self, data: schemas.CategoryCreate) -> dict[str, Any]:
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

    def create(self, data: schemas.PostCreate) -> dict[str, Any]:
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

    def update(self, post_id: int, data: schemas.PostUpdate) -> dict[str, Any]:
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

    def create(self, post_id: int, data: schemas.CommentCreate) -> dict[str, Any]:
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
