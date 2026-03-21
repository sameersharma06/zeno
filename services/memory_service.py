# core/memory.py — Layer 2: Memory + Context Engine
import sqlite3
import datetime
import os
from runtime.config.settings import DB_PATH, DATA_DIR


def _connect():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            type      TEXT NOT NULL,
            content   TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_logs (
            date       TEXT PRIMARY KEY,
            summary    TEXT,
            work_hours REAL DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patterns (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern     TEXT NOT NULL,
            detected_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def log_event(event_type: str, content: str):
    conn = _connect()
    conn.execute(
        "INSERT INTO events (timestamp, type, content) VALUES (?,?,?)",
        (datetime.datetime.now().isoformat(), event_type, content[:300])
    )
    conn.commit()
    conn.close()

def get_recent_events(limit: int = 20) -> list:
    conn = _connect()
    rows = conn.execute(
        "SELECT timestamp, type, content FROM events "
        "ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return rows

def get_todays_events() -> list:
    conn = _connect()
    today = datetime.date.today().isoformat()
    rows = conn.execute(
        "SELECT timestamp, type, content FROM events "
        "WHERE timestamp LIKE ? ORDER BY id ASC",
        (f"{today}%",)
    ).fetchall()
    conn.close()
    return rows


def get_context_summary() -> str:
    now = datetime.datetime.now()
    hour = now.hour

    if hour < 12:
        time_context = "morning"
    elif hour < 17:
        time_context = "afternoon"
    elif hour < 21:
        time_context = "evening"
    else:
        time_context = "night"

    events = get_recent_events(10)
    if not events:
        activity_str = "No recent activity logged yet."
    else:
        lines = []
        for ts, etype, content in reversed(events):
            time_str = ts[11:16]
            lines.append(f"[{time_str}] {etype}: {content}")
        activity_str = "\n".join(lines)

    todays = get_todays_events()
    queries_today = sum(1 for _, t, _ in todays if t == "query")
    tasks_created = sum(1 for _, t, _ in todays if t == "task_created")
    tasks_done    = sum(1 for _, t, _ in todays if t == "task_completed")
    voice_used    = sum(1 for _, t, _ in todays if t == "voice_used")

    return f"""Time: {now.strftime('%A, %d %B %Y — %H:%M')} ({time_context})

Today's activity:
- Queries asked: {queries_today}
- Tasks created: {tasks_created}
- Tasks completed: {tasks_done}
- Voice conversations: {voice_used}

Recent events (last 10):
{activity_str}"""


def detect_patterns() -> list:
    conn = _connect()
    patterns_found = []

    old_tasks = conn.execute("""
        SELECT content, timestamp FROM events
        WHERE type = 'task_created'
        AND timestamp < datetime('now', '-3 days')
    """).fetchall()

    completed = conn.execute(
        "SELECT content FROM events WHERE type = 'task_completed'"
    ).fetchall()
    completed_contents = [r[0] for r in completed]

    for content, ts in old_tasks:
        if content not in completed_contents:
            patterns_found.append(
                f"Delayed task: '{content}' created {ts[:10]} still pending"
            )

    peak = conn.execute("""
        SELECT substr(timestamp, 12, 2) as hour, COUNT(*) as cnt
        FROM events WHERE type = 'query'
        GROUP BY hour ORDER BY cnt DESC LIMIT 1
    """).fetchone()
    if peak:
        patterns_found.append(
            f"Most active hour: {peak[0]}:00 ({peak[1]} queries)"
        )

    voice_count = conn.execute(
        "SELECT COUNT(*) FROM events WHERE type = 'voice_used'"
    ).fetchone()[0]
    text_count = conn.execute(
        "SELECT COUNT(*) FROM events WHERE type = 'query'"
    ).fetchone()[0]
    if voice_count + text_count > 5:
        pref = "voice" if voice_count > text_count else "text"
        patterns_found.append(
            f"Prefers {pref} ({voice_count} voice, {text_count} text queries)"
        )

    conn.close()
    return patterns_found


def save_log(summary: str, work_hours: float = 0):
    conn = _connect()
    today = datetime.date.today().isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO daily_logs (date, summary, work_hours) VALUES (?,?,?)",
        (today, summary, work_hours)
    )
    conn.commit()
    conn.close()

def get_recent_logs(days: int = 7) -> list:
    conn = _connect()
    rows = conn.execute(
        "SELECT date, summary, work_hours FROM daily_logs "
        "ORDER BY date DESC LIMIT ?", (days,)
    ).fetchall()
    conn.close()
    return rows

def generate_daily_summary() -> str:
    todays = get_todays_events()
    if not todays:
        return "No activity recorded today."

    created = [c for _, t, c in todays if t == "task_created"]
    done    = [c for _, t, c in todays if t == "task_completed"]
    queries = [c for _, t, c in todays if t == "query"]

    lines = [f"Date: {datetime.date.today().isoformat()}"]
    lines.append(f"Total interactions: {len(todays)}")
    if created:
        lines.append(f"Tasks created: {', '.join(created)}")
    if done:
        lines.append(f"Tasks completed: {', '.join(done)}")
    if queries:
        lines.append(f"Main topics: {', '.join(queries[:3])}")

    summary = "\n".join(lines)
    save_log(summary)
    return summary
