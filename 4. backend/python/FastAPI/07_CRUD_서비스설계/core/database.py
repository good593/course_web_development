from datetime import UTC, datetime
from pathlib import Path
import sqlite3
from typing import Any, Iterator

DATABASE_PATH = Path("blog.db")


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
