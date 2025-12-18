"""
WebSocket connection manager for MuLyCue.
Manages multiple WebSocket connections and broadcasts messages to all clients.
"""

from fastapi import WebSocket
from typing import List, Dict, Any
import json
import asyncio


class WebSocketManager:
    """
    Manages WebSocket connections for real-time communication.
    Supports broadcasting to all connected clients.
    """
    
    def __init__(self):
        """Initialize WebSocket manager."""
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection to register
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket) -> None:
        """
        Unregister a WebSocket connection.
        
        Args:
            websocket: WebSocket connection to remove
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket) -> None:
        """
        Send a message to a specific client.
        
        Args:
            message: Message dict to send
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]) -> None:
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: Message dict to broadcast
        """
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_position(self, position: float) -> None:
        """
        Broadcast current playback position.
        
        Args:
            position: Current position in seconds
        """
        await self.broadcast({
            "type": "position_update",
            "position": position
        })
    
    async def broadcast_entry(self, entry: Dict[str, Any]) -> None:
        """
        Broadcast current entry (word/chord) change.
        
        Args:
            entry: Current entry dict
        """
        await self.broadcast({
            "type": "entry_change",
            "entry": entry
        })
    
    async def broadcast_section(self, section: Dict[str, Any]) -> None:
        """
        Broadcast section change.
        
        Args:
            section: Current section dict
        """
        await self.broadcast({
            "type": "section_change",
            "section": section
        })
    
    async def broadcast_beat(self, beat: int) -> None:
        """
        Broadcast beat tick.
        
        Args:
            beat: Beat number (1-4)
        """
        await self.broadcast({
            "type": "beat_tick",
            "beat": beat
        })
    
    async def broadcast_playback_state(self, state: str) -> None:
        """
        Broadcast playback state change (play, pause, stop).
        
        Args:
            state: Playback state ("playing", "paused", "stopped")
        """
        await self.broadcast({
            "type": "playback_state",
            "state": state
        })
    
    async def broadcast_song_loaded(self, song_data: Dict[str, Any]) -> None:
        """
        Broadcast that a new song has been loaded.
        
        Args:
            song_data: Song data dict
        """
        await self.broadcast({
            "type": "song_loaded",
            "song": song_data
        })
    
    def get_connection_count(self) -> int:
        """
        Get number of active connections.
        
        Returns:
            Number of active WebSocket connections
        """
        return len(self.active_connections)

