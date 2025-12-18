"""
Sync engine for MuLyCue.
Handles timing synchronization between audio playback and lyrics/chords display.
"""

from typing import Optional, Callable, Dict, Any
from ..models.song import Song
import time


class SyncEngine:
    """
    Synchronization engine that coordinates audio playback with lyrics/chords display.
    Triggers callbacks when words, chords, sections, or beats change.
    """
    
    def __init__(self, song: Song):
        """
        Initialize sync engine with a song.
        
        Args:
            song: Song object to sync with
        """
        self.song = song
        self._current_position: float = 0.0
        self._current_entry: Optional[Dict[str, Any]] = None
        self._current_section: Optional[Dict[str, Any]] = None
        self._current_beat: int = 0
        self._last_beat_time: float = 0.0
        
        # Callbacks
        self._on_entry_change: Optional[Callable[[Dict[str, Any]], None]] = None
        self._on_section_change: Optional[Callable[[Dict[str, Any]], None]] = None
        self._on_beat: Optional[Callable[[int], None]] = None
    
    def update(self, position: float) -> None:
        """
        Update sync engine with current playback position.
        Should be called frequently (e.g., every 50ms).
        
        Args:
            position: Current playback position in seconds
        """
        self._current_position = position
        
        # Check for entry change
        entry = self.song.get_entry_at_time(position)
        if entry != self._current_entry:
            self._current_entry = entry
            if self._on_entry_change and entry:
                self._on_entry_change(entry)
        
        # Check for section change
        section = self.song.get_section_at_time(position)
        if section != self._current_section:
            self._current_section = section
            if self._on_section_change and section:
                self._on_section_change(section)
        
        # Check for beat
        self._update_beat(position)
    
    def _update_beat(self, position: float) -> None:
        """
        Update beat counter based on BPM.
        
        Args:
            position: Current position in seconds
        """
        beat_duration = 60.0 / self.song.bpm  # Duration of one beat in seconds
        
        # Calculate current beat
        current_beat = int(position / beat_duration) % 4  # Assuming 4/4 time
        
        # Check if beat changed
        if position - self._last_beat_time >= beat_duration:
            self._last_beat_time = position
            self._current_beat = (self._current_beat + 1) % 4
            
            if self._on_beat:
                self._on_beat(self._current_beat + 1)  # 1-indexed for display
    
    def set_on_entry_change(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Set callback for when current word/chord entry changes.
        
        Args:
            callback: Function that takes entry dict as argument
        """
        self._on_entry_change = callback
    
    def set_on_section_change(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Set callback for when current section changes.
        
        Args:
            callback: Function that takes section dict as argument
        """
        self._on_section_change = callback
    
    def set_on_beat(self, callback: Callable[[int], None]) -> None:
        """
        Set callback for beat events.
        
        Args:
            callback: Function that takes beat number (1-4) as argument
        """
        self._on_beat = callback
    
    def get_current_entry(self) -> Optional[Dict[str, Any]]:
        """Get current entry (word/chord)."""
        return self._current_entry
    
    def get_current_section(self) -> Optional[Dict[str, Any]]:
        """Get current section."""
        return self._current_section
    
    def get_current_beat(self) -> int:
        """Get current beat (1-4)."""
        return self._current_beat + 1
    
    def get_upcoming_entries(self, lookahead: float = 5.0) -> list[Dict[str, Any]]:
        """
        Get entries coming up within lookahead time.
        
        Args:
            lookahead: Time in seconds to look ahead
            
        Returns:
            List of upcoming entries
        """
        upcoming = []
        end_time = self._current_position + lookahead
        
        for section in self.song.sections:
            if section["start_time"] > end_time:
                break
            
            if section["end_time"] < self._current_position:
                continue
            
            for entry in section["entries"]:
                if self._current_position <= entry["start_time"] <= end_time:
                    upcoming.append({
                        **entry,
                        "section": section["name"]
                    })
        
        return upcoming
    
    def reset(self) -> None:
        """Reset sync engine state."""
        self._current_position = 0.0
        self._current_entry = None
        self._current_section = None
        self._current_beat = 0
        self._last_beat_time = 0.0

