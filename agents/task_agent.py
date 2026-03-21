# agents/task_agent.py
from core.tasks import get_tasks, add_task, mark_done
from core.memory import log_event


def run(user_input: str) -> str:
    text = user_input.lower()

    # Show tasks
    if any(w in text for w in ["show", "list", "what are", "my tasks", "today"]):
        tasks = get_tasks()
        if not tasks:
            return "You have no pending tasks. Add one from the dashboard."
        lines = [f"{i+1}. {t[1]} — due {t[2]}" for i, t in enumerate(tasks)]
        return "Your current tasks:\n" + "\n".join(lines)

    # Add task
    if any(w in text for w in ["add", "create", "new task"]):
        words = user_input.replace("add task", "").replace("add", "").replace("create", "").strip()
        if words:
            add_task(words, "TBD")
            log_event("task_created", words)
            return f"Added task: '{words}'"
        return "What task do you want to add?"

    # Complete task
    if any(w in text for w in ["done", "complete", "finish", "mark"]):
        tasks = get_tasks()
        if not tasks:
            return "No pending tasks to complete."
        lines = [f"{i+1}. {t[1]}" for i, t in enumerate(tasks)]
        return "Which task is done?\n" + "\n".join(lines)

    # Default — show tasks
    tasks = get_tasks()
    if not tasks:
        return "No pending tasks."
    lines = [f"{i+1}. {t[1]} — due {t[2]}" for i, t in enumerate(tasks)]
    return "Your tasks:\n" + "\n".join(lines)