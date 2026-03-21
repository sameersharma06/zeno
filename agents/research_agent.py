# agents/research_agent.py
from core.brain import get_response
from core.memory import log_event


def run(user_input: str) -> str:
    log_event("research_query", user_input[:100])

    # Check knowledge base first
    try:
        from knowledge.retriever import query as knowledge_query
        local_result = knowledge_query(user_input)
        if local_result and "empty" not in local_result.lower():
            return f"From your notes:\n\n{local_result}"
    except Exception:
        pass

    # Nothing in notes — answer from training data honestly
    prompt = f"""Research request: {user_input}

IMPORTANT: Only answer what you actually know.
If this topic is not in Sameer's notes, say clearly:
"I don't have notes on this yet. Here's what I know from general knowledge:"
Then give a honest, accurate answer.
Never pretend Sameer has knowledge he doesn't have.
Never say "based on your notes" if there are no notes on this topic."""

    return get_response(prompt, voice_mode=False)