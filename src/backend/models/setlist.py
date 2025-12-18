"""
Setlist/Queue models for MuLyCue.
Professional setlist management for live performances.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SetlistSong(BaseModel):
    """Song entry in a setlist"""
    id: str = Field(..., description="Reference to .mlc file")
    title: str
    artist: str
    duration: float = Field(..., description="Duration in seconds")
    notes: Optional[str] = Field(None, description="Performance notes (capo, tuning, etc.)")
    transpose: int = Field(0, description="Override song transpose")
    key: Optional[str] = Field(None, description="Song key")
    bpm: Optional[int] = Field(None, description="Song BPM")


class SetlistSettings(BaseModel):
    """Setlist playback settings"""
    auto_advance: bool = Field(True, description="Auto-advance to next song when current ends")
    gap_seconds: int = Field(5, ge=0, le=60, description="Gap between songs in seconds")
    loop: bool = Field(False, description="Loop setlist when finished")
    shuffle: bool = Field(False, description="Shuffle playback order")
    countdown: bool = Field(True, description="Show countdown during gap")


class Setlist(BaseModel):
    """Setlist/Queue model for live performances"""
    version: str = "1.0.0"
    name: str = Field(..., description="Setlist name (e.g., 'Coffee Shop Gig')")
    description: Optional[str] = Field(None, description="Setlist description")
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
    settings: SetlistSettings = Field(default_factory=SetlistSettings)
    songs: List[SetlistSong] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list, description="Tags for organization (venue, genre, etc.)")
    
    @property
    def total_duration(self) -> float:
        """
        Calculate total duration including gaps.
        
        Returns:
            Total duration in seconds
        """
        if not self.songs:
            return 0.0
        
        song_time = sum(song.duration for song in self.songs)
        gap_time = (len(self.songs) - 1) * self.settings.gap_seconds if len(self.songs) > 1 else 0
        return song_time + gap_time
    
    @property
    def estimated_time(self) -> str:
        """
        Human-readable time estimate.
        
        Returns:
            Formatted time string (e.g., "45 minutes")
        """
        total_seconds = self.total_duration
        minutes = int(total_seconds / 60)
        seconds = int(total_seconds % 60)
        
        if minutes > 60:
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours}h {minutes}m"
        elif seconds > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{minutes} minutes"
    
    @property
    def song_count(self) -> int:
        """Get number of songs in setlist."""
        return len(self.songs)
    
    def move_song(self, from_index: int, to_index: int) -> None:
        """
        Reorder songs in setlist.
        
        Args:
            from_index: Current position of song
            to_index: Target position for song
        """
        if 0 <= from_index < len(self.songs) and 0 <= to_index < len(self.songs):
            song = self.songs.pop(from_index)
            self.songs.insert(to_index, song)
            self.modified_at = datetime.now()
    
    def remove_song(self, index: int) -> Optional[SetlistSong]:
        """
        Remove song from setlist.
        
        Args:
            index: Position of song to remove
            
        Returns:
            Removed song or None if index invalid
        """
        if 0 <= index < len(self.songs):
            self.modified_at = datetime.now()
            return self.songs.pop(index)
        return None
    
    def add_song(self, song: SetlistSong, index: Optional[int] = None) -> None:
        """
        Add song to setlist.
        
        Args:
            song: Song to add
            index: Position to insert (None = append to end)
        """
        if index is None:
            self.songs.append(song)
        else:
            self.songs.insert(index, song)
        self.modified_at = datetime.now()
    
    def get_song(self, index: int) -> Optional[SetlistSong]:
        """
        Get song at specific index.
        
        Args:
            index: Position of song
            
        Returns:
            Song or None if index invalid
        """
        if 0 <= index < len(self.songs):
            return self.songs[index]
        return None
    
    def clear(self) -> None:
        """Remove all songs from setlist."""
        self.songs.clear()
        self.modified_at = datetime.now()
    
    def duplicate(self, new_name: str) -> 'Setlist':
        """
        Create a duplicate of this setlist.
        
        Args:
            new_name: Name for the duplicated setlist
            
        Returns:
            New Setlist instance
        """
        return Setlist(
            name=new_name,
            description=self.description,
            settings=self.settings.copy(),
            songs=self.songs.copy(),
            tags=self.tags.copy()
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Coffee Shop Gig",
                "description": "Acoustic set for downtown venue",
                "settings": {
                    "auto_advance": True,
                    "gap_seconds": 5,
                    "loop": False,
                    "shuffle": False
                },
                "songs": [
                    {
                        "id": "wonderwall.mlc",
                        "title": "Wonderwall",
                        "artist": "Oasis",
                        "duration": 225,
                        "notes": "Capo 2, drop D tuning"
                    }
                ]
            }
        }

