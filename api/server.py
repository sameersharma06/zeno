import sys
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="Zeno AI", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import your routes
try:
    from api.routes import router
    app.include_router(router, prefix="/api")
    print("✅ Loaded API routes")
except ImportError as e:
    print(f"⚠️ Could not load routes: {e}")
    # Create basic routes if import fails
    @app.get("/api/health")
    async def health():
        return {"status": "healthy", "version": "2.0.0"}
    
    @app.get("/api/test")
    async def test():
        return {"message": "Zeno API is working"}

# Serve frontend from single port
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(BASE_DIR, "frontend/dist")

if os.path.exists(DIST):
    # Serve static assets
    assets_path = os.path.join(DIST, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
        print("✅ Static assets mounted")
    
    # Serve index.html for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_ui(full_path: str):
        if full_path.startswith("api/"):
            return None  # Let API routes handle it
        
        index_path = os.path.join(DIST, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        
        return {"error": "Frontend not built", "path": full_path}

else:
    print("⚠️ Frontend dist not found at:", DIST)
    @app.get("/")
    async def root():
        return {"message": "Zeno Backend Running", "frontend": "Not built"}

# Health check endpoint (always available)
@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "zeno", "version": "2.0.0"}

if __name__ == "__main__":
    print("🚀 Starting Zeno on http://localhost:8000")
    print("📁 Frontend: http://localhost:8000")
    print("🔧 API: http://localhost:8000/api/health")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
