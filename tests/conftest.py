"""
Pytest configuration and shared fixtures.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_chord_strings():
    """Fixture providing sample chord strings for testing"""
    return [
        "C", "Am", "F", "G",
        "C#m7", "Bbmaj7", "F#m/E",
        "Asus4", "Cadd9", "Dm7b5"
    ]


@pytest.fixture
def sample_setlist_song():
    """Fixture providing a sample setlist song"""
    from src.backend.models.setlist import SetlistSong
    
    return SetlistSong(
        id="test_song",
        title="Test Song",
        artist="Test Artist",
        duration=180.0,
        notes="Test notes",
        transpose=0,
        key="C",
        bpm=120
    )


@pytest.fixture
def sample_setlist():
    """Fixture providing a sample setlist"""
    from src.backend.models.setlist import Setlist, SetlistSong
    
    setlist = Setlist(
        name="Test Gig",
        description="Test setlist for unit tests",
        tags=["test", "unit"]
    )
    
    # Add some songs
    for i in range(1, 4):
        song = SetlistSong(
            id=f"song{i}",
            title=f"Song {i}",
            artist="Test Artist",
            duration=180.0 + (i * 20),
            key="C",
            bpm=120
        )
        setlist.add_song(song)
    
    return setlist


@pytest.fixture
def sample_chord():
    """Fixture providing a sample chord"""
    from src.backend.models.chord import Chord, ChordRoot
    
    return Chord(ChordRoot.C, "maj7")


@pytest.fixture
def mock_audio_file(tmp_path):
    """Fixture providing a mock audio file path"""
    audio_file = tmp_path / "test_song.mp3"
    audio_file.write_bytes(b"fake audio data")
    return str(audio_file)


@pytest.fixture
def mock_mlc_file(tmp_path):
    """Fixture providing a mock .mlc file"""
    import json
    
    mlc_data = {
        "version": "1.0.0",
        "meta": {
            "title": "Test Song",
            "artist": "Test Artist",
            "bpm": 120,
            "key": "C",
            "duration": 180.0,
            "audio_file": "test_song.mp3"
        },
        "sections": [
            {
                "name": "Verse 1",
                "entries": [
                    {
                        "timestamp": 0.0,
                        "word": "Test",
                        "chords": ["C"]
                    }
                ]
            }
        ]
    }
    
    mlc_file = tmp_path / "test_song.mlc"
    mlc_file.write_text(json.dumps(mlc_data, indent=2))
    return str(mlc_file)


@pytest.fixture
def mock_setlist_file(tmp_path):
    """Fixture providing a mock setlist file"""
    import json
    from datetime import datetime
    
    setlist_data = {
        "version": "1.0.0",
        "name": "Test Gig",
        "description": "Test setlist",
        "created_at": datetime.now().isoformat(),
        "settings": {
            "auto_advance": True,
            "gap_seconds": 5,
            "loop": False,
            "shuffle": False,
            "countdown": True
        },
        "songs": [
            {
                "id": "song1",
                "title": "Song 1",
                "artist": "Artist 1",
                "duration": 180.0,
                "notes": None,
                "transpose": 0,
                "key": "C",
                "bpm": 120
            }
        ],
        "tags": ["test"]
    }
    
    setlist_file = tmp_path / "test_gig.json"
    setlist_file.write_text(json.dumps(setlist_data, indent=2))
    return str(setlist_file)

