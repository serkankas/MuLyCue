"""
Queue Manager for MuLyCue.
Manages setlist playback with auto-advance functionality.
"""

from typing import Optional, Callable
from ..models.setlist import Setlist, SetlistSong
from .audio_engine import AudioEngine
from .websocket_manager import WebSocketManager
import asyncio
import random


class QueueManager:
    """
    Manages setlist playback with auto-advance.
    Coordinates between setlist, audio engine, and WebSocket.
    """
    
    def __init__(self, audio_engine: AudioEngine, ws_manager: WebSocketManager):
        """
        Initialize queue manager.
        
        Args:
            audio_engine: Audio playback engine
            ws_manager: WebSocket manager for broadcasting updates
        """
        self.audio_engine = audio_engine
        self.ws_manager = ws_manager
        self.setlist: Optional[Setlist] = None
        self.current_index: int = 0
        self.is_playing: bool = False
        self.auto_advance_task: Optional[asyncio.Task] = None
        self.shuffle_order: List[int] = []
        
    def load_setlist(self, setlist: Setlist) -> None:
        """
        Load a setlist.
        
        Args:
            setlist: Setlist to load
        """
        self.setlist = setlist
        self.current_index = 0
        self.is_playing = False
        
        # Setup shuffle order if enabled
        if setlist.settings.shuffle:
            self.shuffle_order = list(range(len(setlist.songs)))
            random.shuffle(self.shuffle_order)
        else:
            self.shuffle_order = []
        
        asyncio.create_task(self.broadcast_setlist_update())
    
    def get_actual_index(self, logical_index: int) -> int:
        """
        Get actual song index considering shuffle.
        
        Args:
            logical_index: Logical position in playback order
            
        Returns:
            Actual index in songs list
        """
        if self.shuffle_order:
            return self.shuffle_order[logical_index]
        return logical_index
    
    def get_current_song(self) -> Optional[SetlistSong]:
        """
        Get currently playing song.
        
        Returns:
            Current song or None
        """
        if not self.setlist or self.current_index >= len(self.setlist.songs):
            return None
        
        actual_index = self.get_actual_index(self.current_index)
        return self.setlist.songs[actual_index]
    
    def get_next_song(self) -> Optional[SetlistSong]:
        """
        Get next song in queue.
        
        Returns:
            Next song or None
        """
        if not self.setlist:
            return None
        
        next_index = self.current_index + 1
        
        if next_index >= len(self.setlist.songs):
            if self.setlist.settings.loop:
                actual_index = self.get_actual_index(0)
                return self.setlist.songs[actual_index]
            return None
        
        actual_index = self.get_actual_index(next_index)
        return self.setlist.songs[actual_index]
    
    def get_previous_song(self) -> Optional[SetlistSong]:
        """
        Get previous song in queue.
        
        Returns:
            Previous song or None
        """
        if not self.setlist or self.current_index == 0:
            return None
        
        prev_index = self.current_index - 1
        actual_index = self.get_actual_index(prev_index)
        return self.setlist.songs[actual_index]
    
    async def play_current(self) -> None:
        """Play current song in setlist."""
        current = self.get_current_song()
        if not current:
            return
        
        # TODO: Load .mlc file and start playback
        # For now, just mark as playing
        self.is_playing = True
        
        # Setup auto-advance if enabled
        if self.setlist and self.setlist.settings.auto_advance:
            self.auto_advance_task = asyncio.create_task(
                self._auto_advance_handler()
            )
        
        await self.broadcast_setlist_update()
    
    async def _auto_advance_handler(self) -> None:
        """Monitor playback and auto-advance when song ends."""
        try:
            while self.is_playing:
                # Check if song ended
                position = self.audio_engine.get_position()
                duration = self.audio_engine.get_duration()
                
                if duration > 0 and position >= duration - 0.5:  # 0.5s before end
                    # Broadcast countdown if enabled
                    if self.setlist and self.setlist.settings.countdown:
                        await self._countdown_handler()
                    
                    # Wait gap time
                    if self.setlist:
                        await asyncio.sleep(self.setlist.settings.gap_seconds)
                    
                    # Advance to next
                    await self.next_song()
                    break
                
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass
    
    async def _countdown_handler(self) -> None:
        """Show countdown during gap."""
        if not self.setlist:
            return
        
        gap_seconds = self.setlist.settings.gap_seconds
        next_song = self.get_next_song()
        
        for remaining in range(gap_seconds, 0, -1):
            await self.ws_manager.broadcast({
                'type': 'gap_countdown',
                'remaining': remaining,
                'next_song': next_song.dict() if next_song else None
            })
            await asyncio.sleep(1)
    
    async def next_song(self) -> None:
        """Skip to next song."""
        if not self.setlist:
            return
        
        # Cancel auto-advance task
        if self.auto_advance_task:
            self.auto_advance_task.cancel()
            self.auto_advance_task = None
        
        # Advance index
        self.current_index += 1
        
        # Handle loop
        if self.current_index >= len(self.setlist.songs):
            if self.setlist.settings.loop:
                self.current_index = 0
            else:
                # Setlist finished
                self.is_playing = False
                await self.ws_manager.broadcast({
                    'type': 'setlist_finished',
                    'message': 'All songs completed!',
                    'total_songs': len(self.setlist.songs)
                })
                return
        
        # Play next song
        await self.play_current()
    
    async def previous_song(self) -> None:
        """Go back to previous song."""
        if not self.setlist or self.current_index == 0:
            return
        
        if self.auto_advance_task:
            self.auto_advance_task.cancel()
            self.auto_advance_task = None
        
        self.current_index -= 1
        await self.play_current()
    
    async def jump_to_song(self, index: int) -> None:
        """
        Jump to specific song in setlist.
        
        Args:
            index: Target song index
        """
        if not self.setlist or index < 0 or index >= len(self.setlist.songs):
            return
        
        if self.auto_advance_task:
            self.auto_advance_task.cancel()
            self.auto_advance_task = None
        
        self.current_index = index
        await self.play_current()
    
    def stop(self) -> None:
        """Stop playback and cancel auto-advance."""
        self.is_playing = False
        
        if self.auto_advance_task:
            self.auto_advance_task.cancel()
            self.auto_advance_task = None
    
    def get_progress(self) -> dict:
        """
        Get setlist progress info.
        
        Returns:
            Progress dictionary
        """
        if not self.setlist:
            return {
                'current_index': 0,
                'total_songs': 0,
                'progress_percent': 0,
                'elapsed_time': 0,
                'total_time': 0,
                'remaining_songs': 0
            }
        
        # Calculate elapsed time
        elapsed_songs = self.setlist.songs[:self.current_index]
        elapsed_time = sum(song.duration for song in elapsed_songs)
        elapsed_gaps = self.current_index * self.setlist.settings.gap_seconds
        
        return {
            'current_index': self.current_index,
            'total_songs': len(self.setlist.songs),
            'progress_percent': int((self.current_index / len(self.setlist.songs)) * 100) if self.setlist.songs else 0,
            'elapsed_time': elapsed_time + elapsed_gaps,
            'total_time': self.setlist.total_duration,
            'remaining_songs': len(self.setlist.songs) - self.current_index - 1
        }
    
    async def broadcast_setlist_update(self) -> None:
        """Broadcast setlist state to all clients."""
        current_song = self.get_current_song()
        next_song = self.get_next_song()
        
        await self.ws_manager.broadcast({
            'type': 'setlist_update',
            'setlist_name': self.setlist.name if self.setlist else None,
            'current_song': current_song.dict() if current_song else None,
            'next_song': next_song.dict() if next_song else None,
            'progress': self.get_progress(),
            'settings': self.setlist.settings.dict() if self.setlist else {},
            'is_playing': self.is_playing
        })
    
    def get_setlist_info(self) -> dict:
        """
        Get complete setlist information.
        
        Returns:
            Setlist info dictionary
        """
        if not self.setlist:
            return {}
        
        return {
            'name': self.setlist.name,
            'description': self.setlist.description,
            'song_count': self.setlist.song_count,
            'total_duration': self.setlist.total_duration,
            'estimated_time': self.setlist.estimated_time,
            'settings': self.setlist.settings.dict(),
            'songs': [song.dict() for song in self.setlist.songs],
            'current_index': self.current_index,
            'is_playing': self.is_playing
        }

