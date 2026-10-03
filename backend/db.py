"""SQLite persistence for print jobs."""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .models import Job

STATUSES = {"queued", "claimed", "printing", "printed", "failed"}
TRANSITIONS = {
    "queued": {"claimed", "failed"},
    "claimed": {"printing", "queued", "failed"},
    "printing": {"printed", "failed"},
    "printed": set(),
    "failed": set(),
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY, original_name TEXT NOT NULL, original_path TEXT NOT NULL,
    print_path TEXT NOT NULL, pages TEXT NOT NULL, colour TEXT NOT NULL,
    sides TEXT NOT NULL, flip TEXT NOT NULL, copies INTEGER NOT NULL,
    page_count INTEGER, status TEXT NOT NULL CHECK(status IN
      ('queued','claimed','printing','printed','failed')),
    created_at TEXT NOT NULL, claimed_at TEXT, updated_at TEXT NOT NULL,
    error TEXT
);
CREATE INDEX IF NOT EXISTS idx_jobs_queue ON jobs(status, created_at);
"""


def _connect(path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(str(path), timeout=30, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 30000")
    return connection


def init_db(path: str | Path) -> None:
    """Create the database schema if it does not exist."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with _connect(path) as connection:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.executescript(SCHEMA)


create_schema = init_db


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_job(db_path: str | Path, *, original_name: str, original_path: str,
               print_path: str, pages: str = "all", colour: str = "colour",
               sides: str = "single", flip: str = "long", copies: int = 1,
               page_count: int | None = None, job_id: str | None = None) -> str:
    """Insert a queued job and return its id."""
    if copies < 1:
        raise ValueError("copies must be positive")
    init_db(db_path)
    job_id = job_id or str(uuid.uuid4())
    now = _now()
    with _connect(db_path) as connection:
        connection.execute(
            """INSERT INTO jobs (id,original_name,original_path,print_path,pages,colour,
               sides,flip,copies,page_count,status,created_at,updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?, 'queued',?,?)""",
            (job_id, original_name, original_path, print_path, pages, colour,
             sides, flip, copies, page_count, now, now),
        )
    return job_id


def get_job(db_path: str | Path, job_id: str) -> Job | None:
    """Fetch a job, or None when it is unknown."""
    with _connect(db_path) as connection:
        row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return Job.from_row(row) if row else None


def claim_next_job(db_path: str | Path) -> Job | None:
    """Atomically claim the oldest queued job, safe across threads/processes."""
    with _connect(db_path) as connection:
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT id FROM jobs WHERE status='queued' ORDER BY created_at, id LIMIT 1"
            ).fetchone()
            if row is None:
                connection.execute("COMMIT")
                return None
            now = _now()
            connection.execute(
                "UPDATE jobs SET status='claimed', claimed_at=?, updated_at=? WHERE id=? AND status='queued'",
                (now, now, row["id"]),
            )
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
    return get_job(db_path, row["id"])


def update_status(db_path: str | Path, job_id: str, status: str, error: str | None = None) -> Job:
    """Apply a validated state transition and return the updated job."""
    if status not in STATUSES:
        raise ValueError(f"Unknown job status: {status!r}")
    with _connect(db_path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute("SELECT status FROM jobs WHERE id=?", (job_id,)).fetchone()
        if row is None:
            connection.execute("ROLLBACK")
            raise KeyError(f"Unknown job: {job_id}")
        current = row["status"]
        if status not in TRANSITIONS[current]:
            connection.execute("ROLLBACK")
            raise ValueError(f"Invalid job transition: {current} -> {status}")
        connection.execute(
            "UPDATE jobs SET status=?, error=?, updated_at=? WHERE id=?",
            (status, error, _now(), job_id),
        )
        connection.execute("COMMIT")
    return get_job(db_path, job_id)  # type: ignore[return-value]


def requeue_stale_claims(db_path: str | Path, max_age_seconds: int = 600) -> int:
    """Put claimed jobs older than the threshold back in the queue."""
    if max_age_seconds < 0:
        raise ValueError("max_age_seconds cannot be negative")
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=max_age_seconds)
    with _connect(db_path) as connection:
        cursor = connection.execute(
            """UPDATE jobs SET status='queued', claimed_at=NULL, updated_at=?
               WHERE status='claimed' AND claimed_at IS NOT NULL AND claimed_at < ?""",
            (_now(), cutoff.isoformat()),
        )
    return cursor.rowcount
