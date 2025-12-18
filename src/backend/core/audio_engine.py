"""
Audio engine for MuLyCue using pygame.mixer.
Handles MP3 playback, position tracking, and playback controls.
"""

import pygame
from pathlib import Path
from typing import Optional, Callable
import threading
import time


class AudioEngine:
    """
    Audio playback engine using pygame.mixer.
    Provides play, pause, stop, seek functionality and position tracking.
    """
    
    def __init__(self):
        """Initialize pygame mixer."""
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self._current_file: Optional[str] = None
        self._is_playing: bool = False
        self._is_paused: bool = False
        self._position: float = 0.0
        self._duration: float = 0.0
        self._position_callbacks: list[Callable[[float], None]] = []
        self._update_thread: Optional[threading.Thread] = None
        self._stop_update: bool = False
    
    def load(self, audio_file: str) -> None:
        """
        Load an audio file.
        
        Args:
            audio_file: Path to audio file (MP3, OGG, WAV)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            pygame.error: If file format is not supported
        """
        path = Path(audio_file)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        # Stop current playback
        self.stop()
        
        # Load new file
        pygame.mixer.music.load(str(path))
        self._current_file = audio_file
        self._position = 0.0
        
        # Get duration using mutagen
        try:
            from mutagen.mp3 import MP3
            from mutagen.oggvorbis import OggVorbis
            from mutagen.wave import WAVE
            
            # Try different formats
            try:
                audio = MP3(str(path))
                self._duration = audio.info.length
            except:
                try:
                    audio = OggVorbis(str(path))
                    self._duration = audio.info.length
                except:
                    try:
                        audio = WAVE(str(path))
                        self._duration = audio.info.length
                    except:
                        print(f"Warning: Could not detect audio format for duration")
                        self._duration = 0.0
        except Exception as e:
            print(f"Warning: Could not get audio duration: {e}")
            self._duration = 0.0
    
    def play(self) -> None:
        """Start or resume playback."""
        if self._current_file is None:
            raise RuntimeError("No audio file loaded")
        
        if self._is_paused:
            pygame.mixer.music.unpause()
            self._is_paused = False
        else:
            pygame.mixer.music.play(start=self._position)
        
        self._is_playing = True
        self._start_position_tracking()
    
    def pause(self) -> None:
        """Pause playback."""
        if self._is_playing and not self._is_paused:
            pygame.mixer.music.pause()
            self._is_paused = True
            self._is_playing = False
            self._stop_position_tracking()
    
    def stop(self) -> None:
        """Stop playback and reset position."""
        self._stop_position_tracking()  # Stop tracking FIRST
        pygame.mixer.music.stop()
        self._is_playing = False
        self._is_paused = False
        self._position = 0.0
    
    def seek(self, position: float) -> None:
        """
        Seek to a specific position in seconds.
        
        NOTE: pygame.mixer doesn't support reliable seeking.
        This will be implemented in v2.0 with python-vlc backend.
        
        Args:
            position: Position in seconds
            
        Raises:
            NotImplementedError: Seeking not supported in current version
        """
        raise NotImplementedError(
            "Seeking is not yet supported with current audio backend. "
            "This feature will be available in version 2.0 with VLC backend."
        )
    
    def get_position(self) -> float:
        """
        Get current playback position in seconds.
        
        Returns:
            Current position in seconds
        """
        if self._is_playing:
            # pygame.mixer.music.get_pos() returns milliseconds since start
            elapsed = pygame.mixer.music.get_pos() / 1000.0
            return self._position + elapsed
        return self._position
    
    def get_duration(self) -> float:
        """
        Get audio file duration in seconds.
        
        Returns:
            Duration in seconds
        """
        return self._duration
    
    def set_volume(self, volume: float) -> None:
        """
        Set playback volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(volume)
    
    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return self._is_playing
    
    def is_paused(self) -> bool:
        """Check if audio is paused."""
        return self._is_paused
    
    def add_position_callback(self, callback: Callable[[float], None]) -> None:
        """
        Add a callback that will be called with current position periodically.
        
        Args:
            callback: Function that takes position (float) as argument
        """
        self._position_callbacks.append(callback)
    
    def remove_position_callback(self, callback: Callable[[float], None]) -> None:
        """
        Remove a position callback.
        
        Args:
            callback: Callback function to remove
        """
        if callback in self._position_callbacks:
            self._position_callbacks.remove(callback)
    
    def _start_position_tracking(self) -> None:
        """Start position tracking thread."""
        if self._update_thread is None or not self._update_thread.is_alive():
            self._stop_update = False
            self._update_thread = threading.Thread(target=self._position_update_loop, daemon=True)
            self._update_thread.start()
    
    def _stop_position_tracking(self) -> None:
        """Stop position tracking thread."""
        self._stop_update = True
    
    def _position_update_loop(self) -> None:
        """Position tracking loop (runs in separate thread)."""
        while not self._stop_update and self._is_playing:
            current_pos = self.get_position()
            
            # Call all registered callbacks
            for callback in self._position_callbacks:
                try:
                    callback(current_pos)
                except Exception as e:
                    print(f"Error in position callback: {e}")
            
            # Update every 50ms
            time.sleep(0.05)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop()
        pygame.mixer.quit()

