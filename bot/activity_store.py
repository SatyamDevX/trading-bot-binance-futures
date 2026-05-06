import os
import sqlite3
from contextlib import contextmanager


DEFAULT_DB_PATH = os.path.join("data", "dashboard.db")


class ActivityStore:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.db_path = db_path
        self._ensure_parent_dir()
        self._init_db()

    def _ensure_parent_dir(self):
        parent = os.path.dirname(self.db_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _init_db(self):
        with self._connect() as connection:
            # A single table is enough for this demo and keeps persistence easy to explain.
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS order_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    details TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def append(self, title, payload, details=None):
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO order_activity (title, payload, details)
                VALUES (?, ?, ?)
                """,
                (title, payload, details),
            )

    def list_recent(self, limit=8):
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT title, payload, details, created_at
                FROM order_activity
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]


def create_activity_store(db_path=DEFAULT_DB_PATH):
    return ActivityStore(db_path)
