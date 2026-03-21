import { useState, useEffect, useRef } from "react"
import axios from "axios"

const API = `http://${window.location.hostname}:8000/api`

// ── ICONS ──────────────────────────────────────────────────────────────
const Icons = {
    chat: (active) => (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
                stroke={active ? "#ffffff" : "#666"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                fill={active ? "#ffffff20" : "none"} />
        </svg>
    ),
    tasks: (active) => (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M9 11l3 3L22 4" stroke={active ? "#ffffff" : "#666"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"
                stroke={active ? "#ffffff" : "#666"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    memory: (active) => (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke={active ? "#ffffff" : "#666"} strokeWidth="2" />
            <path d="M12 8v4l3 3" stroke={active ? "#ffffff" : "#666"} strokeWidth="2" strokeLinecap="round" />
        </svg>
    ),
    proactive: (active) => (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"
                stroke={active ? "#ffffff" : "#666"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0"
                stroke={active ? "#ffffff" : "#666"} strokeWidth="2" strokeLinecap="round" />
        </svg>
    ),
    mic: () => (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" fill="white" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" stroke="white" strokeWidth="2" strokeLinecap="round" />
            <line x1="12" y1="19" x2="12" y2="23" stroke="white" strokeWidth="2" strokeLinecap="round" />
            <line x1="8" y1="23" x2="16" y2="23" stroke="white" strokeWidth="2" strokeLinecap="round" />
        </svg>
    ),
    send: () => (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <line x1="22" y1="2" x2="11" y2="13" stroke="white" strokeWidth="2" strokeLinecap="round" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" fill="white" />
        </svg>
    ),
}

// ── AGENT COLORS ───────────────────────────────────────────────────────
const AGENT = {
    TaskAgent: { label: "Task", color: "#25D366" },
    ResearchAgent: { label: "Research", color: "#34B7F1" },
    CodingAgent: { label: "Code", color: "#FFB74D" },
    AutomationAgent: { label: "Auto", color: "#EC407A" },
    Brain: { label: "Brain", color: "#7C4DFF" },
    StrictCoach: { label: "Coach", color: "#FF5252" },
    "...": { label: "...", color: "#666" },
    Error: { label: "Error", color: "#FF5252" },
}

// ── PROACTIVE PANEL ────────────────────────────────────────────────────
function ProactivePanel() {
    const [briefing, setBriefing] = useState("")
    const [nudge, setNudge] = useState("")
    const [warnings, setWarnings] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        Promise.all([
            axios.get(`${API}/proactive/briefing`),
            axios.get(`${API}/proactive/nudge`),
            axios.get(`${API}/proactive/warnings`),
        ]).then(([b, n, w]) => {
            setBriefing(b.data.briefing)
            if (n.data.show) setNudge(n.data.nudge)
            setWarnings(w.data.warnings)
        }).catch(() => { }).finally(() => setLoading(false))
    }, [])

    if (loading) return (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "200px" }}>
            <div style={{ color: "#666", fontSize: "14px" }}>Loading...</div>
        </div>
    )

    return (
        <div style={{ padding: "16px", display: "flex", flexDirection: "column", gap: "12px" }}>
            {warnings.map((w, i) => (
                <div key={i} style={{
                    padding: "14px 16px", background: "#1a0a0a",
                    border: "1px solid #FF525230", borderRadius: "16px",
                    fontSize: "14px", color: "#FF8A80",
                    display: "flex", alignItems: "center", gap: "10px",
                }}>
                    <span style={{ fontSize: "18px" }}>⏰</span>
                    {w}
                </div>
            ))}
            {nudge && (
                <div style={{
                    padding: "14px 16px", background: "#0a0a1a",
                    border: "1px solid #7C4DFF30", borderRadius: "16px",
                    fontSize: "14px", color: "#B39DDB",
                    display: "flex", alignItems: "center", gap: "10px",
                }}>
                    <span style={{ fontSize: "18px" }}>💡</span>
                    {nudge}
                </div>
            )}
            {briefing && (
                <div style={{
                    background: "#111", borderRadius: "16px",
                    padding: "16px", border: "1px solid #222",
                }}>
                    <div style={{
                        fontSize: "11px", color: "#555",
                        letterSpacing: "0.08em", textTransform: "uppercase",
                        marginBottom: "10px", fontWeight: "600",
                    }}>Morning Briefing</div>
                    <div style={{ fontSize: "14px", color: "#ccc", lineHeight: "1.7", whiteSpace: "pre-wrap" }}>
                        {briefing}
                    </div>
                </div>
            )}
        </div>
    )
}

// ── MAIN APP ───────────────────────────────────────────────────────────
export default function App() {
    const [messages, setMessages] = useState([
        { role: "ai", content: "Hey Sameer 👋 I'm online and ready. What do you want to work on?", agent: "Brain" }
    ])
    const [input, setInput] = useState("")
    const [loading, setLoading] = useState(false)
    const [tasks, setTasks] = useState([])
    const [newTask, setNewTask] = useState("")
    const [newDeadline, setNewDeadline] = useState("")
    const [patterns, setPatterns] = useState([])
    const [insight, setInsight] = useState("")
    const [insightLoading, setInsightLoading] = useState(false)
    const [summary, setSummary] = useState("")
    const [activeTab, setActiveTab] = useState("chat")
    const [recording, setRecording] = useState(false)
    const [recordingSeconds, setRecordingSeconds] = useState(5)
    const messagesEndRef = useRef(null)
    const inputRef = useRef(null)
    const mediaRecorderRef = useRef(null)
    const audioChunksRef = useRef([])
    const recordingTimerRef = useRef(null)

    useEffect(() => { fetchTasks(); fetchPatterns() }, [])
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages])

    const fetchTasks = async () => {
        try { const r = await axios.get(`${API}/tasks`); setTasks(r.data.tasks) } catch (e) { }
    }
    const fetchPatterns = async () => {
        try { const r = await axios.get(`${API}/memory/patterns`); setPatterns(r.data.patterns) } catch (e) { }
    }

    const sendMessage = async (msg) => {
        if (!msg.trim() || loading) return
        setMessages(prev => [...prev, { role: "user", content: msg }])
        setInput("")
        setLoading(true)
        setMessages(prev => [...prev, { role: "ai", content: "", agent: "..." }])

        try {
            const response = await fetch(`${API}/chat/stream`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: msg })
            })
            const reader = response.body.getReader()
            const decoder = new TextDecoder()
            let fullContent = ""
            let agentName = "Brain"
            let buffer = ""

            while (true) {
                const { done, value } = await reader.read()
                if (done) break
                buffer += decoder.decode(value, { stream: true })
                const lines = buffer.split("\n")
                buffer = lines.pop() || ""
                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        try {
                            const data = JSON.parse(line.slice(6))
                            agentName = data.agent || agentName
                            if (data.done) { setLoading(false); fetchTasks(); break }
                            if (data.token) {
                                fullContent += data.token
                                setMessages(prev => {
                                    const u = [...prev]
                                    u[u.length - 1] = { role: "ai", content: fullContent, agent: agentName }
                                    return u
                                })
                            }
                        } catch (e) { }
                    }
                }
            }
        } catch (e) {
            setMessages(prev => {
                const u = [...prev]
                u[u.length - 1] = { role: "ai", content: "Connection error. Is the backend running?", agent: "Error" }
                return u
            })
            setLoading(false)
        }
    }

    const addTask = async () => {
        if (!newTask.trim()) return
        await axios.post(`${API}/tasks/add`, { task: newTask, deadline: newDeadline || "TBD" })
        setNewTask(""); setNewDeadline(""); fetchTasks()
    }

    const completeTask = async (id) => {
        await axios.post(`${API}/tasks/complete`, { task_id: id }); fetchTasks()
    }

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
            mediaRecorderRef.current = new MediaRecorder(stream)
            audioChunksRef.current = []
            mediaRecorderRef.current.ondataavailable = (e) => audioChunksRef.current.push(e.data)
            mediaRecorderRef.current.onstop = async () => {
                const blob = new Blob(audioChunksRef.current, { type: "audio/wav" })
                const formData = new FormData()
                formData.append("file", blob, "voice.wav")
                try {
                    setLoading(true)
                    const res = await axios.post(`${API}/voice/transcribe`, formData)
                    await sendMessage(res.data.text)
                } catch (e) {
                    setMessages(prev => [...prev, { role: "ai", content: "Could not transcribe. Try again.", agent: "Error" }])
                    setLoading(false)
                }
                stream.getTracks().forEach(t => t.stop())
            }
            mediaRecorderRef.current.start()
            setRecording(true)
            setRecordingSeconds(5)
            recordingTimerRef.current = setInterval(() => {
                setRecordingSeconds(s => {
                    if (s <= 1) { stopRecording(); return 5 }
                    return s - 1
                })
            }, 1000)
        } catch (e) { alert("Microphone access denied.") }
    }

    const stopRecording = () => {
        if (mediaRecorderRef.current && recording) {
            mediaRecorderRef.current.stop()
            setRecording(false)
            clearInterval(recordingTimerRef.current)
        }
    }

    const renderMessage = (content) => {
        if (!content) return null
        return content.split("\n").map((line, i) => {
            if (line.startsWith("# ")) return <div key={i} style={{ fontWeight: "600", fontSize: "16px", margin: "8px 0 4px", color: "#fff" }}>{line.slice(2)}</div>
            if (line.startsWith("## ")) return <div key={i} style={{ fontWeight: "600", fontSize: "14px", margin: "6px 0 3px", color: "#eee" }}>{line.slice(3)}</div>
            if (line.startsWith("- ") || line.startsWith("• ")) return (
                <div key={i} style={{ display: "flex", gap: "8px", margin: "2px 0" }}>
                    <span style={{ color: "#25D366", flexShrink: 0, marginTop: "2px" }}>•</span>
                    <span>{line.slice(2)}</span>
                </div>
            )
            if (line.match(/^\d+\./)) return (
                <div key={i} style={{ display: "flex", gap: "8px", margin: "2px 0" }}>
                    <span style={{ color: "#25D366", flexShrink: 0, minWidth: "18px" }}>{line.match(/^\d+/)[0]}.</span>
                    <span>{line.replace(/^\d+\.\s*/, "")}</span>
                </div>
            )
            if (line === "") return <div key={i} style={{ height: "5px" }} />
            if (line.startsWith("```")) return null
            return <div key={i} style={{ margin: "1px 0", lineHeight: "1.6" }}>{line}</div>
        })
    }

    const now = new Date()
    const timeStr = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })

    return (
        <div style={{
            display: "flex", flexDirection: "column",
            height: "100vh", height: "100dvh",
            background: "#000", color: "#e8e8e6",
            fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            fontSize: "14px", overflow: "hidden",
            maxWidth: "480px", margin: "0 auto",
            position: "relative",
        }}>

            {/* ── TOP HEADER ── */}
            <div style={{
                background: "#1a1a1a",
                padding: "12px 16px 10px",
                display: "flex", alignItems: "center", gap: "12px",
                borderBottom: "1px solid #222",
                paddingTop: "calc(12px + env(safe-area-inset-top))",
                flexShrink: 0,
            }}>
                {/* Avatar */}
                <div style={{
                    width: "40px", height: "40px", borderRadius: "50%",
                    background: "linear-gradient(135deg, #7C4DFF, #25D366)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: "16px", fontWeight: "700", color: "white",
                    flexShrink: 0,
                }}>S</div>

                {/* Name and status */}
                <div style={{ flex: 1 }}>
                    <div style={{ fontSize: "16px", fontWeight: "600", color: "#fff" }}>
                        Zeno
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "5px", marginTop: "1px" }}>
                        <div style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#25D366" }} />
                        <span style={{ fontSize: "12px", color: "#25D366" }}>Online · Local · Private</span>
                    </div>
                </div>

                {/* Time */}
                <div style={{ fontSize: "12px", color: "#555" }}>{timeStr}</div>
            </div>

            {/* ── CONTENT AREA ── */}
            <div style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }}>

                {/* ── CHAT TAB ── */}
                {activeTab === "chat" && (
                    <>
                        {/* Messages */}
                        <div style={{
                            flex: 1, overflowY: "auto",
                            padding: "12px 12px 8px",
                            display: "flex", flexDirection: "column", gap: "4px",
                            background: "#0d0d0d",
                        }}>
                            {messages.map((msg, i) => {
                                const cfg = AGENT[msg.agent] || AGENT.Brain
                                const isUser = msg.role === "user"
                                return (
                                    <div key={i} style={{
                                        display: "flex",
                                        justifyContent: isUser ? "flex-end" : "flex-start",
                                        marginBottom: "4px",
                                    }}>
                                        <div style={{ maxWidth: "82%", display: "flex", flexDirection: "column", alignItems: isUser ? "flex-end" : "flex-start" }}>
                                            {/* Agent label */}
                                            {!isUser && msg.agent && msg.agent !== "..." && (
                                                <div style={{
                                                    fontSize: "10px", color: cfg.color,
                                                    marginBottom: "3px", marginLeft: "4px",
                                                    fontWeight: "600", letterSpacing: "0.04em",
                                                }}>
                                                    {cfg.label}
                                                </div>
                                            )}

                                            {/* Bubble */}
                                            <div style={{
                                                padding: "9px 13px",
                                                borderRadius: isUser
                                                    ? "18px 18px 4px 18px"
                                                    : "18px 18px 18px 4px",
                                                background: isUser ? "#25D366" : "#1e1e1e",
                                                color: isUser ? "#fff" : "#e0e0e0",
                                                fontSize: "14px",
                                                lineHeight: "1.5",
                                                border: isUser ? "none" : "1px solid #2a2a2a",
                                                position: "relative",
                                            }}>
                                                {isUser ? msg.content : renderMessage(msg.content)}

                                                {/* Blinking cursor when streaming */}
                                                {!isUser && msg.content === "" && loading && (
                                                    <span style={{
                                                        display: "inline-block", width: "2px", height: "14px",
                                                        background: cfg.color, marginLeft: "2px",
                                                        animation: "blink 1s infinite", verticalAlign: "middle",
                                                    }} />
                                                )}

                                                {/* Typing dots */}
                                                {!isUser && msg.agent === "..." && (
                                                    <div style={{ display: "flex", gap: "4px", alignItems: "center", padding: "2px 0" }}>
                                                        {[0, 1, 2].map(j => (
                                                            <div key={j} style={{
                                                                width: "6px", height: "6px", borderRadius: "50%",
                                                                background: "#555",
                                                                animation: `bounce 1.2s ${j * 200}ms infinite`,
                                                            }} />
                                                        ))}
                                                    </div>
                                                )}
                                            </div>

                                            {/* Time */}
                                            <div style={{
                                                fontSize: "10px", color: "#444",
                                                marginTop: "2px",
                                                marginLeft: isUser ? "0" : "4px",
                                                marginRight: isUser ? "4px" : "0",
                                            }}>
                                                {timeStr}
                                            </div>
                                        </div>
                                    </div>
                                )
                            })}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input bar */}
                        <div style={{
                            background: "#1a1a1a",
                            padding: "8px 12px",
                            paddingBottom: "calc(8px + env(safe-area-inset-bottom))",
                            borderTop: "1px solid #222",
                            display: "flex", alignItems: "flex-end", gap: "8px",
                            flexShrink: 0,
                        }}>
                            {/* Text input */}
                            <div style={{
                                flex: 1, background: "#2a2a2a",
                                borderRadius: "24px", padding: "10px 16px",
                                display: "flex", alignItems: "center",
                            }}>
                                <textarea
                                    ref={inputRef}
                                    value={input}
                                    onChange={e => {
                                        setInput(e.target.value)
                                        e.target.style.height = "auto"
                                        e.target.style.height = Math.min(e.target.scrollHeight, 100) + "px"
                                    }}
                                    onKeyDown={e => {
                                        if (e.key === "Enter" && !e.shiftKey) {
                                            e.preventDefault()
                                            sendMessage(input)
                                        }
                                    }}
                                    placeholder="Message..."
                                    rows={1}
                                    style={{
                                        flex: 1, background: "transparent",
                                        border: "none", outline: "none",
                                        resize: "none", fontSize: "14px",
                                        color: "#e0e0de", fontFamily: "inherit",
                                        lineHeight: "1.4", maxHeight: "100px",
                                    }}
                                />
                            </div>

                            {/* Voice or Send button */}
                            {input.trim() ? (
                                <button
                                    onClick={() => sendMessage(input)}
                                    disabled={loading}
                                    style={{
                                        width: "44px", height: "44px", borderRadius: "50%",
                                        background: "#25D366", border: "none",
                                        display: "flex", alignItems: "center", justifyContent: "center",
                                        cursor: "pointer", flexShrink: 0,
                                        opacity: loading ? 0.6 : 1,
                                    }}
                                >
                                    {Icons.send()}
                                </button>
                            ) : (
                                <button
                                    onClick={recording ? stopRecording : startRecording}
                                    style={{
                                        width: "44px", height: "44px", borderRadius: "50%",
                                        background: recording ? "#FF5252" : "#25D366",
                                        border: "none",
                                        display: "flex", alignItems: "center", justifyContent: "center",
                                        cursor: "pointer", flexShrink: 0,
                                        animation: recording ? "pulse 1s infinite" : "none",
                                    }}
                                >
                                    {recording
                                        ? <span style={{ color: "white", fontSize: "13px", fontWeight: "700" }}>{recordingSeconds}</span>
                                        : Icons.mic()
                                    }
                                </button>
                            )}
                        </div>
                    </>
                )}

                {/* ── TASKS TAB ── */}
                {activeTab === "tasks" && (
                    <div style={{ flex: 1, overflowY: "auto", background: "#0d0d0d" }}>
                        {/* Add task bar */}
                        <div style={{
                            background: "#1a1a1a", padding: "12px 16px",
                            borderBottom: "1px solid #222",
                            display: "flex", gap: "8px", alignItems: "center",
                        }}>
                            <input
                                value={newTask}
                                onChange={e => setNewTask(e.target.value)}
                                onKeyDown={e => e.key === "Enter" && addTask()}
                                placeholder="Add a task..."
                                style={{
                                    flex: 1, background: "#2a2a2a", border: "none",
                                    borderRadius: "20px", padding: "10px 16px",
                                    fontSize: "14px", color: "#e0e0de", outline: "none",
                                    fontFamily: "inherit",
                                }}
                            />
                            <button
                                onClick={addTask}
                                style={{
                                    width: "36px", height: "36px", borderRadius: "50%",
                                    background: "#25D366", border: "none",
                                    fontSize: "20px", color: "white", cursor: "pointer",
                                    display: "flex", alignItems: "center", justifyContent: "center",
                                    flexShrink: 0,
                                }}
                            >+</button>
                        </div>

                        {/* Task count */}
                        <div style={{ padding: "12px 16px 8px", fontSize: "12px", color: "#555", letterSpacing: "0.04em" }}>
                            {tasks.length} PENDING TASKS
                        </div>

                        {/* Tasks */}
                        <div style={{ padding: "0 12px 100px" }}>
                            {tasks.length === 0 && (
                                <div style={{ textAlign: "center", color: "#333", padding: "60px 20px", fontSize: "14px" }}>
                                    No pending tasks 🎉
                                </div>
                            )}
                            {tasks.map(task => (
                                <div
                                    key={task.id}
                                    style={{
                                        display: "flex", alignItems: "center", gap: "12px",
                                        padding: "14px 16px", marginBottom: "6px",
                                        background: "#1a1a1a", borderRadius: "16px",
                                        border: "1px solid #222",
                                    }}
                                >
                                    <button
                                        onClick={() => completeTask(task.id)}
                                        style={{
                                            width: "22px", height: "22px", borderRadius: "50%",
                                            border: "2px solid #333", background: "transparent",
                                            cursor: "pointer", flexShrink: 0,
                                            transition: "all 0.2s",
                                        }}
                                        onMouseEnter={e => {
                                            e.currentTarget.style.background = "#25D366"
                                            e.currentTarget.style.borderColor = "#25D366"
                                        }}
                                        onMouseLeave={e => {
                                            e.currentTarget.style.background = "transparent"
                                            e.currentTarget.style.borderColor = "#333"
                                        }}
                                    />
                                    <div style={{ flex: 1 }}>
                                        <div style={{ fontSize: "14px", color: "#e0e0de" }}>{task.task}</div>
                                        <div style={{ fontSize: "11px", color: "#555", marginTop: "2px" }}>Due {task.deadline}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* ── MEMORY TAB ── */}
                {activeTab === "memory" && (
                    <div style={{ flex: 1, overflowY: "auto", background: "#0d0d0d", padding: "16px 12px 100px" }}>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "16px" }}>
                            {[
                                {
                                    label: "Daily Insight", icon: "💡", action: async () => {
                                        setInsightLoading(true)
                                        try { const r = await axios.get(`${API}/memory/insight`); setInsight(r.data.insight) } catch (e) { }
                                        setInsightLoading(false)
                                    }, loading: insightLoading
                                },
                                {
                                    label: "Day Summary", icon: "📊", action: async () => {
                                        try { const r = await axios.get(`${API}/memory/summary`); setSummary(r.data.summary) } catch (e) { }
                                    }, loading: false
                                },
                            ].map((item, i) => (
                                <button key={i} onClick={item.action} disabled={item.loading} style={{
                                    padding: "16px", background: "#1a1a1a",
                                    border: "1px solid #222", borderRadius: "16px",
                                    textAlign: "left", cursor: "pointer",
                                    opacity: item.loading ? 0.6 : 1, fontFamily: "inherit",
                                }}>
                                    <div style={{ fontSize: "22px", marginBottom: "6px" }}>{item.icon}</div>
                                    <div style={{ fontSize: "13px", fontWeight: "500", color: "#e0e0de" }}>
                                        {item.loading ? "Loading..." : item.label}
                                    </div>
                                </button>
                            ))}
                        </div>

                        {insight && (
                            <div style={{
                                background: "#1a1a1a", border: "1px solid #222",
                                borderRadius: "16px", padding: "16px", marginBottom: "10px",
                                fontSize: "14px", color: "#d0d0ce", lineHeight: "1.7", whiteSpace: "pre-wrap",
                            }}>{insight}</div>
                        )}

                        {summary && (
                            <div style={{
                                background: "#1a1a1a", border: "1px solid #222",
                                borderRadius: "16px", padding: "16px", marginBottom: "10px",
                                fontSize: "12px", color: "#888", lineHeight: "1.8",
                                whiteSpace: "pre-wrap", fontFamily: "monospace",
                            }}>{summary}</div>
                        )}

                        {patterns.length > 0 && (
                            <div>
                                <div style={{ fontSize: "11px", color: "#555", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: "10px" }}>
                                    Detected Patterns
                                </div>
                                {patterns.map((p, i) => (
                                    <div key={i} style={{
                                        padding: "12px 14px", marginBottom: "6px",
                                        background: "#1a1a1a", borderRadius: "12px",
                                        fontSize: "13px", color: "#888", border: "1px solid #222",
                                        display: "flex", gap: "10px",
                                    }}>
                                        <span style={{ color: "#25D366" }}>◆</span>{p}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* ── PROACTIVE TAB ── */}
                {activeTab === "proactive" && (
                    <div style={{ flex: 1, overflowY: "auto", background: "#0d0d0d", paddingBottom: "80px" }}>
                        <ProactivePanel />
                    </div>
                )}
            </div>

            {/* ── BOTTOM NAV (WhatsApp style) ── */}
            <div style={{
                background: "#1a1a1a",
                borderTop: "1px solid #222",
                display: "flex",
                paddingBottom: "env(safe-area-inset-bottom)",
                flexShrink: 0,
                position: "relative",
                zIndex: 10,
            }}>
                {[
                    { id: "chat", label: "Chat", icon: Icons.chat },
                    { id: "tasks", label: "Tasks", icon: Icons.tasks },
                    { id: "memory", label: "Memory", icon: Icons.memory },
                    { id: "proactive", label: "Proactive", icon: Icons.proactive },
                ].map(tab => {
                    const active = activeTab === tab.id
                    return (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            style={{
                                flex: 1, padding: "10px 0 8px",
                                background: "transparent", border: "none",
                                display: "flex", flexDirection: "column",
                                alignItems: "center", gap: "3px",
                                cursor: "pointer", transition: "all 0.15s",
                                position: "relative",
                            }}
                        >
                            {/* Active indicator */}
                            {active && (
                                <div style={{
                                    position: "absolute", top: "0", left: "50%",
                                    transform: "translateX(-50%)",
                                    width: "32px", height: "2px",
                                    background: "#25D366", borderRadius: "2px",
                                }} />
                            )}
                            {tab.icon(active)}
                            <span style={{
                                fontSize: "10px",
                                color: active ? "#fff" : "#555",
                                fontWeight: active ? "600" : "400",
                                letterSpacing: "0.02em",
                            }}>
                                {tab.label}
                            </span>
                            {/* Tasks badge */}
                            {tab.id === "tasks" && tasks.length > 0 && (
                                <div style={{
                                    position: "absolute", top: "6px", right: "calc(50% - 18px)",
                                    background: "#25D366", color: "white",
                                    borderRadius: "10px", fontSize: "9px",
                                    fontWeight: "700", padding: "1px 5px",
                                    minWidth: "16px", textAlign: "center",
                                }}>
                                    {tasks.length}
                                </div>
                            )}
                        </button>
                    )
                })}
            </div>

            <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
        body { overflow: hidden; background: #000; }
        input::placeholder, textarea::placeholder { color: #555; }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
        @keyframes bounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-4px); } }
        @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
        ::-webkit-scrollbar { width: 0; }
        input[type="date"]::-webkit-calendar-picker-indicator { filter: invert(0.3); }
      `}</style>
        </div>
    )
}
