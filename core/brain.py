# core/brain.py — OPTIMIZED ZENO ENGINE (WITH MEMORY)

from mlx_lm import load, generate
import threading
import gc

# ─────────────────────────────────────────
# MODEL CACHE + LOCK
# ─────────────────────────────────────────

_model_cache = {
    "text": None,
    "voice": None
}

_model_lock = threading.Lock()


def _load_model():
    with _model_lock:
        if _model_cache["text"] is None:
            print("⚡ Loading 7B model (first time)...")
            model, tokenizer = load("mlx-community/Qwen2.5-7B-Instruct-4bit")
            _model_cache["text"] = (model, tokenizer)
    return _model_cache["text"]


def _load_fast_model():
    with _model_lock:
        if _model_cache["voice"] is None:
            print("⚡ Loading 3B model (voice)...")

            # optional memory cleanup
            if _model_cache["text"] is not None:
                _model_cache["text"] = None
                gc.collect()

            model, tokenizer = load("mlx-community/Qwen2.5-3B-Instruct-4bit")
            _model_cache["voice"] = (model, tokenizer)

    return _model_cache["voice"]


# ─────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────

FULL_SYSTEM_PROMPT = """You are SAMEER AI — Sameer's personal AI operator and second brain.

RULES:
- Be concise
- Max 5 bullet points
- No fluff
- Focus on execution and debugging
- Avoid repeating previous responses

Today's tasks:
{tasks}

Recent activity:
{recent_activity}
"""


VOICE_SYSTEM_PROMPT = """You are SAMEER AI — short voice assistant.

Rules:
- Max 2 sentences
- Natural tone
- End with one action

Tasks:
{tasks}

Recent:
{recent_activity}
"""


# ─────────────────────────────────────────
# MAIN RESPONSE ENGINE
# ─────────────────────────────────────────

def get_response(
    user_message: str,
    tasks_context: str = "",
    voice_mode: bool = False,
    history=None
) -> str:

    from core.memory import log_event, get_context_summary
    from core.state import get_full_state

    try:
        # ── SAFE DEFAULT ──
        if history is None:
            history = []

        # ── MODEL SELECT ──
        if voice_mode:
            model, tokenizer = _load_fast_model()
        else:
            model, tokenizer = _load_model()

        # ── CONTEXT ──
        recent_activity = get_context_summary()

        prompt_template = VOICE_SYSTEM_PROMPT if voice_mode else FULL_SYSTEM_PROMPT

        system_content = prompt_template.format(
            tasks=tasks_context if tasks_context else "No tasks",
            recent_activity=recent_activity[-300:]
        )

        # ── STATE (LIMIT SIZE) ──
        try:
            state = get_full_state()
            if len(state) > 800:
                state = state[:800]
            system_content += "\n\n" + state
        except:
            pass

        # ── PERSONALITY ──
        try:
            from core.personality import get_personality_prompt
            system_content += get_personality_prompt(user_message)
        except:
            pass

        # ── SMART RAG (OPTIONAL) ──
        if any(x in user_message.lower() for x in ["what", "how", "explain", "why"]):
            try:
                from knowledge.retriever import query as knowledge_query
                kc = knowledge_query(user_message)
                if kc and "empty" not in kc.lower():
                    system_content += f"\n\nKNOWLEDGE:\n{kc[:500]}"
            except:
                pass

        # ── LOG QUERY ──
        try:
            log_event("query", user_message[:200])
        except:
            pass

        # ─────────────────────────────
        # 🧠 BUILD MESSAGE STACK (MEMORY FIX)
        # ─────────────────────────────

        messages = [{"role": "system", "content": system_content}]

        # add history safely (limit to last 10)
        for msg in history[-10:]:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # add current message
        messages.append({"role": "user", "content": user_message})

        # ── TOKENIZE ──
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        max_tokens = 80 if voice_mode else 400

        # ── GENERATE ──
        response = generate(
            model,
            tokenizer,
            prompt,
            max_tokens=max_tokens
        )

        result = response.strip()

        # ── LOG RESPONSE ──
        try:
            log_event("response", result[:200])
        except:
            pass

        return result

    except Exception as e:
        return f"⚠️ Brain error: {str(e)}"

        