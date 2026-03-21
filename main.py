import subprocess
import sys
import os
import time
import webbrowser
from threading import Thread

ROOT = os.path.dirname(os.path.abspath(__file__))

def start_backend():
    os.chdir(ROOT)
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "api.server:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])

def start_frontend():
    os.chdir(os.path.join(ROOT, "frontend"))
    subprocess.run(["npm", "run", "dev"])

def open_browser():
    time.sleep(4)
    webbrowser.open("http://localhost:5173")

if __name__ == "__main__":
    print("🧠 Starting Zeno...")

    Thread(target=start_backend, daemon=True).start()
    Thread(target=start_frontend, daemon=True).start()
    Thread(target=open_browser, daemon=True).start()

    print("✅ Zeno is running at http://localhost:5173")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Zeno stopped.")
