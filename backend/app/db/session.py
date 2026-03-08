import asyncio
import sqlite3
import threading
from pathlib import Path
from typing import Any
from typing import Optional

from app.core.config import settings


class SqliteDatabase:
    def __init__(self, db_path: str) -> None:
        self._db_path = Path(db_path).expanduser().resolve()
        self._ready = False
        self._ready_lock = threading.Lock()

    async def init(self) -> None:
        await asyncio.to_thread(self._ensure_ready_sync)

    def _connect(self) -> sqlite3.Connection:
        self._ensure_ready_sync()
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _ensure_ready_sync(self) -> None:
        if self._ready:
            return
        with self._ready_lock:
            if self._ready:
                return
            self._init_sync()
            self._ready = True

    def _init_sync(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys=ON;")
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    thinking TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, created_at);

                CREATE TABLE IF NOT EXISTS supervisor_runs (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    objective TEXT NOT NULL,
                    plan_text TEXT NOT NULL,
                    primary_name TEXT NOT NULL,
                    worker_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_supervisor_runs_conversation
                    ON supervisor_runs(conversation_id, created_at DESC);

                CREATE TABLE IF NOT EXISTS supervisor_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    task_index INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    worker_output TEXT NOT NULL,
                    review_verdict TEXT NOT NULL,
                    review_feedback TEXT NOT NULL,
                    status TEXT NOT NULL,
                    retries INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(run_id, task_index),
                    FOREIGN KEY(run_id) REFERENCES supervisor_runs(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_supervisor_tasks_run ON supervisor_tasks(run_id, task_index);
                """
            )
            conn.execute(
                """
                UPDATE supervisor_runs
                SET status = 'failed',
                    summary = CASE
                        WHEN summary = '' THEN 'Run interrupted by service restart.'
                        ELSE summary
                    END
                WHERE status = 'running';
                """
            )
            conn.execute(
                """
                UPDATE supervisor_tasks
                SET status = 'failed',
                    review_feedback = CASE
                        WHEN review_feedback = '' THEN 'Interrupted by service restart.'
                        ELSE review_feedback
                    END
                WHERE status = 'running';
                """
            )
            conn.commit()

    async def fetchall(self, sql: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        return await asyncio.to_thread(self._fetchall_sync, sql, params)

    def _fetchall_sync(self, sql: str, params: tuple[Any, ...]) -> list[sqlite3.Row]:
        with self._connect() as conn:
            cur = conn.execute(sql, params)
            return cur.fetchall()

    async def fetchone(self, sql: str, params: tuple[Any, ...] = ()) -> Optional[sqlite3.Row]:
        return await asyncio.to_thread(self._fetchone_sync, sql, params)

    def _fetchone_sync(self, sql: str, params: tuple[Any, ...]) -> Optional[sqlite3.Row]:
        with self._connect() as conn:
            cur = conn.execute(sql, params)
            return cur.fetchone()

    async def execute(self, sql: str, params: tuple[Any, ...] = ()) -> None:
        await asyncio.to_thread(self._execute_sync, sql, params)

    def _execute_sync(self, sql: str, params: tuple[Any, ...]) -> None:
        with self._connect() as conn:
            conn.execute(sql, params)
            conn.commit()

    async def executemany(self, sql: str, params: list[tuple[Any, ...]]) -> None:
        await asyncio.to_thread(self._executemany_sync, sql, params)

    def _executemany_sync(self, sql: str, params: list[tuple[Any, ...]]) -> None:
        with self._connect() as conn:
            conn.executemany(sql, params)
            conn.commit()

    async def transaction(
        self,
        statements: list[tuple[str, tuple[Any, ...]]],
        many_statements: Optional[list[tuple[str, list[tuple[Any, ...]]]]] = None,
    ) -> None:
        await asyncio.to_thread(self._transaction_sync, statements, many_statements or [])

    def _transaction_sync(
        self,
        statements: list[tuple[str, tuple[Any, ...]]],
        many_statements: list[tuple[str, list[tuple[Any, ...]]]],
    ) -> None:
        with self._connect() as conn:
            for sql, params in statements:
                conn.execute(sql, params)
            for sql, rows in many_statements:
                if rows:
                    conn.executemany(sql, rows)
            conn.commit()


db = SqliteDatabase(settings.db_path)
