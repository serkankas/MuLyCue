"""
Chord handling system for MuLyCue.
Supports chord parsing, transposition, and notation conversion.
"""

from enum import Enum
from typing import Optional
import re


class ChordRoot(Enum):
    """12 semitones as enum for easy transposition"""
    C = 0
    Cs = 1   # C# / Db
    D = 2
    Ds = 3   # D# / Eb
    E = 4
    F = 5
    Fs = 6   # F# / Gb
    G = 7
    Gs = 8   # G# / Ab
    A = 9
    As = 10  # A# / Bb
    B = 11
    
    @property
    def sharp_name(self) -> str:
        """Return sharp notation (C#, D#, etc.)"""
        return self.name.replace('s', '#')
    
    @property
    def flat_name(self) -> str:
        """Return flat notation (Db, Eb, etc.)"""
        flats = {
            'Cs': 'Db', 'Ds': 'Eb', 'Fs': 'Gb',
            'Gs': 'Ab', 'As': 'Bb'
        }
        return flats.get(self.name, self.name)
    
    @classmethod
    def from_string(cls, note_str: str) -> Optional['ChordRoot']:
        """
        Parse a note string to ChordRoot.
        Accepts both sharp (#) and flat (b) notation.
        
        Args:
            note_str: Note string like "C", "C#", "Db", etc.
            
        Returns:
            ChordRoot enum or None if invalid
        """
        note_str = note_str.strip().upper()
        
        # Map of note strings to ChordRoot
        note_map = {
            'C': cls.C,
            'C#': cls.Cs, 'DB': cls.Cs,
            'D': cls.D,
            'D#': cls.Ds, 'EB': cls.Ds,
            'E': cls.E,
            'F': cls.F,
            'F#': cls.Fs, 'GB': cls.Fs,
            'G': cls.G,
            'G#': cls.Gs, 'AB': cls.Gs,
            'A': cls.A,
            'A#': cls.As, 'BB': cls.As,
            'B': cls.B,
        }
        
        return note_map.get(note_str)


class Chord:
    """
    Represents a musical chord with root, suffix, and optional bass note.
    Supports transposition while preserving chord quality.
    
    Examples:
        - C, Am, G7, Fmaj7, Dm7b5
        - Slash chords: C/G, Am/E
    """
    
    def __init__(
        self,
        root: ChordRoot,
        suffix: str = "",  # "m", "7", "maj7", "m7b5", etc.
        bass: Optional[ChordRoot] = None  # For slash chords like C/G
    ):
        """
        Initialize a chord.
        
        Args:
            root: The root note of the chord
            suffix: Chord quality/type (m, 7, maj7, etc.)
            bass: Optional bass note for slash chords
        """
        self.root = root
        self.suffix = suffix
        self.bass = bass
    
    def transpose(self, semitones: int) -> 'Chord':
        """
        Transpose chord by semitones.
        Only root and bass notes change, suffix preserved.
        
        Args:
            semitones: Number of semitones to transpose (positive = up, negative = down)
            
        Returns:
            New transposed Chord object
        """
        new_root_value = (self.root.value + semitones) % 12
        new_root = ChordRoot(new_root_value)
        
        new_bass = None
        if self.bass:
            new_bass_value = (self.bass.value + semitones) % 12
            new_bass = ChordRoot(new_bass_value)
        
        return Chord(new_root, self.suffix, new_bass)
    
    def to_string(self, prefer_sharp: bool = True) -> str:
        """
        Convert chord to string notation.
        
        Args:
            prefer_sharp: If True, use sharp notation (C#), else flat (Db)
            
        Returns:
            String representation of the chord
        """
        root_name = (self.root.sharp_name if prefer_sharp 
                    else self.root.flat_name)
        result = root_name + self.suffix
        
        if self.bass:
            bass_name = (self.bass.sharp_name if prefer_sharp 
                        else self.bass.flat_name)
            result += f"/{bass_name}"
        
        return result
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        return f"Chord({self.root.name}, '{self.suffix}', {self.bass.name if self.bass else None})"
    
    @classmethod
    def from_string(cls, chord_str: str) -> Optional['Chord']:
        """
        Parse chord from string notation.
        
        Examples: "C", "Am7", "Fmaj7", "G/B", "C#m7b5"
        
        Args:
            chord_str: String representation of chord
            
        Returns:
            Chord object or None if parsing fails
        """
        if not chord_str or not isinstance(chord_str, str):
            return None
        
        chord_str = chord_str.strip()
        
        # Pattern: [Root][#/b]?[suffix]?[/bass]?
        # Examples: C, C#, Db, Am, Fmaj7, C/G, C#m7/G#
        pattern = r'^([A-G][#b]?)([^/]*?)(?:/([A-G][#b]?))?$'
        match = re.match(pattern, chord_str)
        
        if not match:
            return None
        
        root_str, suffix, bass_str = match.groups()
        
        # Parse root
        root = ChordRoot.from_string(root_str)
        if root is None:
            return None
        
        # Parse bass (if exists)
        bass = None
        if bass_str:
            bass = ChordRoot.from_string(bass_str)
            if bass is None:
                return None
        
        return cls(root, suffix or "", bass)

