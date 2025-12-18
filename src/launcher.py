"""
Desktop launcher for MuLyCue.
Wraps the web application in a native window using PyWebView.
"""

import webview
import threading
import uvicorn
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.main import app


def start_api():
    """Start FastAPI backend in separate thread"""
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            access_log=False
        )
    except Exception as e:
        print(f"Error starting API: {e}")
        sys.exit(1)


def on_closing():
    """Handle window closing"""
    print("Closing MuLyCue...")


def main():
    """Main entry point for desktop application"""
    print("Starting MuLyCue...")
    
    # Start backend in separate thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # Give the server a moment to start
    import time
    time.sleep(2)
    
    # Create desktop window
    window = webview.create_window(
        title="MuLyCue - Music Lyrics & Chords Cue System",
        url="http://127.0.0.1:8000/",
        width=1280,
        height=800,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600),
        background_color='#0f172a'
    )
    
    # Start webview
    webview.start(debug=False)
    
    print("MuLyCue closed")


if __name__ == "__main__":
    main()

