"""
Tests for Chord class and chord operations.
"""

import pytest
from src.backend.models.chord import Chord, ChordRoot


def test_chord_creation():
    """Test basic chord creation"""
    chord = Chord(ChordRoot.C, "m7")
    assert chord.root == ChordRoot.C
    assert chord.suffix == "m7"
    assert chord.bass is None


def test_chord_transpose_up():
    """Test transposing chord up"""
    chord = Chord(ChordRoot.C, "maj7")
    transposed = chord.transpose(2)
    
    assert transposed.root == ChordRoot.D
    assert transposed.suffix == "maj7"


def test_chord_transpose_down():
    """Test transposing chord down"""
    chord = Chord(ChordRoot.G, "m")
    transposed = chord.transpose(-3)
    
    assert transposed.root == ChordRoot.E
    assert transposed.suffix == "m"


def test_chord_transpose_wrap_around():
    """Test transpose wrapping around octave"""
    chord = Chord(ChordRoot.B, "7")
    transposed = chord.transpose(2)
    
    assert transposed.root == ChordRoot.Cs
    assert transposed.suffix == "7"


def test_chord_to_string_sharp():
    """Test chord to string with sharp notation"""
    chord = Chord(ChordRoot.Cs, "m7b5")
    result = chord.to_string(prefer_sharp=True)
    
    assert result == "C#m7b5"


def test_chord_to_string_flat():
    """Test chord to string with flat notation"""
    chord = Chord(ChordRoot.Cs, "m7b5")
    result = chord.to_string(prefer_sharp=False)
    
    assert result == "Dbm7b5"


def test_slash_chord():
    """Test slash chord (chord with bass note)"""
    chord = Chord(ChordRoot.C, "", ChordRoot.G)
    result = chord.to_string()
    
    assert result == "C/G"


def test_slash_chord_transpose():
    """Test transposing slash chord"""
    chord = Chord(ChordRoot.C, "maj7", ChordRoot.E)
    transposed = chord.transpose(2)
    
    assert transposed.root == ChordRoot.D
    assert transposed.bass == ChordRoot.Fs
    assert transposed.suffix == "maj7"


def test_chord_from_string_simple():
    """Test parsing simple chord"""
    chord = Chord.from_string("Am")
    
    assert chord is not None
    assert chord.root == ChordRoot.A
    assert chord.suffix == "m"


def test_chord_from_string_complex():
    """Test parsing complex chord"""
    chord = Chord.from_string("Dmaj7")
    
    assert chord is not None
    assert chord.root == ChordRoot.D
    assert chord.suffix == "maj7"


def test_chord_from_string_slash():
    """Test parsing slash chord"""
    chord = Chord.from_string("C/G")
    
    assert chord is not None
    assert chord.root == ChordRoot.C
    assert chord.bass == ChordRoot.G


def test_chord_from_string_sharp():
    """Test parsing chord with sharp"""
    chord = Chord.from_string("F#m7")
    
    assert chord is not None
    assert chord.root == ChordRoot.Fs
    assert chord.suffix == "m7"


def test_chord_root_sharp_name():
    """Test ChordRoot sharp name property"""
    assert ChordRoot.Cs.sharp_name == "C#"
    assert ChordRoot.Fs.sharp_name == "F#"
    assert ChordRoot.C.sharp_name == "C"


def test_chord_root_flat_name():
    """Test ChordRoot flat name property"""
    assert ChordRoot.Cs.flat_name == "Db"
    assert ChordRoot.Fs.flat_name == "Gb"
    assert ChordRoot.C.flat_name == "C"


def test_chord_root_from_string():
    """Test parsing ChordRoot from string"""
    assert ChordRoot.from_string("C") == ChordRoot.C
    assert ChordRoot.from_string("C#") == ChordRoot.Cs
    assert ChordRoot.from_string("Db") == ChordRoot.Cs
    assert ChordRoot.from_string("F#") == ChordRoot.Fs
    assert ChordRoot.from_string("Gb") == ChordRoot.Fs


def test_complex_chords():
    """Test complex chord parsing"""
    test_cases = [
        ("C#m7b5", ChordRoot.Cs, "m7b5", None),
        ("Bbmaj7", ChordRoot.As, "maj7", None),
        ("F#m/E", ChordRoot.Fs, "m", ChordRoot.E),
        ("Db7/Ab", ChordRoot.Cs, "7", ChordRoot.Gs),
        ("Asus4", ChordRoot.A, "sus4", None),
        ("Cadd9", ChordRoot.C, "add9", None),
    ]
    
    for chord_str, expected_root, expected_suffix, expected_bass in test_cases:
        chord = Chord.from_string(chord_str)
        assert chord is not None, f"Failed to parse {chord_str}"
        assert chord.root == expected_root, f"Wrong root for {chord_str}"
        assert chord.suffix == expected_suffix, f"Wrong suffix for {chord_str}"
        assert chord.bass == expected_bass, f"Wrong bass for {chord_str}"


def test_chord_transpose_preserves_suffix():
    """Test that transposition preserves chord suffix"""
    complex_chords = ["Cm7b5", "Fmaj7", "Asus4", "Gadd9"]
    
    for chord_str in complex_chords:
        chord = Chord.from_string(chord_str)
        transposed = chord.transpose(5)
        
        # Suffix should be preserved
        assert chord.suffix == transposed.suffix, f"Suffix changed for {chord_str}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

