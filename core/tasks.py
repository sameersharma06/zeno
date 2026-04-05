# core/tasks.py
from core.database import db_pool  # CHANGED: Use database pool

def get_tasks():
    return db_pool.execute_query(
        "SELECT id, task, deadline FROM tasks WHERE done = 0 ORDER BY id"
    )

def add_task(task: str, deadline: str):
    db_pool.execute_query(
        "INSERT INTO tasks (task, deadline) VALUES (?, ?)", (task, deadline)
    )

def mark_done(task_id: int):
    db_pool.execute_query("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
