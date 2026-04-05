import sys
import os

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# Make project root importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")
INDEX_FILE = os.path.join(DIST_DIR, "index.html")

# Main app
app = FastAPI(title="Zeno AI", version="2.0.0")

# Load router from api.routes
try:
    from api.routes import router
    app.include_router(router)
    print("✅ Loaded API routes successfully")
except Exception as e:
    raise RuntimeError(f"❌ Failed to load routes: {e}") from e

# Serve frontend assets if build exists
if os.path.exists(DIST_DIR):
    assets_path = os.path.join(DIST_DIR, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
        print("✅ Static assets mounted")
    else:
        print(f"⚠️ Assets folder not found at: {assets_path}")
else:
    print(f"⚠️ Frontend not built at: {DIST_DIR}")

# Single-page app fallback
@app.get("/{full_path:path}")
async def serve_ui(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API route not found")

    if os.path.exists(INDEX_FILE):
        return FileResponse(INDEX_FILE)

    raise HTTPException(status_code=404, detail="Frontend not built")

if __name__ == "__main__":
    print("🚀 Starting Zeno on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

    