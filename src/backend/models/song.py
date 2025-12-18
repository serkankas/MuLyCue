"""
Song class for MuLyCue.
Handles .mlc file data with runtime transpose, BPM override, and key changes.
"""

from typing import List, Dict, Optional, Any
from .chord import Chord
import copy


class Song:
    """
    Main song class that handles .mlc file data.
    Supports runtime transpose, BPM override, and key changes.
    """
    
    def __init__(
        self,
        mlc_data: dict,
        transpose: int = 0,
        bpm_override: Optional[int] = None,
        key_override: Optional[str] = None,
        capo: int = 0,
        prefer_notation: str = "sharp"
    ):
        """
        Initialize a Song from .mlc data.
        
        Args:
            mlc_data: Parsed .mlc file data (dict)
            transpose: Number of semitones to transpose
            bpm_override: Override BPM from file
            key_override: Override key from file
            capo: Capo position (added to transpose)
            prefer_notation: "sharp" or "flat" for chord display
        """
        self.meta = mlc_data.get("meta", {})
        self._original_sections = mlc_data.get("sections", [])
        self.prefer_notation = prefer_notation
        
        # Apply settings
        self._transpose = transpose + capo
        self._bpm = bpm_override or self.meta.get("bpm", 120)
        self._key = key_override or self.meta.get("key", "C")
        
        # Auto-transpose all chords
        self.sections = self._apply_transpose()
    
    def _apply_transpose(self) -> List[Dict]:
        """
        Transpose all chords in all sections.
        
        Returns:
            List of sections with transposed chords
        """
        if self._transpose == 0:
            return copy.deepcopy(self._original_sections)
        
        transposed_sections = []
        
        for section in self._original_sections:
            new_section = {
                "name": section["name"],
                "order": section["order"],
                "start_time": section["start_time"],
                "end_time": section["end_time"],
                "entries": []
            }
            
            for entry in section.get("entries", []):
                new_entry = {
                    "word": entry.get("word"),
                    "start_time": entry.get("start_time"),
                    "end_time": entry.get("end_time"),
                    "chords": self._transpose_chord_string(entry.get("chords"))
                }
                new_section["entries"].append(new_entry)
            
            transposed_sections.append(new_section)
        
        return transposed_sections
    
    def _transpose_chord_string(self, chord_str: Optional[str]) -> Optional[str]:
        """
        Transpose a chord string (may contain multiple chords separated by spaces).
        
        Args:
            chord_str: Chord string like "C" or "Am G7 F"
            
        Returns:
            Transposed chord string or None
        """
        if not chord_str:
            return None
        
        chords = chord_str.split()
        transposed_chords = []
        
        for chord_text in chords:
            chord = Chord.from_string(chord_text)
            if chord:
                transposed = chord.transpose(self._transpose)
                prefer_sharp = self.prefer_notation == "sharp"
                transposed_chords.append(transposed.to_string(prefer_sharp))
            else:
                # If parsing fails, keep original
                transposed_chords.append(chord_text)
        
        return " ".join(transposed_chords)
    
    @property
    def transpose(self) -> int:
        """Get current transpose value."""
        return self._transpose
    
    @transpose.setter
    def transpose(self, value: int):
        """
        Re-transpose all chords when transpose value changes.
        
        Args:
            value: New transpose value in semitones
        """
        self._transpose = value
        self.sections = self._apply_transpose()
    
    @property
    def bpm(self) -> int:
        """Get current BPM."""
        return self._bpm
    
    @bpm.setter
    def bpm(self, value: int):
        """
        Set BPM override.
        
        Args:
            value: New BPM value
        """
        self._bpm = value
    
    @property
    def key(self) -> str:
        """Get current key."""
        return self._key
    
    @key.setter
    def key(self, value: str):
        """
        Set key override.
        
        Args:
            value: New key (e.g., "C", "Am", "F#")
        """
        self._key = value
    
    @property
    def title(self) -> str:
        """Get song title."""
        return self.meta.get("title", "Untitled")
    
    @property
    def artist(self) -> str:
        """Get artist name."""
        return self.meta.get("artist", "Unknown")
    
    @property
    def duration(self) -> float:
        """Get song duration in seconds."""
        return self.meta.get("duration", 0.0)
    
    @property
    def audio_file(self) -> Optional[str]:
        """Get associated audio file path."""
        return self.meta.get("audio_file")
    
    def get_entry_at_time(self, time: float) -> Optional[Dict[str, Any]]:
        """
        Get the entry (word/chord) at a specific time.
        
        Args:
            time: Time in seconds
            
        Returns:
            Entry dict or None if not found
        """
        for section in self.sections:
            if section["start_time"] <= time <= section["end_time"]:
                for entry in section["entries"]:
                    if entry["start_time"] <= time <= entry["end_time"]:
                        return {
                            **entry,
                            "section": section["name"]
                        }
        return None
    
    def get_section_at_time(self, time: float) -> Optional[Dict[str, Any]]:
        """
        Get the section at a specific time.
        
        Args:
            time: Time in seconds
            
        Returns:
            Section dict or None if not found
        """
        for section in self.sections:
            if section["start_time"] <= time <= section["end_time"]:
                return section
        return None
    
    def to_dict(self) -> dict:
        """
        Convert song to dictionary format (for API responses).
        
        Returns:
            Dictionary representation of the song
        """
        return {
            "meta": {
                **self.meta,
                "bpm": self._bpm,
                "key": self._key,
                "transpose": self._transpose,
                "prefer_notation": self.prefer_notation
            },
            "sections": self.sections
        }

