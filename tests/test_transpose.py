"""
Tests for transpose utility functions.
"""

import pytest
from src.backend.utils.transpose import (
    transpose_chord,
    transpose_key,
    semitones_between_keys
)


def test_transpose_chord_up():
    """Test transposing chord up"""
    result = transpose_chord("C", 2)
    assert result == "D"
    
    result = transpose_chord("Am", 3)
    assert result == "Cm"


def test_transpose_chord_down():
    """Test transposing chord down"""
    result = transpose_chord("G", -2)
    assert result == "F"
    
    result = transpose_chord("Em7", -5)
    assert result == "Bm7"


def test_transpose_chord_sharp_notation():
    """Test transpose with sharp notation"""
    result = transpose_chord("C", 1, prefer_sharp=True)
    assert result == "C#"


def test_transpose_chord_flat_notation():
    """Test transpose with flat notation"""
    result = transpose_chord("C", 1, prefer_sharp=False)
    assert result == "Db"


def test_transpose_key():
    """Test transposing key"""
    result = transpose_key("C", 2)
    assert result == "D"
    
    result = transpose_key("Am", 5)
    assert result == "Dm"


def test_semitones_between_keys():
    """Test calculating semitones between keys"""
    # C to D = 2 semitones
    assert semitones_between_keys("C", "D") == 2
    
    # C to G = 7 semitones (or -5, should prefer smaller)
    result = semitones_between_keys("C", "G")
    assert result == -5 or result == 7
    
    # C to C = 0 semitones
    assert semitones_between_keys("C", "C") == 0


def test_transpose_invalid_chord():
    """Test transposing invalid chord returns None"""
    result = transpose_chord("Invalid", 2)
    assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

