# 🧠 Zeno — Personal AI Twin

![Local](https://img.shields.io/badge/100%25_Local-brightgreen)
![Apple Silicon](https://img.shields.io/badge/Apple_Silicon-black)
![Voice](https://img.shields.io/badge/Voice_Enabled-orange)
![Agents](https://img.shields.io/badge/LangGraph_Agents-5-purple)
![Status](https://img.shields.io/badge/Status-Active_Development-blue)
![Built in India](https://img.shields.io/badge/Built_in-Haryana_India-ff69b4)
![Stars](https://img.shields.io/github/stars/sameersharma06/zeno?style=social)

> Zeno is a personal AI twin that runs 100% on your Mac.
> No cloud. No subscriptions. No data leaving your machine.
> It knows your tasks, learns your patterns, and helps you
> plan and execute your day — every single day.

---

## Demo

> 🎬 Demo video coming soon — follow to get notified

---

## What makes Zeno different

Every AI tool today requires internet, charges monthly, and sends your data to servers you don't control.

Zeno runs entirely on your MacBook. Every conversation, every task, every memory stays on your machine. Forever. Private by design.

This is not a chatbot wrapper. This is a personal AI twin with memory, knowledge, agents, and voice — built from scratch on Apple Silicon.

---

## What Zeno does

### 🧠 AI Brain
Qwen2.5 running locally via MLX. Streams responses in real time. Knows your tasks, your patterns, your day. Three modes: Strict (blocks procrastination), Coach (pushes you), Chill (casual).

### 🎤 Voice Pipeline
Speak naturally → Whisper transcribes → Zeno thinks → Kokoro speaks back. Full offline voice conversation. No internet. No API calls.

### 📋 Task Engine
SQLite-backed task manager with deadlines. Add tasks by voice or text. Auto-detects tasks from conversation — "I have exam tomorrow" → task created automatically.

### 🧬 Memory Engine
Logs every interaction. Detects your patterns — most active hour, work preferences, daily habits. Builds daily summary automatically. Zeno knows what you did today without being told.

### 📚 RAG Knowledge
Answers from your own notes, PDFs, and documents. Fully local embeddings. Drop any file into ~/Notes → Zeno instantly knows it.

### 🤖 5 LangGraph Agents

| Agent | What it does |
|-------|-------------|
| Task Agent | Manages tasks via natural language |
| Research Agent | Queries your notes, falls back to LLM |
| Coding Agent | Writes code for your exact stack |
| Automation Agent | Opens Mac apps via voice |
| Brain | Planning, strategy, decisions |

### ⚡ Proactive Intelligence
Morning briefing. Hourly nudges. Deadline warnings. Zeno initiates — you don't have to ask.

### 🎭 Personality Engine
Detects Hinglish. Auto-switches modes based on situation. Feels like YOUR AI, not an AI.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Qwen2.5-7B-Instruct-4bit via mlx_lm |
| Speech to text | whisper-large-v3-turbo via mlx-audio |
| Text to speech | Kokoro-82M-bf16 via mlx-audio |
| Knowledge / RAG | LlamaIndex + ChromaDB |
| Embeddings | BAAI/bge-small-en-v1.5 (fully local) |
| Agents | LangGraph StateGraph |
| Backend | FastAPI |
| Frontend | React + Vite |
| Storage | SQLite |
| Hardware | Apple Silicon M-series (MLX native) |

---

## Run it yourself

Requirements: Mac with Apple Silicon (M1/M2/M3/M4) · 16GB RAM minimum
```bash
git clone https://github.com/sameersharma06/zeno
cd zeno
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && cd ..
python main.py
```

Open `http://localhost:5173` — Zeno starts automatically.

First run downloads ~6GB of models once. Fully offline after that. No API keys. No accounts.

---

## Add your own knowledge
```bash
# Drop any .txt .md .pdf into ~/Notes
cp your_notes.md ~/Notes/

# Rebuild the index
python knowledge/ingestor.py
```

---

## Roadmap

| Version | Feature | Status |
|---------|---------|--------|
| v1 | Brain + Voice + Tasks + Memory + Agents + Proactive | ✅ Live |
| v2 | Telegram bot — phone access | 🔨 Building |
| v3 | Action engine — control your Mac | 📋 Planned |
| v4 | Coming soon | 📋 Planned |

---

## Sponsorship

Built and maintained by one student in Haryana, India.

If Zeno helped you or you want to support local AI development:

- GitHub Sponsors — coming soon
- UPI: sameersharmaa95@gmail.com

**For companies:** If your company builds AI tools, developer tools, or Apple Silicon products and wants to be featured — reach out.

**What sponsors get:**
- Logo in README
- Mention in every LinkedIn/Twitter update
- Early access to Pro features
- Direct feedback channel

---

## Open to Opportunities

Solo AI builder from Haryana, India looking for:

- AI/ML Engineering Internship (remote or Delhi-NCR)
- Research Internship (AI, LLM, Agents)
- Part-time AI consulting
- Open source collaboration

**Stack:** Python · MLX · LangGraph · LlamaIndex · ChromaDB · React · FastAPI · Whisper · Kokoro · Qwen2.5 · Apple Silicon

📧 Email: sameersharmaa95@gmail.com
💼 LinkedIn: https://www.linkedin.com/in/sameersharma0028/
🐦 Twitter/X: @sameersharma28_
📍 Haryana, India · Open to remote globally · Available for in-office roles

---

*Star ⭐ this repo if you want your own personal AI twin.*
*Follow for weekly updates as I build this live.*
