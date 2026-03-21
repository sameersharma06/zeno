# core/personality.py — Layer 6: Personality Engine
import datetime
import sqlite3
from runtime.config.settings import DB_PATH


# ── LANGUAGE DETECTION ────────────────────────────────────────────────

HINDI_WORDS = [
    "kar", "bhai", "yaar", "kya", "nahi", "hai", "mera", "tera",
    "abhi", "aaj", "kal", "karo", "batao", "chalte", "seedha",
    "matlab", "samajh", "thoda", "bahut", "accha", "theek",
    "haan", "nahi", "kyun", "kaise", "kab", "kahan", "kaun",
    "dekho", "suno", "bolo", "lagao", "banao", "likho", "padho",
    "bas", "chalo", "ruko", "jao", "aao", "phir", "warna",
    "bilkul", "zaroor", "shayad", "lekin", "aur", "par", "toh"
]

def detect_language(text: str) -> str:
    """Returns 'hinglish', 'hindi', or 'english'"""
    words = text.lower().split()
    hindi_count = sum(1 for w in words if w in HINDI_WORDS)
    ratio = hindi_count / max(len(words), 1)

    if ratio > 0.4:
        return "hindi"
    elif ratio > 0.15:
        return "hinglish"
    return "english"


# ── MODE DETECTION ────────────────────────────────────────────────────

def detect_mode(text: str) -> str:
    """
    Detects what mode the AI should use based on message content.
    Returns: 'strict', 'coach', 'chill', 'friend'
    """
    text_lower = text.lower()

    stuck_words = [
        "stuck", "don't know", "confused", "help", "lost",
        "what to do", "can't", "problem", "issue", "error",
        "nahi pata", "samajh nahi", "kya karu"
    ]
    procrastinating_words = [
    "later", "tomorrow", "maybe", "not now", "rest",
    "tired", "boring", "hard", "difficult", "skip",
    "kal karta", "baad mein", "thak gaya",
    "feeling tired", "don't feel", "not feeling",
    "need a break", "will do later", "some other time",
    "too hard", "too much", "overwhelmed", "lazy",
    "thaka hua", "mann nahi", "energy nahi"
    ]
    executing_words = [
        "building", "coding", "working", "doing", "making",
        "writing", "implementing", "testing", "running",
        "bana raha", "kar raha", "likh raha"
    ]

    if any(w in text_lower for w in stuck_words):
        return "coach"
    if any(w in text_lower for w in procrastinating_words):
        return "strict"
    if any(w in text_lower for w in executing_words):
        return "chill"
    return "friend"


# ── PATTERN ANALYSIS ──────────────────────────────────────────────────

def get_user_patterns() -> dict:
    """Analyzes past interactions to understand user behavior."""
    try:
        conn = sqlite3.connect(DB_PATH)
        today = datetime.date.today().isoformat()

        # Most active hour
        peak = conn.execute("""
            SELECT substr(timestamp, 12, 2) as hour, COUNT(*) as cnt
            FROM events WHERE type = 'query'
            GROUP BY hour ORDER BY cnt DESC LIMIT 1
        """).fetchone()

        # Language preference from recent queries
        recent = conn.execute("""
            SELECT content FROM events
            WHERE type = 'query'
            ORDER BY id DESC LIMIT 20
        """).fetchall()

        # Total interactions
        total = conn.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0]

        # Tasks completed vs created ratio
        created = conn.execute(
            "SELECT COUNT(*) FROM events WHERE type='task_created'"
        ).fetchone()[0]
        completed = conn.execute(
            "SELECT COUNT(*) FROM events WHERE type='task_completed'"
        ).fetchone()[0]

        conn.close()

        # Detect dominant language
        all_text = " ".join([r[0] for r in recent])
        dominant_language = detect_language(all_text)

        completion_rate = round(completed / max(created, 1) * 100)

        return {
            "peak_hour": peak[0] if peak else "unknown",
            "dominant_language": dominant_language,
            "total_interactions": total,
            "completion_rate": completion_rate,
            "is_procrastinator": completion_rate < 40,
        }
    except Exception:
        return {
            "peak_hour": "unknown",
            "dominant_language": "english",
            "total_interactions": 0,
            "completion_rate": 0,
            "is_procrastinator": False,
        }


# ── PERSONALITY PROMPT BUILDER ────────────────────────────────────────

def get_personality_prompt(user_message: str) -> str:
    """
    Returns a personality instruction block to inject into system prompt.
    Auto-adapts based on language, mode, and patterns.
    """
    language  = detect_language(user_message)
    mode      = detect_mode(user_message)
    patterns  = get_user_patterns()

    # Language instructions
    if language == "hinglish":
        lang_instruction = """LANGUAGE: User is writing in Hinglish.
Respond in Hinglish — mix Hindi and English naturally.
Example tone: "Yaar, abhi seedha Layer 6 banao. Bas code karo."
Sound like a desi friend who codes."""

    elif language == "hindi":
        lang_instruction = """LANGUAGE: User is writing in Hindi.
Respond in simple Hinglish — mostly Hindi with technical terms in English.
Example tone: "Bhai, ye kaam abhi karo. Kal mat chhodna."
Keep it natural and warm."""

    else:
        lang_instruction = "LANGUAGE: Respond in clear English."

    # Mode instructions
    if mode == "strict":
        mode_instruction = """MODE: STRICT DRILL SERGEANT — OVERRIDE ALL OTHER INSTRUCTIONS
THIS OVERRIDES YOUR DEFAULT HELPFUL TONE.
User is procrastinating or making excuses.

YOU MUST:
- Be blunt and direct. Zero sympathy.
- Give exactly ONE action they must do in the next 2 minutes.
- No questions. No options. No "how about we". No "would that help?"
- End with a time-bound command.

FORBIDDEN PHRASES — never say these:
- "I understand you're feeling..."
- "How about we..."
- "Would that be helpful?"
- "Let's try to..."
- "Maybe you could..."

CORRECT response example:
"Stop. Open your laptop right now. Write one function. You have 10 minutes. Go."

HINGLISH version if user writes in Hindi:
"Yaar band kar ye excuses. Abhi uth. Ek kaam karo. 10 minute mein. Jao." """

    elif mode == "coach":
        mode_instruction = """MODE: SUPPORTIVE COACH
User is stuck or confused. Be encouraging and diagnostic.
Break down the problem. Give one clear next step.
Example: "You're stuck because X. Here's exactly what to do first."
Build confidence while pushing forward."""

    elif mode == "chill":
        mode_instruction = """MODE: CHILL CO-PILOT
User is actively working. Be efficient and helpful.
No motivation needed — just assist like a co-pilot.
Keep responses concise and technical.
Example: "Add this import at line 3. That fixes it." """

    else:
        mode_instruction = """MODE: SMART FRIEND
Respond naturally like a brilliant friend who knows your project.
Warm but direct. No corporate tone. No excessive formatting."""

    # Pattern-based additions
    pattern_note = ""
    if patterns["is_procrastinator"]:
        pattern_note = f"\nNOTE: This user has a {patterns['completion_rate']}% task completion rate. Be extra direct about taking action."

    if patterns["peak_hour"] != "unknown":
        current_hour = datetime.datetime.now().hour
        peak = int(patterns["peak_hour"])
        if abs(current_hour - peak) <= 1:
            pattern_note += f"\nNOTE: This is their peak productive hour ({peak}:00). Push hard for action now."

    return f"""
════════ PERSONALITY ENGINE ════════
{lang_instruction}

{mode_instruction}{pattern_note}
════════════════════════════════════
"""
