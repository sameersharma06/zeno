from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import json
import threading
import queue
import tempfile
import asyncio

router = APIRouter()

# ── MODELS ─────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    voice_mode: bool = False
    history: list = []  # ✅ ADDED MEMORY


class TaskRequest(BaseModel):
    task: str
    deadline: str


class TaskCompleteRequest(BaseModel):
    task_id: int


# ── CHAT ─────────────────────────────────────────

@router.post("/api/chat")
async def chat(req: ChatRequest):
    from agents.router import run_agents
    from core.tasks import get_tasks

    try:
        tasks_text = "\n".join([f"- {t[1]} (due {t[2]})" for t in get_tasks()])

        reply, agent = run_agents(
            req.message,
            tasks_text,
            history=req.history  # ✅ PASS HISTORY
        )

        return {"reply": reply, "agent": agent}

    except Exception as e:
        return {"error": f"Chat failed: {str(e)}"}


# ── STREAMING CHAT ───────────────────────────────

@router.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    from core.tasks import get_tasks
    from core.memory import log_event, get_context_summary
    from core.brain import _load_model, FULL_SYSTEM_PROMPT
    from core.state import get_full_state
    from mlx_lm import stream_generate

    try:
        tasks_text = "\n".join([f"- {t[1]} (due {t[2]})" for t in get_tasks()])

        model, tokenizer = _load_model()
        recent_activity = get_context_summary()

        system_content = FULL_SYSTEM_PROMPT.format(
            tasks=tasks_text,
            recent_activity=recent_activity
        )

        # limit state size
        state = get_full_state()
        if len(state) > 1000:
            state = state[:1000]

        system_content += "\n\n" + state

        # ✅ BUILD MESSAGES WITH HISTORY
        messages_list = [{"role": "system", "content": system_content}]

        if req.history:
            messages_list += req.history[-10:]

        messages_list.append({"role": "user", "content": req.message})

        prompt = tokenizer.apply_chat_template(
            messages_list, tokenize=False, add_generation_prompt=True
        )

    except Exception as e:
        return {"error": f"Setup failed: {str(e)}"}

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
        loop = asyncio.get_running_loop()

        while True:
            token = await loop.run_in_executor(None, token_q.get)

            if token is None:
                try:
                    log_event("response", full_response[:200])
                except:
                    pass
                yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"
                break

            if token.startswith("[ERROR]"):
                yield f"data: {json.dumps({'token': token[7:], 'done': True})}\n\n"
                break

            full_response += token
            yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"

    return StreamingResponse(token_stream(), media_type="text/event-stream")


# ── VOICE ─────────────────────────────────────────

@router.post("/api/voice/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    from core.voice import transcribe

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(await file.read())
            temp_path = temp_file.name

        text = transcribe(temp_path)
        return {"text": text}

    except Exception as e:
        return {"error": f"Transcription failed: {str(e)}"}


@router.post("/api/voice/speak")
async def speak_text(req: ChatRequest):
    from core.voice import speak
    from core.brain import get_response
    from core.tasks import get_tasks

    try:
        tasks_text = "\n".join([f"- {t[1]} (due {t[2]})" for t in get_tasks()])

        reply = get_response(
            req.message,
            tasks_text,
            history=req.history  # ✅ MEMORY SUPPORT
        )

        audio_path = speak(reply)
        return FileResponse(audio_path, media_type="audio/wav")

    except Exception as e:
        return {"error": f"TTS failed: {str(e)}"}


# ── TASKS ─────────────────────────────────────────

@router.get("/api/tasks")
async def get_all_tasks():
    from core.tasks import get_tasks

    try:
        tasks = get_tasks()
        return {"tasks": [{"id": t[0], "task": t[1], "deadline": t[2]} for t in tasks]}
    except Exception as e:
        return {"error": str(e)}


@router.post("/api/tasks/add")
async def add_new_task(req: TaskRequest):
    from core.tasks import add_task

    try:
        add_task(req.task, req.deadline)
        return {"status": "added"}
    except Exception as e:
        return {"error": str(e)}


@router.post("/api/tasks/complete")
async def complete_task(req: TaskCompleteRequest):
    from core.tasks import mark_done

    try:
        mark_done(req.task_id)
        return {"status": "completed"}
    except Exception as e:
        return {"error": str(e)}


# ── MEMORY ───────────────────────────────────────

@router.get("/api/memory/summary")
async def get_summary():
    from core.memory import generate_daily_summary

    try:
        return {"summary": generate_daily_summary()}
    except Exception as e:
        return {"error": str(e)}


# ── HEALTH ───────────────────────────────────────

@router.get("/api/health")
async def health():
    return {"status": "online", "system": "Zeno AI"}

    