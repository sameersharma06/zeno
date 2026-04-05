# 🧠 Zeno — Personal AI Twin (Fully Local AI System)

![Local](https://img.shields.io/badge/100%25_Local-brightgreen)
![Apple Silicon](https://img.shields.io/badge/Apple_Silicon-black)
![Voice](https://img.shields.io/badge/Voice_Enabled-orange)
![Agents](https://img.shields.io/badge/5_Agents_System-purple)
![Mac App](https://img.shields.io/badge/Native_macOS_App-Swift-blue)
![Status](https://img.shields.io/badge/Status-Active_Development-blue)

> **Zeno is a fully local AI system that acts as your personal digital twin — it remembers, plans, and executes your life on your machine.**

No cloud. No subscriptions. No data leaving your device.

---

## ⚡ The Shift

AI today is powerful — but fundamentally broken.

- It forgets you  
- It depends on the internet  
- It sends your data to servers  

> Zeno flips the model.

Instead of *you using AI* → **AI works for you locally**

---

## 🧠 What Zeno Is

Zeno is not a chatbot.

It is a **multi-layered AI system** built around:

- Memory  
- Agents  
- Voice  
- Personal context  
- Proactive behavior  

> Think of it as a **personal AI operating system**

---

## 🔥 What Actually Works (Today)

### 🧠 Local AI Brain
- Qwen2.5 7B running via MLX (Apple Silicon optimized)
- Real-time streaming responses
- Multi-mode personality (Strict / Coach / Chill)

### 🎤 Fully Offline Voice
- Whisper STT + Kokoro TTS
- Real-time conversation loop
- No API calls, no tracking

### 📋 Task System
- Natural language → structured tasks
- Deadline detection
- SQLite-backed persistence

### 🧬 Memory Engine
- Logs every interaction
- Learns behavior patterns
- Generates daily summaries

### 📚 Personal Knowledge (RAG)
- Reads from your local files (`~/Notes`)
- LlamaIndex + ChromaDB
- Fully private embeddings

### 🤖 Multi-Agent System

| Agent | Role |
|------|------|
| Task Agent | Task execution |
| Research Agent | Knowledge retrieval |
| Coding Agent | Code generation |
| Automation Agent | System control |
| Brain | Planning + reasoning |

### ⚡ Proactive Intelligence
- Morning briefings  
- Deadline alerts  
- Context-aware nudges  

Zeno doesn’t wait.  
It **initiates**.

---

## 🖥️ Native macOS App (Core Advantage)

Zeno runs as a **real Mac application**, not a browser wrapper.

- Built using **Swift + WebKit**
- Distributed via `.dmg`
- Runs local backend on `localhost`
- Designed for OS-level automation

> This is a major advantage over web-based AI tools.

---

## 🧱 Real Architecture

```
User (voice / text)
        ↓
FastAPI (single port system)
        ↓
LangGraph Router (intent classification)
        ↓
 ┌───────────────────────────────┐
 │ Task Agent      → SQLite      │
 │ Research Agent  → RAG         │
 │ Coding Agent    → LLM         │
 │ Automation Agent→ macOS       │
 │ Brain Agent     → Planning    │
 └───────────────────────────────┘
        ↓
Memory Engine → behavior tracking
        ↓
Response → Text + Voice
```

---

## ⚙️ Key Engineering Decisions

- **Single-port architecture (8000)**  
  → fixed frontend/backend failures  

- **Fully local inference (MLX)**  
  → zero API dependency  

- **Agent-based modular system**  
  → scalable architecture  

- **Native Mac integration**  
  → future automation capability  

---

## 🧪 Real Problems Solved

- Fixed connection failures (multi-port → single-port)
- Removed hardcoded system paths → portable system
- Built backend health-check → no blank UI
- Reduced blocking inference issues
- Optimized local model performance

> This is not a demo. This is an evolving system.

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Qwen2.5 (MLX) |
| Voice STT | Whisper |
| Voice TTS | Kokoro |
| Agents | LangGraph |
| RAG | LlamaIndex + ChromaDB |
| Backend | FastAPI |
| Frontend | React + Vite |
| Mac App | Swift + WebKit |
| Storage | SQLite |

---

## ▶️ Run Locally

```bash
git clone https://github.com/sameersharma06/zeno
cd zeno
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
uvicorn api.server:app --host 0.0.0.0 --port 8000
```

Open → http://localhost:8000

---

## 🚀 Roadmap

| Version | Feature |
|--------|--------|
| v1 | Core system (brain + voice + memory + agents) ✅ |
| v2 | Action engine (control Mac) 🔨 |
| v3 | Web search (optional) 📋 |
| v4 | Vision + behavior graph 📋 |

---

## 🧠 Vision

> Every person will have a personal AI system that thinks, remembers, and acts for them.

Zeno is an early version of that future.

---

## 👤 Builder

Built end-to-end by a solo developer in India.

Focused on:
- Local AI systems  
- Agents & automation  
- Personal intelligence systems  

---

## contact

📧 Email: sameersharmaa95@gmail.com
💼 LinkedIn: https://www.linkedin.com/in/sameersharma0028/
🐦 Twitter/X: @sameersharma28_
📍 Haryana, India 

---

## ⭐

If you believe AI should be **private by default**, star this repo.