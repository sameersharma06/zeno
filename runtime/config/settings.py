import os

ROOT        = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUNTIME_DIR = os.path.join(ROOT, "runtime")
DATA_DIR    = os.path.join(RUNTIME_DIR, "db")
DB_PATH     = os.path.join(RUNTIME_DIR, "db", "zeno.db")
CHROMA_PATH = os.path.join(RUNTIME_DIR, "db", "chroma")
LOGS_PATH   = os.path.join(RUNTIME_DIR, "logs")
NOTES_PATH  = os.path.expanduser("~/Notes")
AUDIO_IN    = os.path.join(RUNTIME_DIR, "db", "input.wav")
AUDIO_OUT   = os.path.join(RUNTIME_DIR, "db", "output.wav")

os.makedirs(LOGS_PATH, exist_ok=True)
