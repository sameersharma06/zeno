# core/proactive.py — Layer 5: Proactive Intelligence
import datetime
import sqlite3
from runtime.config.settings import DB_PATH


def get_morning_briefing() -> str:
    """
    Generates a morning briefing based on tasks and patterns.
    Call this when the app first opens in the morning.
    """
    now = datetime.datetime.now()
    hour = now.hour
    today = now.strftime("%A, %d %B")

    # Get pending tasks
    try:
        conn = sqlite3.connect(DB_PATH)
        tasks = conn.execute(
            "SELECT task, deadline FROM tasks WHERE done=0 ORDER BY id"
        ).fetchall()
        conn.close()
    except Exception:
        tasks = []

    if not tasks:
        task_text = "You have no pending tasks. Add something to work on today."
    else:
        task_lines = "\n".join([f"- {t[0]} (due {t[1]})" for t in tasks])
        task_text = f"You have {len(tasks)} tasks:\n{task_lines}"

    # Get overdue tasks
    overdue = []
    today_date = datetime.date.today()
    for task, deadline in tasks:
        try:
            # Try to parse deadline
            for fmt in ["%d %b", "%d %B", "%Y-%m-%d"]:
                try:
                    dl = datetime.datetime.strptime(
                        f"{deadline} {today_date.year}", f"{fmt} %Y"
                    ).date()
                    if dl < today_date:
                        overdue.append(task)
                    break
                except ValueError:
                    continue
        except Exception:
            pass

    overdue_text = ""
    if overdue:
        overdue_text = f"\n\nOVERDUE — act on these immediately:\n"
        overdue_text += "\n".join([f"- {t}" for t in overdue])

    # Get most productive hour from patterns
    try:
        conn = sqlite3.connect(DB_PATH)
        peak = conn.execute("""
            SELECT substr(timestamp, 12, 2) as hour, COUNT(*) as cnt
            FROM events WHERE type = 'query'
            GROUP BY hour ORDER BY cnt DESC LIMIT 1
        """).fetchone()
        conn.close()
        peak_text = f"\nYour most productive hour is {peak[0]}:00." if peak else ""
    except Exception:
        peak_text = ""

    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

    briefing = f"""{greeting} Sameer. Today is {today}.

{task_text}{overdue_text}{peak_text}

Focus on your highest priority task first."""

    return briefing


def get_nudge() -> str:
    """
    Returns a nudge message if Sameer has been inactive.
    Returns empty string if no nudge needed.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        now = datetime.datetime.now()

        # Get last event time
        last = conn.execute(
            "SELECT timestamp FROM events ORDER BY id DESC LIMIT 1"
        ).fetchone()
        conn.close()

        if not last:
            return ""

        last_time = datetime.datetime.fromisoformat(last[0])
        minutes_inactive = (now - last_time).total_seconds() / 60

        hour = now.hour

        # Only nudge during working hours
        if not (8 <= hour <= 22):
            return ""

        # Nudge if inactive for more than 45 minutes
        if minutes_inactive > 45:
            minutes = int(minutes_inactive)
            return f"You've been inactive for {minutes} minutes. What are you working on?"

        return ""

    except Exception:
        return ""


def get_deadline_warnings() -> list:
    """
    Returns list of tasks due today or tomorrow.
    """
    warnings = []
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)

    try:
        conn = sqlite3.connect(DB_PATH)
        tasks = conn.execute(
            "SELECT task, deadline FROM tasks WHERE done=0"
        ).fetchall()
        conn.close()

        for task, deadline in tasks:
            for fmt in ["%d %b", "%d %B"]:
                try:
                    dl = datetime.datetime.strptime(
                        f"{deadline} {today.year}", f"{fmt} %Y"
                    ).date()
                    if dl == today:
                        warnings.append(f"DUE TODAY: {task}")
                    elif dl == tomorrow:
                        warnings.append(f"Due tomorrow: {task}")
                    break
                except ValueError:
                    continue

    except Exception:
        pass

    return warnings


def should_show_morning_briefing() -> bool:
    """
    Returns True if morning briefing should be shown.
    Only shows once per day, between 6am and 11am.
    """
    now = datetime.datetime.now()
    hour = now.hour
    today = datetime.date.today().isoformat()

    if not (6 <= hour <= 11):
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        shown = conn.execute(
            "SELECT COUNT(*) FROM events WHERE type='morning_briefing' "
            "AND timestamp LIKE ?",
            (f"{today}%",)
        ).fetchone()[0]
        conn.close()
        return shown == 0
    except Exception:
        return False


def mark_briefing_shown():
    """Call after showing morning briefing so it doesn't repeat."""
    from core.memory import log_event
    log_event("morning_briefing", "shown")
    