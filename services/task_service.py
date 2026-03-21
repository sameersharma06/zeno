# core/tasks.py
import sqlite3
from runtime.config.settings import DB_PATH, DATA_DIR
import os

def _connect():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            task     TEXT    NOT NULL,
            deadline TEXT    NOT NULL,
            done     BOOLEAN DEFAULT 0
        )
    """)
    conn.commit()
    return conn

def get_tasks():
    conn = _connect()
    rows = conn.execute(
        "SELECT id, task, deadline FROM tasks WHERE done = 0 ORDER BY id"
    ).fetchall()
    conn.close()
    return rows

def add_task(task: str, deadline: str):
    conn = _connect()
    conn.execute(
        "INSERT INTO tasks (task, deadline) VALUES (?, ?)", (task, deadline)
    )
    conn.commit()
    conn.close()

def mark_done(task_id: int):
    conn = _connect()
    conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    