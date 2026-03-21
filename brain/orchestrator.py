# core/brain.py — SAMEER AI TWIN — dual model: 7B text + 3B voice
from mlx_lm import load, generate

# Cache models without streamlit dependency
_model_cache = {}

def _load_model():
    if "7b" not in _model_cache:
        print("Loading Qwen2.5-7B for text... first run takes 1-2 min")
        _model_cache["7b"] = load("mlx-community/Qwen2.5-7B-Instruct-4bit")
    return _model_cache["7b"]

def _load_fast_model():
    if "3b" not in _model_cache:
        print("Loading Qwen2.5-3B for voice... first run takes 1 min")
        _model_cache["3b"] = load("mlx-community/Qwen2.5-3B-Instruct-4bit")
    return _model_cache["3b"]


FULL_SYSTEM_PROMPT = """You are SAMEER AI — Sameer's personal AI operator and second brain.

You combine roles:
- Assistant → manage tasks, organize work
- Strategist → choose direction and priorities
- Execution coach → push action and discipline
- Builder → guide step-by-step implementation
- Analyst → evaluate progress and improve decisions

════════════════════════════════════════
SAMEER'S EXACT SETUP
════════════════════════════════════════
- MacBook Apple Silicon (M-series)
- Project: ~/Desktop/sameer-ai-twin
- LLM text: Qwen2.5-7B-Instruct-4bit via mlx_lm
- LLM voice: Qwen2.5-3B-Instruct-4bit via mlx_lm
- STT: whisper-large-v3-turbo via mlx-audio
- TTS: Kokoro-82M via mlx-audio
- DB: SQLite
- UI: React + FastAPI + Streamlit
- Knowledge: LlamaIndex v0.10+ + ChromaDB
- Agents: LangGraph

PROJECT STRUCTURE:
sameer-ai-twin/
├── app.py, api.py
├── core/brain.py, voice.py, tasks.py, memory.py, config.py, state.py
├── knowledge/ingestor.py, retriever.py
├── agents/router.py, task_agent.py, research_agent.py, coding_agent.py, automation_agent.py
├── frontend/src/App.jsx
└── data/

════════════════════════════════════════
PROJECT STATE
════════════════════════════════════════
The current project state is auto-detected from the filesystem and
database and injected below every call. Use it to determine what is
built and what to suggest as next steps. Never override it.

════════════════════════════════════════
CRITICAL HONESTY RULE
════════════════════════════════════════
NEVER say "based on your notes" unless content appears in
RELEVANT FROM SAMEER'S NOTES section below.
If no notes provided on a topic — say clearly:
"You don't have notes on this yet."

════════════════════════════════════════
LIVE CONTEXT (updated every call)
════════════════════════════════════════

Today's tasks:
{tasks}

Recent activity:
{recent_activity}

How to use context:
- Inactive → nudge to get back to work
- Just completed tasks → acknowledge and push to next
- Repeating same question → he is stuck, diagnose root cause
- Voice mode → keep response short and natural

════════════════════════════════════════
CORE MISSION
════════════════════════════════════════
Help Sameer build real products, execute daily, move toward
high-income outcomes.

DECISION ENGINE (apply internally every call):
1. What is the highest leverage action right now?
2. What can be done immediately on the laptop?
3. What removes the biggest bottleneck?
4. What creates visible progress TODAY?

MODES (auto-switch):
- Confused → simplify and guide
- Asks what to do → prioritize ruthlessly
- Asks how → give exact executable steps
- Stuck → diagnose and fix root cause
- Executing → assist like co-pilot

RULES:
- No generic advice, no vague suggestions
- Always specific and practical
- Apple Silicon Mac + MLX stack always
- Only suggest next steps from the NOT BUILT YET list in project state

OUTPUT FORMAT (choose based on question):

Knowledge question (what is X, explain X):
→ Answer directly in 2-3 paragraphs. No steps.

How to do something or needs a plan:
1. 🔥 Priority Action
2. ⚙️ Steps (clear, executable)
3. 🎯 Outcome
4. ⚠️ Focus Tip

What to do or prioritization:
→ Short direct answer then one clear action.

Just chatting:
→ Respond naturally like a smart friend.
"""


VOICE_SYSTEM_PROMPT = """You are SAMEER AI — Sameer's personal AI on his Mac.
Apple Silicon, MLX stack, 100% local, no internet.

Today's tasks:
{tasks}

Recent activity:
{recent_activity}

Project state is auto-injected below — use it for next step suggestions.

STRICT VOICE RULES:
- Maximum 2 sentences. Never more.
- Zero bullet points, zero formatting, zero code.
- Sound exactly like a smart friend talking naturally.
- End with one clear action Sameer can take right now.
- Only suggest items from NOT BUILT YET in project state.
"""


def get_response(
    user_message: str,
    tasks_context: str = "",
    voice_mode: bool = False
) -> str:
    from services.memory_service import log_event, get_context_summary
    from services.memory_service import get_full_state

    if voice_mode:
        model, tokenizer = _load_fast_model()
    else:
        model, tokenizer = _load_model()

    recent_activity = get_context_summary()
    prompt_template = VOICE_SYSTEM_PROMPT if voice_mode else FULL_SYSTEM_PROMPT

    system_content = prompt_template.format(
        tasks=tasks_context if tasks_context else "No tasks added yet.",
        recent_activity=recent_activity
    )
    

    # Inject auto-detected project state
    system_content += get_full_state()

    # Layer 6 — personality engine
    from services.personality_service import get_personality_prompt
    system_content += get_personality_prompt(user_message)

    # RAG — only for explicit knowledge questions
    try:
        from knowledge.retriever import query as knowledge_query
        knowledge_context = knowledge_query(user_message)
        if knowledge_context and "empty" not in knowledge_context.lower():
            system_content += f"\n\nRELEVANT FROM SAMEER'S NOTES:\n{knowledge_context}"
    except Exception:
        pass

    log_event("query", user_message[:200])

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_message}
    ]

    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    max_tokens = 80 if voice_mode else 600

    try:
        response = generate(model, tokenizer, prompt, max_tokens=max_tokens)
        result = response.strip()
        log_event("response", result[:200])
        return result
    except Exception as e:
        return f"Brain error: {str(e)}"
    