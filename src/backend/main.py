"""
Main FastAPI application for MuLyCue.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import uvicorn

app = FastAPI(
    title="MuLyCue API",
    version="0.1.0",
    description="Music Lyrics & Chords Cue System API"
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get paths
BASE_DIR = Path(__file__).parent.parent.parent
FRONTEND_DIR = BASE_DIR / "src" / "frontend"

# Mount frontend static files
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# Include routers
from .api import routes, websocket
app.include_router(routes.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    """Root endpoint - serve index.html"""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "MuLyCue API v0.1.0", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/api/info")
async def info():
    """API information"""
    return {
        "name": "MuLyCue API",
        "version": "0.1.0",
        "description": "Music Lyrics & Chords Cue System",
        "endpoints": {
            "songs": "/api/songs",
            "playback": "/api/playback",
            "websocket": "/ws"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

