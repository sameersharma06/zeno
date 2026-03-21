# agents/coding_agent.py
from core.brain import get_response
from core.memory import log_event


def run(user_input: str) -> str:
    log_event("coding_query", user_input[:100])

    prompt = f"""Coding request: {user_input}

You are helping Sameer write or debug code for his SAMEER AI TWIN project.
Stack: Python, MLX, Streamlit, SQLite, LlamaIndex, ChromaDB, LangGraph.
Always give complete, runnable code.
If debugging — identify the root cause first, then fix it."""

    return get_response(prompt, voice_mode=False)