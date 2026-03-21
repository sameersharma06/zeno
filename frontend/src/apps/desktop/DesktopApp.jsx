import { useState, useEffect, useRef } from "react"
import axios from "axios"

const API = `http://${window.location.hostname}:8000/api`



function ProactivePanel() {
    const [briefing, setBriefing] = useState("")
    const [nudge, setNudge] = useState("")
    const [warnings, setWarnings] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const load = async () => {
            try {
                const [b, n, w] = await Promise.all([
                    axios.get(`${API}/proactive/briefing`),
                    axios.get(`${API}/proactive/nudge`),
                    axios.get(`${API}/proactive/warnings`),
                ])
                setBriefing(b.data.briefing)
                if (n.data.show) setNudge(n.data.nudge)
                setWarnings(w.data.warnings)
            } catch (e) { }
            setLoading(false)
        }
        load()
    }, [])

    if (loading) return (
        <div style={{ color: "#4a4a52", fontSize: "13px" }}>Loading...</div>
    )

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {warnings.length > 0 && warnings.map((w, i) => (
                <div key={i} style={{
                    padding: "12px 16px",
                    background: "#2a1a1a",
                    border: "1px solid #ef444430",
                    borderRadius: "10px",
                    fontSize: "13px",
                    color: "#fca5a5",
                }}>
                    ⏰ {w}
                </div>
            ))}

            {nudge && (
                <div style={{
                    padding: "12px 16px",
                    background: "#1a1a2a",
                    border: "1px solid #6366f130",
                    borderRadius: "10px",
                    fontSize: "13px",
                    color: "#a5b4fc",
                }}>
                    💡 {nudge}
                </div>
            )}

            {briefing && (
                <div style={{
                    padding: "16px",
                    background: "#111113",
                    border: "1px solid #1c1c1e",
                    borderRadius: "12px",
                    fontSize: "13.5px",
                    color: "#d0d0ce",
                    lineHeight: "1.7",
                    whiteSpace: "pre-wrap",
                }}>
                    <div style={{
                        fontSize: "11px", color: "#4a4a52",
                        letterSpacing: "0.06em", textTransform: "uppercase",
                        marginBottom: "10px"
                    }}>
                        Morning Briefing
                    </div>
                    {briefing}
                </div>
            )}
        </div>
    )
}




export default function App() {
    const [messages, setMessages] = useState([
        {
            role: "ai",
            content: "Hey Sameer. I'm online and ready. What do you want to work on today?",
            agent: "Brain"
        }
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

    useEffect(() => {
        fetchTasks()
        fetchPatterns()
        inputRef.current?.focus()
    }, [])

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages])

    // Cmd+K to focus input
    useEffect(() => {
        const handler = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === "k") {
                e.preventDefault()
                inputRef.current?.focus()
            }
        }
        window.addEventListener("keydown", handler)
        return () => window.removeEventListener("keydown", handler)
    }, [])

    const fetchTasks = async () => {
        try {
            const res = await axios.get(`${API}/tasks`)
            setTasks(res.data.tasks)
        } catch (e) { }
    }

    const fetchPatterns = async () => {
        try {
            const res = await axios.get(`${API}/memory/patterns`)
            setPatterns(res.data.patterns)
        } catch (e) { }
    }

    const sendMessage = async (msg) => {
        if (!msg.trim() || loading) return
        const userMsg = { role: "user", content: msg }
        setMessages(prev => [...prev, userMsg])
        setInput("")
        setLoading(true)

        // Add empty AI message immediately
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

                            if (data.done) {
                                setLoading(false)
                                // Refresh tasks in case agent modified them
                                fetchTasks()
                                break
                            }

                            if (data.token) {
                                fullContent += data.token
                                const snap = fullContent
                                const snapAgent = agentName
                                setMessages(prev => {
                                    const updated = [...prev]
                                    updated[updated.length - 1] = {
                                        role: "ai",
                                        content: snap,
                                        agent: snapAgent
                                    }
                                    return updated
                                })
                            }
                        } catch (e) { }
                    }
                }
            }
        } catch (e) {
            setMessages(prev => {
                const updated = [...prev]
                updated[updated.length - 1] = {
                    role: "ai",
                    content: "Connection error. Make sure the backend is running on port 8000.",
                    agent: "Error"
                }
                return updated
            })
            setLoading(false)
        }
    }

    const addTask = async () => {
        if (!newTask.trim()) return
        await axios.post(`${API}/tasks/add`, {
            task: newTask,
            deadline: newDeadline || "TBD"
        })
        setNewTask("")
        setNewDeadline("")
        fetchTasks()
    }

    const completeTask = async (id) => {
        await axios.post(`${API}/tasks/complete`, { task_id: id })
        fetchTasks()
    }

    const getInsight = async () => {
        setInsightLoading(true)
        try {
            const res = await axios.get(`${API}/memory/insight`)
            setInsight(res.data.insight)
        } catch (e) { }
        setInsightLoading(false)
    }

    const getSummary = async () => {
        try {
            const res = await axios.get(`${API}/memory/summary`)
            setSummary(res.data.summary)
        } catch (e) { }
    }

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
            mediaRecorderRef.current = new MediaRecorder(stream)
            audioChunksRef.current = []
            mediaRecorderRef.current.ondataavailable = (e) => {
                audioChunksRef.current.push(e.data)
            }
            mediaRecorderRef.current.onstop = async () => {
                const blob = new Blob(audioChunksRef.current, { type: "audio/wav" })
                const formData = new FormData()
                formData.append("file", blob, "voice.wav")
                try {
                    setLoading(true)
                    const res = await axios.post(`${API}/voice/transcribe`, formData)
                    await sendMessage(res.data.text)
                } catch (e) {
                    setMessages(prev => [...prev, {
                        role: "ai",
                        content: "Could not transcribe. Please try again.",
                        agent: "Error"
                    }])
                    setLoading(false)
                }
                stream.getTracks().forEach(t => t.stop())
            }
            mediaRecorderRef.current.start()
            setRecording(true)
            setRecordingSeconds(5)

            recordingTimerRef.current = setInterval(() => {
                setRecordingSeconds(s => {
                    if (s <= 1) {
                        stopRecording()
                        return 5
                    }
                    return s - 1
                })
            }, 1000)

        } catch (e) {
            alert("Microphone access denied.")
        }
    }

    const stopRecording = () => {
        if (mediaRecorderRef.current && recording) {
            mediaRecorderRef.current.stop()
            setRecording(false)
            clearInterval(recordingTimerRef.current)
        }
    }

    const agentConfig = {
        TaskAgent: { label: "Task", color: "#10b981" },
        ResearchAgent: { label: "Research", color: "#6366f1" },
        CodingAgent: { label: "Code", color: "#f59e0b" },
        AutomationAgent: { label: "Automation", color: "#ec4899" },
        Brain: { label: "Brain", color: "#8b5cf6" },
        "...": { label: "Thinking", color: "#6b7280" },
        Error: { label: "Error", color: "#ef4444" },
    }

    const renderMessage = (content) => {
        // Simple markdown-like rendering
        return content.split("\n").map((line, i) => {
            if (line.startsWith("# ")) return <h1 key={i} style={{ fontSize: "18px", fontWeight: "600", margin: "12px 0 6px", color: "#f0f0ee" }}>{line.slice(2)}</h1>
            if (line.startsWith("## ")) return <h2 key={i} style={{ fontSize: "15px", fontWeight: "600", margin: "10px 0 4px", color: "#e0e0de" }}>{line.slice(3)}</h2>
            if (line.startsWith("### ")) return <h3 key={i} style={{ fontSize: "13px", fontWeight: "600", margin: "8px 0 4px", color: "#d0d0ce" }}>{line.slice(4)}</h3>
            if (line.startsWith("- ") || line.startsWith("• ")) return (
                <div key={i} style={{ display: "flex", gap: "8px", margin: "3px 0" }}>
                    <span style={{ color: "#6b7280", flexShrink: 0 }}>•</span>
                    <span>{line.slice(2)}</span>
                </div>
            )
            if (line.match(/^\d+\./)) return (
                <div key={i} style={{ display: "flex", gap: "8px", margin: "3px 0" }}>
                    <span style={{ color: "#6b7280", flexShrink: 0, minWidth: "16px" }}>{line.match(/^\d+/)[0]}.</span>
                    <span>{line.replace(/^\d+\.\s*/, "")}</span>
                </div>
            )
            if (line.startsWith("```") || line.endsWith("```")) return null
            if (line === "") return <div key={i} style={{ height: "6px" }} />
            return <p key={i} style={{ margin: "2px 0", lineHeight: "1.7" }}>{line}</p>
        })
    }

    return (
        <div style={{
            display: "flex",
            height: "100vh",
            background: "#0c0c0e",
            color: "#e8e8e6",
            fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            overflow: "hidden",
            fontSize: "14px",
        }}>

            {/* ── SIDEBAR ── */}
            <div style={{
                width: "240px",
                background: "#111113",
                borderRight: "1px solid #1c1c1e",
                display: "flex",
                flexDirection: "column",
                flexShrink: 0,
            }}>
                {/* Logo area */}
                <div style={{
                    padding: "16px 16px 12px",
                    borderBottom: "1px solid #1c1c1e",
                }}>
                    <div style={{
                        display: "flex", alignItems: "center",
                        gap: "10px", marginBottom: "8px"
                    }}>
                        <div style={{
                            width: "32px", height: "32px",
                            background: "#1c1c1e",
                            borderRadius: "10px",
                            display: "flex", alignItems: "center",
                            justifyContent: "center",
                            fontSize: "14px", fontWeight: "700",
                            color: "#e8e8e6",
                            border: "1px solid #2c2c2e",
                            letterSpacing: "-0.02em",
                        }}>S</div>
                        <div>
                            <div style={{ fontSize: "13px", fontWeight: "600", color: "#e8e8e6", letterSpacing: "-0.01em" }}>
                                Zeno
                            </div>
                            <div style={{ display: "flex", alignItems: "center", gap: "5px", marginTop: "1px" }}>
                                <div style={{ width: "5px", height: "5px", borderRadius: "50%", background: "#10b981" }} />
                                <span style={{ fontSize: "11px", color: "#4a4a52" }}>Online · Local</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Nav */}
                <div style={{ padding: "8px" }}>
                    {[
                        { id: "chat", label: "Chat", sub: "Ask anything" },
                        { id: "tasks", label: "Tasks", sub: `${tasks.length} pending` },
                        { id: "memory", label: "Memory", sub: "Patterns & insights" },
                        { id: "proactive", label: "Proactive", sub: "Briefing & nudges" },
                    ].map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            style={{
                                width: "100%",
                                display: "flex", alignItems: "center",
                                gap: "10px",
                                padding: "8px 10px",
                                borderRadius: "8px",
                                border: "none",
                                cursor: "pointer",
                                background: activeTab === tab.id ? "#1c1c1e" : "transparent",
                                color: activeTab === tab.id ? "#e8e8e6" : "#5a5a62",
                                textAlign: "left",
                                transition: "all 0.1s",
                                marginBottom: "2px",
                                fontFamily: "inherit",
                            }}
                        >
                            <div style={{ flex: 1 }}>
                                <div style={{ fontSize: "13px", fontWeight: activeTab === tab.id ? "500" : "400" }}>
                                    {tab.label}
                                </div>
                                <div style={{ fontSize: "11px", color: "#3a3a42", marginTop: "1px" }}>
                                    {tab.sub}
                                </div>
                            </div>
                        </button>
                    ))}
                </div>

                <div style={{ flex: 1 }} />



                {/* Bottom stats */}
                <div style={{
                    padding: "12px 16px",
                    borderTop: "1px solid #1c1c1e",
                }}>
                    <div style={{
                        display: "grid", gridTemplateColumns: "1fr 1fr",
                        gap: "8px", marginBottom: "10px"
                    }}>
                        {[
                            { label: "Tasks", value: tasks.length },
                            { label: "Local", value: "100%" },
                        ].map((stat, i) => (
                            <div key={i} style={{
                                background: "#141416",
                                borderRadius: "8px",
                                padding: "8px 10px",
                                border: "1px solid #1c1c1e",
                            }}>
                                <div style={{ fontSize: "16px", fontWeight: "600", color: "#e8e8e6", letterSpacing: "-0.02em" }}>
                                    {stat.value}
                                </div>
                                <div style={{ fontSize: "10px", color: "#4a4a52", marginTop: "1px" }}>
                                    {stat.label}
                                </div>
                            </div>
                        ))}
                    </div>
                    <div style={{ fontSize: "10px", color: "#3a3a42", lineHeight: "1.6", textAlign: "center" }}>
                        No cloud · No tracking · Private
                    </div>
                </div>
            </div>

            {/* ── MAIN ── */}
            <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>

                {/* ── CHAT ── */}
                {activeTab === "chat" && (
                    <>
                        {/* Messages */}
                        <div style={{
                            flex: 1,
                            overflowY: "auto",
                            padding: "0",
                        }}>
                            {messages.map((msg, i) => (
                                <div
                                    key={i}
                                    style={{
                                        padding: "20px 24px",
                                        borderBottom: "1px solid #141416",
                                        background: msg.role === "user" ? "#0c0c0e" : "#111113",
                                        display: "flex",
                                        gap: "14px",
                                        alignItems: "flex-start",
                                    }}
                                >
                                    {/* Avatar */}
                                    <div style={{
                                        width: "28px", height: "28px",
                                        borderRadius: "8px",
                                        background: msg.role === "user" ? "#1c1c1e" : "#1c1c1e",
                                        border: "1px solid #2c2c2e",
                                        display: "flex", alignItems: "center", justifyContent: "center",
                                        fontSize: "11px", fontWeight: "600",
                                        color: msg.role === "user" ? "#e8e8e6" : "#8b5cf6",
                                        flexShrink: 0,
                                        marginTop: "1px",
                                    }}>
                                        {msg.role === "user" ? "S" : "AI"}
                                    </div>

                                    {/* Content */}
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                        <div style={{
                                            display: "flex", alignItems: "center",
                                            gap: "8px", marginBottom: "6px"
                                        }}>
                                            <span style={{
                                                fontSize: "12px", fontWeight: "500",
                                                color: msg.role === "user" ? "#e8e8e6" : "#a0a09e",
                                            }}>
                                                {msg.role === "user" ? "You" : "Zeno"}
                                            </span>
                                            {msg.role === "ai" && msg.agent && (() => {
                                                const cfg = agentConfig[msg.agent] || agentConfig.Brain
                                                return (
                                                    <span style={{
                                                        fontSize: "10px",
                                                        color: cfg.color,
                                                        background: `${cfg.color}15`,
                                                        padding: "1px 7px",
                                                        borderRadius: "10px",
                                                        border: `1px solid ${cfg.color}30`,
                                                        fontWeight: "500",
                                                        letterSpacing: "0.02em",
                                                    }}>
                                                        {cfg.label}
                                                    </span>
                                                )
                                            })()}
                                        </div>
                                        <div style={{
                                            fontSize: "13.5px",
                                            lineHeight: "1.7",
                                            color: "#d8d8d6",
                                        }}>
                                            {msg.role === "ai" ? renderMessage(msg.content) : msg.content}
                                            {msg.role === "ai" && msg.content === "" && loading && (
                                                <span style={{
                                                    display: "inline-block",
                                                    width: "2px", height: "16px",
                                                    background: "#8b5cf6",
                                                    marginLeft: "1px",
                                                    animation: "blink 1s infinite",
                                                    verticalAlign: "text-bottom",
                                                }} />
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input */}
                        <div style={{
                            padding: "16px 24px 20px",
                            background: "#0c0c0e",
                            borderTop: "1px solid #1c1c1e",
                        }}>
                            <div style={{
                                background: "#111113",
                                border: "1px solid #2c2c2e",
                                borderRadius: "14px",
                                overflow: "hidden",
                            }}>
                                <div style={{
                                    display: "flex", alignItems: "flex-end",
                                    padding: "10px 12px",
                                    gap: "8px",
                                }}>
                                    <textarea
                                        ref={inputRef}
                                        value={input}
                                        onChange={e => {
                                            setInput(e.target.value)
                                            e.target.style.height = "auto"
                                            e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px"
                                        }}
                                        onKeyDown={e => {
                                            if (e.key === "Enter" && !e.shiftKey) {
                                                e.preventDefault()
                                                sendMessage(input)
                                            }
                                        }}
                                        placeholder="Message Zeno... (⌘K to focus)"
                                        rows={1}
                                        style={{
                                            flex: 1,
                                            background: "transparent",
                                            border: "none",
                                            outline: "none",
                                            resize: "none",
                                            fontSize: "13.5px",
                                            color: "#e0e0de",
                                            fontFamily: "inherit",
                                            lineHeight: "1.5",
                                            minHeight: "22px",
                                            maxHeight: "120px",
                                            overflowY: "auto",
                                        }}
                                    />

                                    {/* Voice button */}
                                    <button
                                        onClick={recording ? stopRecording : startRecording}
                                        style={{
                                            width: "30px", height: "30px",
                                            borderRadius: "8px",
                                            border: "none",
                                            background: recording ? "#ef444420" : "transparent",
                                            color: recording ? "#ef4444" : "#3a3a42",
                                            cursor: "pointer",
                                            fontSize: "13px",
                                            display: "flex", alignItems: "center",
                                            justifyContent: "center",
                                            flexShrink: 0,
                                            transition: "all 0.15s",
                                            fontFamily: "inherit",
                                        }}
                                        title="Voice input"
                                    >
                                        {recording ? `${recordingSeconds}s` : "🎙"}
                                    </button>

                                    {/* Send button */}
                                    <button
                                        onClick={() => sendMessage(input)}
                                        disabled={loading || !input.trim()}
                                        style={{
                                            width: "30px", height: "30px",
                                            borderRadius: "8px",
                                            border: "none",
                                            background: loading || !input.trim() ? "#1c1c1e" : "#e8e8e6",
                                            color: loading || !input.trim() ? "#3a3a42" : "#0c0c0e",
                                            cursor: loading || !input.trim() ? "not-allowed" : "pointer",
                                            fontSize: "14px",
                                            fontWeight: "700",
                                            display: "flex", alignItems: "center",
                                            justifyContent: "center",
                                            flexShrink: 0,
                                            transition: "all 0.15s",
                                            fontFamily: "inherit",
                                        }}
                                    >
                                        ↑
                                    </button>
                                </div>

                                {recording && (
                                    <div style={{
                                        padding: "6px 12px 8px",
                                        fontSize: "11px",
                                        color: "#ef4444",
                                        borderTop: "1px solid #1c1c1e",
                                        display: "flex", alignItems: "center", gap: "6px",
                                    }}>
                                        <div style={{
                                            width: "5px", height: "5px",
                                            borderRadius: "50%",
                                            background: "#ef4444",
                                            animation: "blink 1s infinite",
                                        }} />
                                        Recording · {recordingSeconds}s remaining · speak now
                                    </div>
                                )}
                            </div>

                            <div style={{
                                textAlign: "center", marginTop: "8px",
                                fontSize: "11px", color: "#2a2a2e",
                            }}>
                                Enter to send · Shift+Enter for new line · ⌘K to focus
                            </div>
                        </div>
                    </>
                )}

                {/* ── TASKS ── */}
                {activeTab === "tasks" && (
                    <div style={{ flex: 1, overflowY: "auto", padding: "24px", maxWidth: "720px", width: "100%" }}>
                        <div style={{ marginBottom: "24px" }}>
                            <h2 style={{ fontSize: "16px", fontWeight: "600", color: "#e8e8e6", marginBottom: "4px" }}>
                                Tasks
                            </h2>
                            <p style={{ fontSize: "12px", color: "#4a4a52" }}>
                                {tasks.length} pending · click circle to complete
                            </p>
                        </div>

                        {/* Add task */}
                        <div style={{
                            display: "flex", gap: "8px",
                            marginBottom: "20px",
                            background: "#111113",
                            border: "1px solid #1c1c1e",
                            borderRadius: "12px",
                            padding: "10px 12px",
                        }}>
                            <input
                                value={newTask}
                                onChange={e => setNewTask(e.target.value)}
                                onKeyDown={e => e.key === "Enter" && addTask()}
                                placeholder="Add a task..."
                                style={{
                                    flex: 1, background: "transparent",
                                    border: "none", outline: "none",
                                    fontSize: "13.5px", color: "#e0e0de",
                                    fontFamily: "inherit",
                                }}
                            />
                            <input
                                type="date"
                                value={newDeadline}
                                onChange={e => setNewDeadline(e.target.value)}
                                style={{
                                    background: "#1c1c1e",
                                    border: "1px solid #2c2c2e",
                                    borderRadius: "8px",
                                    padding: "4px 8px",
                                    fontSize: "12px",
                                    color: "#6a6a72",
                                    outline: "none",
                                    fontFamily: "inherit",
                                }}
                            />
                            <button
                                onClick={addTask}
                                style={{
                                    padding: "4px 14px",
                                    background: "#e8e8e6",
                                    color: "#0c0c0e",
                                    border: "none",
                                    borderRadius: "8px",
                                    fontSize: "12px",
                                    fontWeight: "600",
                                    cursor: "pointer",
                                    fontFamily: "inherit",
                                    whiteSpace: "nowrap",
                                }}
                            >
                                Add
                            </button>
                        </div>

                        {/* Tasks */}
                        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                            {tasks.length === 0 && (
                                <div style={{ textAlign: "center", color: "#3a3a42", padding: "40px", fontSize: "13px" }}>
                                    No pending tasks.
                                </div>
                            )}
                            {tasks.map(task => (
                                <div
                                    key={task.id}
                                    style={{
                                        display: "flex", alignItems: "center",
                                        gap: "12px",
                                        padding: "11px 14px",
                                        background: "#111113",
                                        border: "1px solid #1a1a1c",
                                        borderRadius: "10px",
                                        cursor: "default",
                                        transition: "border-color 0.1s",
                                    }}
                                    onMouseEnter={e => e.currentTarget.style.borderColor = "#2c2c2e"}
                                    onMouseLeave={e => e.currentTarget.style.borderColor = "#1a1a1c"}
                                >
                                    <button
                                        onClick={() => completeTask(task.id)}
                                        style={{
                                            width: "16px", height: "16px",
                                            borderRadius: "50%",
                                            border: "1.5px solid #3a3a42",
                                            background: "transparent",
                                            cursor: "pointer",
                                            flexShrink: 0,
                                            transition: "all 0.15s",
                                            display: "flex", alignItems: "center",
                                            justifyContent: "center",
                                            fontFamily: "inherit",
                                        }}
                                        onMouseEnter={e => {
                                            e.currentTarget.style.background = "#10b981"
                                            e.currentTarget.style.borderColor = "#10b981"
                                        }}
                                        onMouseLeave={e => {
                                            e.currentTarget.style.background = "transparent"
                                            e.currentTarget.style.borderColor = "#3a3a42"
                                        }}
                                    />
                                    <span style={{
                                        flex: 1, fontSize: "13.5px",
                                        color: "#d0d0ce", lineHeight: "1.4"
                                    }}>
                                        {task.task}
                                    </span>
                                    <span style={{
                                        fontSize: "11px", color: "#4a4a52",
                                        background: "#141416",
                                        padding: "2px 8px",
                                        borderRadius: "5px",
                                        border: "1px solid #1c1c1e",
                                        whiteSpace: "nowrap",
                                    }}>
                                        {task.deadline}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* ── MEMORY ── */}
                {activeTab === "memory" && (
                    <div style={{ flex: 1, overflowY: "auto", padding: "24px", maxWidth: "720px" }}>
                        <div style={{ marginBottom: "24px" }}>
                            <h2 style={{ fontSize: "16px", fontWeight: "600", color: "#e8e8e6", marginBottom: "4px" }}>
                                Memory
                            </h2>
                            <p style={{ fontSize: "12px", color: "#4a4a52" }}>
                                Patterns, insights, and daily summary
                            </p>
                        </div>

                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginBottom: "16px" }}>
                            {[
                                { label: "Daily Insight", sub: "AI tip from your activity", action: getInsight, loading: insightLoading },
                                { label: "Day Summary", sub: "Today's complete log", action: getSummary, loading: false },
                            ].map((item, i) => (
                                <button
                                    key={i}
                                    onClick={item.action}
                                    disabled={item.loading}
                                    style={{
                                        padding: "14px 16px",
                                        background: "#111113",
                                        border: "1px solid #1c1c1e",
                                        borderRadius: "12px",
                                        textAlign: "left",
                                        cursor: "pointer",
                                        opacity: item.loading ? 0.6 : 1,
                                        fontFamily: "inherit",
                                        transition: "border-color 0.1s",
                                    }}
                                    onMouseEnter={e => e.currentTarget.style.borderColor = "#2c2c2e"}
                                    onMouseLeave={e => e.currentTarget.style.borderColor = "#1c1c1e"}
                                >
                                    <div style={{ fontSize: "13px", fontWeight: "500", color: "#e0e0de", marginBottom: "3px" }}>
                                        {item.loading ? "Generating..." : item.label}
                                    </div>
                                    <div style={{ fontSize: "11px", color: "#4a4a52" }}>{item.sub}</div>
                                </button>
                            ))}
                        </div>

                        {insight && (
                            <div style={{
                                background: "#111113", border: "1px solid #1c1c1e",
                                borderRadius: "12px", padding: "16px", marginBottom: "10px",
                                fontSize: "13.5px", color: "#d0d0ce", lineHeight: "1.7",
                                whiteSpace: "pre-wrap",
                            }}>
                                {insight}
                            </div>
                        )}

                        {summary && (
                            <div style={{
                                background: "#111113", border: "1px solid #1c1c1e",
                                borderRadius: "12px", padding: "16px", marginBottom: "10px",
                                fontSize: "12px", color: "#a0a09e", lineHeight: "1.8",
                                whiteSpace: "pre-wrap", fontFamily: "monospace",
                            }}>
                                {summary}
                            </div>
                        )}

                        {patterns.length > 0 && (
                            <div>
                                <div style={{
                                    fontSize: "11px", color: "#4a4a52",
                                    letterSpacing: "0.06em", textTransform: "uppercase",
                                    marginBottom: "8px",
                                }}>
                                    Detected Patterns
                                </div>
                                {patterns.map((p, i) => (
                                    <div key={i} style={{
                                        display: "flex", gap: "10px",
                                        padding: "10px 14px", marginBottom: "4px",
                                        background: "#111113", border: "1px solid #1a1a1c",
                                        borderRadius: "8px", fontSize: "13px", color: "#8a8a92",
                                    }}>
                                        <span style={{ color: "#2a2a2e" }}>—</span>
                                        {p}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* -- proactive -- */}
                {activeTab === "proactive" && (
                    <div style={{ flex: 1, overflowY: "auto", padding: "24px", maxWidth: "720px" }}>
                        <div style={{ marginBottom: "24px" }}>
                            <h2 style={{ fontSize: "16px", fontWeight: "600", color: "#e8e8e6", marginBottom: "4px" }}>
                                Proactive Intelligence
                            </h2>
                            <p style={{ fontSize: "12px", color: "#4a4a52" }}>
                                Morning briefing · Nudges · Deadline warnings
                            </p>
                        </div>

                        <ProactivePanel />
                    </div>
                )}


            </div>

            <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { overflow: hidden; }
        input::placeholder, textarea::placeholder { color: #3a3a42; }
        input[type="date"]::-webkit-calendar-picker-indicator { filter: invert(0.2); cursor: pointer; }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #2a2a2e; border-radius: 2px; }
        ::-webkit-scrollbar-thumb:hover { background: #3a3a42; }
      `}</style>
        </div>
    )
}
