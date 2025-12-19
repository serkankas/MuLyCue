"""
Tests for Setlist models and functionality.
"""

import pytest
from datetime import datetime
from src.backend.models.setlist import Setlist, SetlistSong, SetlistSettings


def test_setlist_song_creation():
    """Test creating a setlist song"""
    song = SetlistSong(
        id="test_song",
        title="Test Song",
        artist="Test Artist",
        duration=180.0,
        notes="Capo 2",
        transpose=2,
        key="C",
        bpm=120
    )
    
    assert song.id == "test_song"
    assert song.title == "Test Song"
    assert song.artist == "Test Artist"
    assert song.duration == 180.0
    assert song.notes == "Capo 2"
    assert song.transpose == 2
    assert song.key == "C"
    assert song.bpm == 120


def test_setlist_settings_defaults():
    """Test default setlist settings"""
    settings = SetlistSettings()
    
    assert settings.auto_advance is True
    assert settings.gap_seconds == 5
    assert settings.loop is False
    assert settings.shuffle is False
    assert settings.countdown is True


def test_setlist_creation():
    """Test creating a setlist"""
    setlist = Setlist(
        name="Test Gig",
        description="Test setlist",
        tags=["test", "venue"]
    )
    
    assert setlist.name == "Test Gig"
    assert setlist.description == "Test setlist"
    assert setlist.tags == ["test", "venue"]
    assert len(setlist.songs) == 0


def test_setlist_add_song():
    """Test adding song to setlist"""
    setlist = Setlist(name="Test Gig")
    
    song = SetlistSong(
        id="song1",
        title="Song 1",
        artist="Artist 1",
        duration=180.0
    )
    
    setlist.add_song(song)
    
    assert len(setlist.songs) == 1
    assert setlist.songs[0].id == "song1"


def test_setlist_add_song_at_index():
    """Test adding song at specific index"""
    setlist = Setlist(name="Test Gig")
    
    song1 = SetlistSong(id="song1", title="Song 1", artist="Artist", duration=180.0)
    song2 = SetlistSong(id="song2", title="Song 2", artist="Artist", duration=180.0)
    song3 = SetlistSong(id="song3", title="Song 3", artist="Artist", duration=180.0)
    
    setlist.add_song(song1)
    setlist.add_song(song3)
    setlist.add_song(song2, index=1)  # Insert in middle
    
    assert setlist.songs[0].id == "song1"
    assert setlist.songs[1].id == "song2"
    assert setlist.songs[2].id == "song3"


def test_setlist_remove_song():
    """Test removing song from setlist"""
    setlist = Setlist(name="Test Gig")
    
    song1 = SetlistSong(id="song1", title="Song 1", artist="Artist", duration=180.0)
    song2 = SetlistSong(id="song2", title="Song 2", artist="Artist", duration=180.0)
    
    setlist.add_song(song1)
    setlist.add_song(song2)
    
    removed = setlist.remove_song(0)
    
    assert removed.id == "song1"
    assert len(setlist.songs) == 1
    assert setlist.songs[0].id == "song2"


def test_setlist_move_song():
    """Test moving song in setlist"""
    setlist = Setlist(name="Test Gig")
    
    song1 = SetlistSong(id="song1", title="Song 1", artist="Artist", duration=180.0)
    song2 = SetlistSong(id="song2", title="Song 2", artist="Artist", duration=180.0)
    song3 = SetlistSong(id="song3", title="Song 3", artist="Artist", duration=180.0)
    
    setlist.add_song(song1)
    setlist.add_song(song2)
    setlist.add_song(song3)
    
    setlist.move_song(0, 2)  # Move first to last
    
    assert setlist.songs[0].id == "song2"
    assert setlist.songs[1].id == "song3"
    assert setlist.songs[2].id == "song1"


def test_setlist_total_duration():
    """Test calculating total duration"""
    setlist = Setlist(name="Test Gig")
    setlist.settings.gap_seconds = 5
    
    song1 = SetlistSong(id="song1", title="Song 1", artist="Artist", duration=180.0)
    song2 = SetlistSong(id="song2", title="Song 2", artist="Artist", duration=240.0)
    song3 = SetlistSong(id="song3", title="Song 3", artist="Artist", duration=200.0)
    
    setlist.add_song(song1)
    setlist.add_song(song2)
    setlist.add_song(song3)
    
    # Total: 180 + 240 + 200 = 620 seconds (songs)
    # Gaps: 2 gaps * 5 seconds = 10 seconds
    # Total: 630 seconds
    assert setlist.total_duration == 630.0


def test_setlist_estimated_time():
    """Test estimated time formatting"""
    setlist = Setlist(name="Test Gig")
    setlist.settings.gap_seconds = 0
    
    song = SetlistSong(id="song1", title="Song 1", artist="Artist", duration=3600.0)  # 1 hour
    setlist.add_song(song)
    
    # Should show "1h 0m" or "60 minutes"
    estimated = setlist.estimated_time
    assert ("1h" in estimated) or ("60 minutes" in estimated)


def test_setlist_song_count():
    """Test song count property"""
    setlist = Setlist(name="Test Gig")
    
    assert setlist.song_count == 0
    
    song1 = SetlistSong(id="song1", title="Song 1", artist="Artist", duration=180.0)
    song2 = SetlistSong(id="song2", title="Song 2", artist="Artist", duration=180.0)
    
    setlist.add_song(song1)
    setlist.add_song(song2)
    
    assert setlist.song_count == 2


def test_setlist_get_song():
    """Test getting song by index"""
    setlist = Setlist(name="Test Gig")
    
    song1 = SetlistSong(id="song1", title="Song 1", artist="Artist", duration=180.0)
    song2 = SetlistSong(id="song2", title="Song 2", artist="Artist", duration=180.0)
    
    setlist.add_song(song1)
    setlist.add_song(song2)
    
    assert setlist.get_song(0).id == "song1"
    assert setlist.get_song(1).id == "song2"
    assert setlist.get_song(2) is None  # Out of bounds


def test_setlist_clear():
    """Test clearing all songs"""
    setlist = Setlist(name="Test Gig")
    
    song1 = SetlistSong(id="song1", title="Song 1", artist="Artist", duration=180.0)
    song2 = SetlistSong(id="song2", title="Song 2", artist="Artist", duration=180.0)
    
    setlist.add_song(song1)
    setlist.add_song(song2)
    
    assert len(setlist.songs) == 2
    
    setlist.clear()
    
    assert len(setlist.songs) == 0


def test_setlist_duplicate():
    """Test duplicating setlist"""
    original = Setlist(
        name="Original Gig",
        description="Original description",
        tags=["test"]
    )
    
    song = SetlistSong(id="song1", title="Song 1", artist="Artist", duration=180.0)
    original.add_song(song)
    
    duplicate = original.duplicate("Duplicate Gig")
    
    assert duplicate.name == "Duplicate Gig"
    assert duplicate.description == original.description
    assert len(duplicate.songs) == len(original.songs)
    assert duplicate.songs[0].id == original.songs[0].id
    assert duplicate.tags == original.tags


def test_setlist_gap_seconds_validation():
    """Test gap_seconds validation"""
    settings = SetlistSettings(gap_seconds=30)
    assert settings.gap_seconds == 30
    
    # Test bounds (0-60)
    settings_min = SetlistSettings(gap_seconds=0)
    assert settings_min.gap_seconds == 0
    
    settings_max = SetlistSettings(gap_seconds=60)
    assert settings_max.gap_seconds == 60


def test_setlist_json_serialization():
    """Test setlist JSON serialization"""
    setlist = Setlist(
        name="Test Gig",
        description="Test description"
    )
    
    song = SetlistSong(
        id="song1",
        title="Song 1",
        artist="Artist 1",
        duration=180.0
    )
    
    setlist.add_song(song)
    
    # Test that it can be serialized to JSON
    json_data = setlist.model_dump_json()
    assert json_data is not None
    assert "Test Gig" in json_data
    assert "Song 1" in json_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

