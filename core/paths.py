"""
Platform-agnostic path handling for Zeno
"""
import os

def get_project_root():
    """Get absolute path to project root"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_data_dir():
    """Get platform-agnostic data directory"""
    root = get_project_root()
    data_dir = os.path.join(root, "runtime", "db")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_audio_paths():
    """Get audio file paths"""
    data_dir = get_data_dir()
    return {
        "audio_in": os.path.join(data_dir, "audio_in.wav"),
        "audio_out": os.path.join(data_dir, "audio_out.wav")
    }

def get_chroma_path():
    """Get ChromaDB path"""
    data_dir = get_data_dir()
    chroma_path = os.path.join(data_dir, "chroma")
    os.makedirs(chroma_path, exist_ok=True)
    return chroma_path

def get_notes_path():
    """Get user's notes directory"""
    return os.path.expanduser("~/Notes")
