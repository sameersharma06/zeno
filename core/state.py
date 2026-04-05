"""
Optimized project state detection for Zeno
"""

import os
import glob
import time

# ─────────────────────────────────────────
# CACHE (CRITICAL FIX)
# ─────────────────────────────────────────

_cached_state = None
_last_update = 0
CACHE_TTL = 10  # seconds


def get_full_state() -> str:
    global _cached_state, _last_update

    try:
        # ── RETURN CACHED STATE ──
        if _cached_state and (time.time() - _last_update < CACHE_TTL):
            return _cached_state

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # ── FILE SCAN (ONCE PER TTL) ──
        python_files = glob.glob(
            os.path.join(project_root, "**/*.py"),
            recursive=True
        )

        # ── DETECTIONS ──
        has_frontend = os.path.exists(os.path.join(project_root, "frontend/dist"))
        has_backend = os.path.exists(os.path.join(project_root, "api/server.py"))
        has_voice = os.path.exists(os.path.join(project_root, "core/voice.py"))
        has_memory = os.path.exists(os.path.join(project_root, "data"))
        has_agents = os.path.exists(os.path.join(project_root, "agents"))

        # ── STATE BUILD ──
        state_lines = []

        # Frontend
        if has_frontend:
            state_lines.append("✅ Frontend ready")
        else:
            state_lines.append("❌ Frontend not built")

        # Backend
        if has_backend:
            state_lines.append("✅ Backend API running")
        else:
            state_lines.append("❌ Backend missing")

        # Voice
        if has_voice:
            state_lines.append("✅ Voice system available")
        else:
            state_lines.append("❌ Voice system missing")

        # Memory
        if has_memory:
            state_lines.append("✅ Memory system present")
        else:
            state_lines.append("❌ Memory system missing")

        # Agents
        if has_agents:
            state_lines.append("✅ Agents configured")
        else:
            state_lines.append("❌ Agents not configured")

        # Codebase size
        file_count = len(python_files)
        if file_count > 80:
            state_lines.append(f"🚀 Advanced system ({file_count} modules)")
        elif file_count > 30:
            state_lines.append(f"🔄 Growing system ({file_count} modules)")
        else:
            state_lines.append(f"🚧 Early stage ({file_count} modules)")

        # ── FINAL FORMAT ──
        result = "\n".join([f"PROJECT STATE: {line}" for line in state_lines])

        # ── CACHE SAVE ──
        _cached_state = result
        _last_update = time.time()

        return result

    except Exception as e:
        return f"PROJECT STATE ERROR: {str(e)}"