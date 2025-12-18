"""
WebSocket endpoints for MuLyCue.
Provides real-time communication for playback sync.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..core import WebSocketManager
import json

router = APIRouter(tags=["websocket"])

# WebSocket manager instance
ws_manager = WebSocketManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication.
    
    Clients can connect to receive:
    - position_update: Current playback position
    - entry_change: Current word/chord entry
    - section_change: Current section
    - beat_tick: Beat events (1-4)
    - playback_state: Play/pause/stop events
    - song_loaded: New song loaded
    
    Clients can send:
    - play: Start playback
    - pause: Pause playback
    - stop: Stop playback
    - seek: Seek to position {"position": 10.5}
    - transpose: Change transpose {"semitones": 2}
    """
    await ws_manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                # Handle different message types
                if message_type == "ping":
                    await ws_manager.send_personal_message(
                        {"type": "pong"},
                        websocket
                    )
                
                elif message_type == "play":
                    # Trigger play (this would be handled by audio engine)
                    await ws_manager.broadcast_playback_state("playing")
                
                elif message_type == "pause":
                    await ws_manager.broadcast_playback_state("paused")
                
                elif message_type == "stop":
                    await ws_manager.broadcast_playback_state("stopped")
                
                elif message_type == "seek":
                    position = message.get("position", 0)
                    await ws_manager.broadcast_position(position)
                
                else:
                    await ws_manager.send_personal_message(
                        {"type": "error", "message": f"Unknown message type: {message_type}"},
                        websocket
                    )
            
            except json.JSONDecodeError:
                await ws_manager.send_personal_message(
                    {"type": "error", "message": "Invalid JSON"},
                    websocket
                )
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

