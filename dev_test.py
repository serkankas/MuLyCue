#!/usr/bin/env python3
"""
Quick development test script for MuLyCue.
Tests core functionality without starting full server.
"""

from src.backend.models.chord import Chord, ChordRoot
from src.backend.models.song import Song
from src.backend.models.mlc_format import MLCFormat
from pathlib import Path


def test_chord_system():
    """Test chord parsing and transposition"""
    print("=" * 50)
    print("Testing Chord System")
    print("=" * 50)
    
    test_chords = ["C", "Am7", "Fmaj7", "G/B", "C#m7b5", "Bb7"]
    
    for chord_str in test_chords:
        chord = Chord.from_string(chord_str)
        if chord:
            transposed = chord.transpose(2)
            print(f"{chord_str:10} → +2 semitones → {transposed}")
        else:
            print(f"{chord_str:10} → FAILED TO PARSE")
    
    print()


def test_song_loading():
    """Test song loading and transpose"""
    print("=" * 50)
    print("Testing Song Loading")
    print("=" * 50)
    
    sample_file = Path("examples/sample_song.mlc")
    if sample_file.exists():
        mlc_data = MLCFormat.load_from_file(str(sample_file))
        song = Song(mlc_data)
        
        print(f"Title: {song.title}")
        print(f"Artist: {song.artist}")
        print(f"BPM: {song.bpm}")
        print(f"Key: {song.key}")
        print(f"Duration: {song.duration}s")
        print(f"Sections: {len(song.sections)}")
        
        # Test transpose
        print("\nTransposing +3 semitones...")
        song.transpose = 3
        print(f"First section chords after transpose:")
        if song.sections:
            for entry in song.sections[0]["entries"][:3]:
                print(f"  {entry.get('word', '(no word)')}: {entry.get('chords')}")
    else:
        print(f"Sample file not found: {sample_file}")
    
    print()


def test_mlc_validation():
    """Test MLC format validation"""
    print("=" * 50)
    print("Testing MLC Format Validation")
    print("=" * 50)
    
    # Test valid MLC
    valid_mlc = MLCFormat.create_empty_mlc(
        title="Test Song",
        artist="Test Artist",
        bpm=120,
        key="C"
    )
    
    is_valid, error = MLCFormat.validate_mlc_data(valid_mlc)
    print(f"Empty MLC validation: {'✅ PASS' if is_valid else '❌ FAIL'}")
    if error:
        print(f"  Error: {error}")
    
    # Test invalid MLC
    invalid_mlc = {"invalid": "data"}
    is_valid, error = MLCFormat.validate_mlc_data(invalid_mlc)
    print(f"Invalid MLC validation: {'✅ PASS (correctly rejected)' if not is_valid else '❌ FAIL'}")
    if error:
        print(f"  Error: {error}")
    
    print()


def test_audio_engine():
    """Test audio engine initialization"""
    print("=" * 50)
    print("Testing Audio Engine")
    print("=" * 50)
    
    try:
        from src.backend.core.audio_engine import AudioEngine
        
        engine = AudioEngine()
        print("✅ Audio engine initialized successfully")
        
        # Test with sample file if exists
        sample_audio = Path("examples/sample.mp3")
        if sample_audio.exists():
            try:
                engine.load(str(sample_audio))
                print(f"✅ Audio file loaded: {engine.get_duration()}s")
            except Exception as e:
                print(f"⚠️  Could not load audio: {e}")
        else:
            print("ℹ️  No sample audio file found (examples/sample.mp3)")
        
        engine.cleanup()
    except Exception as e:
        print(f"❌ Audio engine error: {e}")
    
    print()


if __name__ == "__main__":
    print("\n🎵 MuLyCue Development Test Suite\n")
    
    test_chord_system()
    test_song_loading()
    test_mlc_validation()
    test_audio_engine()
    
    print("=" * 50)
    print("✅ Development tests complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("  1. Run full test suite: pytest")
    print("  2. Start dev server: ./run_dev.sh")
    print("  3. Open browser: http://localhost:8000")
    print()

