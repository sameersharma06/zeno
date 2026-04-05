import os
from core.paths import get_data_dir, get_chroma_path, get_notes_path, get_audio_paths

# Dynamic paths
DATA_DIR = get_data_dir()
DB_PATH = os.path.join(DATA_DIR, "zeno.db")
CHROMA_PATH = get_chroma_path()
LOGS_PATH = os.path.join(os.path.dirname(DATA_DIR), "logs")
NOTES_PATH = get_notes_path()

# Audio paths
audio_paths = get_audio_paths()
AUDIO_IN = audio_paths["audio_in"]
AUDIO_OUT = audio_paths["audio_out"]

# Ensure directories exist
os.makedirs(LOGS_PATH, exist_ok=True)
os.makedirs(NOTES_PATH, exist_ok=True)
