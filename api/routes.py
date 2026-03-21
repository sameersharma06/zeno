# api.py — SAMEER AI TWIN — FastAPI Backend
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from runtime.config.settings import AUDIO_IN, AUDIO_OUT
import json
import threading
import queue

app = FastAPI(title="SAMEER AI TWIN API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    voice_mode: bool = False

class TaskRequest(BaseModel):
    task: str
    deadline: str

class TaskCompleteRequest(BaseModel):
    task_id: int

# ── CHAT ─────────────────────────────────────────────────────────────────

@app.post("/api/chat")
async def chat(req: ChatRequest):
    from agents.router import run_agents
    from services.task_service import get_tasks

    tasks_text = "\n".join([f"- {t[1]} (due {t[2]})" for t in get_tasks()])

    task_triggers = [
        "my tasks", "all tasks", "what tasks", "list tasks",
        "show tasks", "pending tasks", "what are my", "tell me my tasks"
    ]
    if any(trigger in req.message.lower() for trigger in task_triggers):
        all_tasks = get_tasks()
        reply = f"You have {len(all_tasks)} tasks: {', '.join([t[1] for t in all_tasks])}." if all_tasks else "No pending tasks."
        return {"reply": reply, "agent": "TaskAgent"}

    reply, agent = run_agents(req.message, tasks_text)
    return {"reply": reply, "agent": agent}

# ── STREAMING CHAT ────────────────────────────────────────────────────────

@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    from services.task_service import get_tasks
    from services.memory_service import log_event, get_context_summary
    from brain.orchestrator import _load_model, FULL_SYSTEM_PROMPT
    from core.state import get_full_state
    from agents.router import run_agents
    from mlx_lm import stream_generate
    import asyncio

    tasks_text = "\n".join([f"- {t[1]} (due {t[2]})" for t in get_tasks()])

    # Task questions — direct from DB
    task_triggers = [
        "my tasks", "all tasks", "what tasks", "list tasks",
        "show tasks", "pending tasks", "what are my", "tell me my tasks"
    ]
    if any(trigger in req.message.lower() for trigger in task_triggers):
        all_tasks = get_tasks()
        reply = f"You have {len(all_tasks)} tasks: {', '.join([t[1] for t in all_tasks])}." if all_tasks else "No pending tasks."
        async def quick():
            yield f"data: {json.dumps({'token': reply, 'agent': 'TaskAgent', 'done': False})}\n\n"
            yield f"data: {json.dumps({'token': '', 'agent': 'TaskAgent', 'done': True})}\n\n"
        return StreamingResponse(quick(), media_type="text/event-stream")

    # Detect intent
    text = req.message.lower()
    if any(w in text for w in ["open", "launch", "start app"]):
        agent = "AutomationAgent"
    elif any(w in text for w in ["write a function", "debug this", "fix this error", "write a script"]):
        agent = "CodingAgent"
    elif any(w in text for w in ["what should i", "what to do", "i have time", "next step",
                                   "i am stuck", "guide me", "prioritize", "help me decide"]):
        agent = "Brain"
    elif any(w in text for w in ["what is", "explain", "research", "how do i", "what do my notes"]):
        agent = "ResearchAgent"
    else:
        agent = "Brain"

    # Automation — no streaming needed
    if agent == "AutomationAgent":
        reply, agent = run_agents(req.message, tasks_text)
        async def auto_stream():
            yield f"data: {json.dumps({'token': reply, 'agent': agent, 'done': False})}\n\n"
            yield f"data: {json.dumps({'token': '', 'agent': agent, 'done': True})}\n\n"
        return StreamingResponse(auto_stream(), media_type="text/event-stream")

    # Build prompt with auto-detected state
    model, tokenizer = _load_model()
    recent_activity = get_context_summary()

    system_content = FULL_SYSTEM_PROMPT.format(
        tasks=tasks_text,
        recent_activity=recent_activity
    )

    # Inject project state — this is the key fix
    system_content += get_full_state()

    # RAG — only for explicit knowledge questions
    try:
        from knowledge.retriever import query as kq
        kc = kq(req.message)
        if kc and "empty" not in kc.lower():
            system_content += f"\n\nRELEVANT FROM SAMEER'S NOTES:\n{kc}"
    except Exception:
        pass

    log_event("query", req.message[:200])

    messages_list = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": req.message}
    ]

    prompt = tokenizer.apply_chat_template(
        messages_list, tokenize=False, add_generation_prompt=True
    )

    final_agent = agent
    token_q = queue.Queue()

    def run_generation():
        try:
            for token_data in stream_generate(model, tokenizer, prompt, max_tokens=500):
                token = token_data.text if hasattr(token_data, "text") else str(token_data)
                token_q.put(token)
        except Exception as e:
            token_q.put(f"[ERROR]{str(e)}")
        finally:
            token_q.put(None)

    threading.Thread(target=run_generation, daemon=True).start()

    async def token_stream():
        full_response = ""
        loop = asyncio.get_event_loop()
        while True:
            token = await loop.run_in_executor(None, token_q.get)
            if token is None:
                log_event("response", full_response[:200])
                yield f"data: {json.dumps({'token': '', 'agent': final_agent, 'done': True})}\n\n"
                break
            if token.startswith("[ERROR]"):
                yield f"data: {json.dumps({'token': token[7:], 'agent': 'Error', 'done': True})}\n\n"
                break
            full_response += token
            yield f"data: {json.dumps({'token': token, 'agent': final_agent, 'done': False})}\n\n"

    return StreamingResponse(token_stream(), media_type="text/event-stream")

# ── VOICE ─────────────────────────────────────────────────────────────────

@app.post("/api/voice/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    from services.voice_service import transcribe
    from services.memory_service import log_event
    with open(AUDIO_IN, "wb") as f:
        f.write(await file.read())
    text = transcribe(AUDIO_IN)
    log_event("voice_used", text[:100])
    return {"text": text}

@app.post("/api/voice/speak")
async def speak_text(req: ChatRequest):
    from services.voice_service import speak
    from services.task_service import get_tasks
    from brain.orchestrator import get_response
    tasks_text = "\n".join([f"- {t[1]} (due {t[2]})" for t in get_tasks()])
    reply = get_response(req.message, tasks_text, voice_mode=True)
    audio_path = speak(reply)
    return FileResponse(audio_path, media_type="audio/wav")

# ── TASKS ─────────────────────────────────────────────────────────────────

@app.get("/api/tasks")
async def get_all_tasks():
    from services.task_service import get_tasks
    tasks = get_tasks()
    return {"tasks": [{"id": t[0], "task": t[1], "deadline": t[2]} for t in tasks]}

@app.post("/api/tasks/add")
async def add_new_task(req: TaskRequest):
    from services.task_service import add_task
    from services.memory_service import log_event
    add_task(req.task, req.deadline)
    log_event("task_created", req.task)
    return {"status": "added", "task": req.task}

@app.post("/api/tasks/complete")
async def complete_task(req: TaskCompleteRequest):
    from services.task_service import mark_done
    from services.memory_service import log_event
    mark_done(req.task_id)
    log_event("task_completed", f"task id {req.task_id}")
    return {"status": "completed", "task_id": req.task_id}

# ── MEMORY ────────────────────────────────────────────────────────────────

@app.get("/api/memory/patterns")
async def get_patterns():
    from services.memory_service import detect_patterns
    return {"patterns": detect_patterns()}

@app.get("/api/memory/summary")
async def get_summary():
    from services.memory_service import generate_daily_summary
    return {"summary": generate_daily_summary()}

@app.get("/api/memory/insight")
async def get_insight():
    from brain.orchestrator import get_response
    from services.task_service import get_tasks
    tasks_text = "\n".join([f"- {t[1]} (due {t[2]})" for t in get_tasks()])
    insight = get_response(
        "Give me one short powerful tip based on my tasks and recent activity.",
        tasks_text
    )
    return {"insight": insight}

# ── HEALTH ────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "online", "system": "SAMEER AI TWIN"}


# -- proactive end points---------------------------------------------------

@app.get("/api/proactive/briefing")
async def get_briefing():
    from services.proactive_service import get_morning_briefing
    briefing = get_morning_briefing()
    return {"briefing": briefing}

@app.get("/api/proactive/nudge")
async def get_nudge_api():
    from services.proactive_service import get_nudge
    nudge = get_nudge()
    return {"nudge": nudge, "show": bool(nudge)}

@app.get("/api/proactive/warnings")
async def get_warnings():
    from services.proactive_service import get_deadline_warnings
    warnings = get_deadline_warnings()
    return {"warnings": warnings}

