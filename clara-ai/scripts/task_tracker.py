"""
task_tracker.py – Local SQLite task tracker (zero-cost Asana mock).
Logs pipeline events for audit and workflow tracking.
"""

import sqlite3
import datetime
import json
import os
from config import TASK_TRACKER_DB


def _get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(TASK_TRACKER_DB), exist_ok=True)
    conn = sqlite3.connect(TASK_TRACKER_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id  TEXT    NOT NULL,
            task_type   TEXT    NOT NULL,
            version     TEXT,
            status      TEXT    DEFAULT 'completed',
            details     TEXT,
            created_at  TEXT    NOT NULL
        )
    """)
    conn.commit()
    return conn


def log_task(account_id: str, task_type: str, version: str = "", details: dict = None) -> int:
    """
    Insert a task record and return its ID.

    task_type examples: 'pipeline_a', 'pipeline_b', 'spec_generated', 'memo_extracted'
    """
    conn = _get_conn()
    now  = datetime.datetime.utcnow().isoformat()
    cur  = conn.execute(
        "INSERT INTO tasks (account_id, task_type, version, status, details, created_at) VALUES (?,?,?,?,?,?)",
        (account_id, task_type, version, "completed", json.dumps(details or {}), now)
    )
    conn.commit()
    task_id = cur.lastrowid
    conn.close()
    return task_id


def get_tasks(account_id: str = None) -> list:
    """Return all tasks, optionally filtered by account_id."""
    conn = _get_conn()
    if account_id:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE account_id=? ORDER BY created_at DESC", (account_id,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    conn.close()
    cols = ["id", "account_id", "task_type", "version", "status", "details", "created_at"]
    return [dict(zip(cols, r)) for r in rows]


def export_tasks_json(path: str) -> None:
    """Export all tasks to a JSON file (backward-compat with original task_tracker.json)."""
    tasks = get_tasks()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


if __name__ == "__main__":
    tasks = get_tasks()
    print(json.dumps(tasks, indent=2))
