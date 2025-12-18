"""
Chord transposition utilities for MuLyCue.
"""

from ..models.chord import Chord, ChordRoot
from typing import Optional


def transpose_chord(chord_str: str, semitones: int, prefer_sharp: bool = True) -> Optional[str]:
    """
    Transpose a chord string by semitones.
    
    Args:
        chord_str: Chord string (e.g., "Am7", "Fmaj7")
        semitones: Number of semitones to transpose
        prefer_sharp: Use sharp notation if True, flat if False
        
    Returns:
        Transposed chord string or None if parsing fails
    """
    chord = Chord.from_string(chord_str)
    if chord is None:
        return None
    
    transposed = chord.transpose(semitones)
    return transposed.to_string(prefer_sharp)


def transpose_key(key: str, semitones: int, prefer_sharp: bool = True) -> Optional[str]:
    """
    Transpose a key by semitones.
    
    Args:
        key: Key string (e.g., "C", "Am", "F#")
        semitones: Number of semitones to transpose
        prefer_sharp: Use sharp notation if True, flat if False
        
    Returns:
        Transposed key string or None if parsing fails
    """
    # Keys can be like "C" (major) or "Am" (minor)
    # Use chord transposition logic
    return transpose_chord(key, semitones, prefer_sharp)


def semitones_between_keys(from_key: str, to_key: str) -> Optional[int]:
    """
    Calculate semitones between two keys.
    
    Args:
        from_key: Starting key
        to_key: Target key
        
    Returns:
        Number of semitones or None if parsing fails
    """
    from_chord = Chord.from_string(from_key)
    to_chord = Chord.from_string(to_key)
    
    if from_chord is None or to_chord is None:
        return None
    
    # Calculate difference
    diff = to_chord.root.value - from_chord.root.value
    
    # Normalize to -6 to +6 range (prefer smaller intervals)
    if diff > 6:
        diff -= 12
    elif diff < -6:
        diff += 12
    
    return diff

