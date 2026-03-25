# core/voice.py — voice input and output
import sounddevice as sd
import soundfile as sf
import numpy as np
import streamlit as st
from mlx_audio.stt.generate import generate_transcription
from mlx_audio.tts.utils import load_model
from runtime.config.settings import AUDIO_IN, AUDIO_OUT

@st.cache_resource
def _load_tts():
    return load_model("mlx-community/Kokoro-82M-bf16")

def record_audio(duration: int = 5, fs: int = 16000) -> str:
    try:
        audio = sd.rec(
            int(duration * fs), samplerate=fs, channels=1, dtype="float32"
        )
        sd.wait()
        sf.write(AUDIO_IN, audio, fs)
        return AUDIO_IN
    except Exception as e:
        raise RuntimeError(
            f"Mic error: {e}\n"
            "Fix: System Preferences → Privacy → Microphone → allow Terminal"
        )

def transcribe(audio_path: str) -> str:
    result = generate_transcription(
        model="mlx-community/whisper-large-v3-turbo-asr-fp16",
        audio=audio_path
    )
    text = result.text.strip()

    if not text:
        raise ValueError("No speech detected. Please speak clearly and try again.")

    words = text.split()
    if len(words) > 3:
        unique_words = set(w.lower() for w in words)
        if len(unique_words) / len(words) < 0.2:
            raise ValueError("No clear speech detected. Please speak clearly and try again.")

    hallucination_phrases = [
        "www.", "fema.gov", "thank you for watching",
        "please subscribe", "visit our website",
        "for more information"
    ]
    if any(phrase in text.lower() for phrase in hallucination_phrases):
        raise ValueError("No clear speech detected. Please speak clearly and try again.")

    return text

def speak(text: str) -> str:
    tts = _load_tts()
    chunks = []
    for result in tts.generate(text=text, voice="af_heart", speed=1.0, lang_code="a"):
        chunks.append(np.array(result.audio).astype(np.float32))
    full = np.concatenate(chunks) if len(chunks) > 1 else chunks[0]
    sf.write(AUDIO_OUT, full, 24000)
    return AUDIO_OUT


