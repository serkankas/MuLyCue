"""
REST API routes for MuLyCue.
Handles song management, file uploads, and playback control.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import List, Optional
import shutil
import json

from ..models import Song, MLCFormat
from ..core import AudioEngine

router = APIRouter(prefix="/api", tags=["api"])

# Global state (in production, use proper state management)
SONGS_DIR = Path("data/songs")
SONGS_DIR.mkdir(parents=True, exist_ok=True)

# Audio engine instance
audio_engine = AudioEngine()
current_song: Optional[Song] = None


@router.get("/songs")
async def list_songs():
    """
    List all available songs.
    
    Returns:
        List of song metadata
    """
    songs = []
    
    for mlc_file in SONGS_DIR.glob("*.mlc"):
        try:
            mlc_data = MLCFormat.load_from_file(str(mlc_file))
            songs.append({
                "id": mlc_file.stem,
                "title": mlc_data["meta"]["title"],
                "artist": mlc_data["meta"]["artist"],
                "duration": mlc_data["meta"]["duration"],
                "bpm": mlc_data["meta"]["bpm"],
                "key": mlc_data["meta"]["key"]
            })
        except Exception as e:
            print(f"Error loading {mlc_file}: {e}")
    
    return {"songs": songs}


@router.get("/songs/{song_id}")
async def get_song(song_id: str, transpose: int = 0):
    """
    Get song details by ID.
    
    Args:
        song_id: Song ID (filename without extension)
        transpose: Transpose semitones (optional)
        
    Returns:
        Complete song data
    """
    mlc_file = SONGS_DIR / f"{song_id}.mlc"
    
    if not mlc_file.exists():
        raise HTTPException(status_code=404, detail="Song not found")
    
    try:
        mlc_data = MLCFormat.load_from_file(str(mlc_file))
        song = Song(mlc_data, transpose=transpose)
        return song.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading song: {str(e)}")


@router.post("/songs")
async def create_song(
    mlc_file: UploadFile = File(...),
    audio_file: Optional[UploadFile] = File(None)
):
    """
    Upload a new song.
    
    Args:
        mlc_file: .mlc file
        audio_file: Optional MP3/audio file
        
    Returns:
        Created song metadata
    """
    # Validate .mlc file
    if not mlc_file.filename.endswith('.mlc'):
        raise HTTPException(status_code=400, detail="File must be .mlc format")
    
    try:
        # Read and validate .mlc content
        content = await mlc_file.read()
        mlc_data = json.loads(content)
        is_valid, error = MLCFormat.validate_mlc_data(mlc_data)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid .mlc file: {error}")
        
        # Save .mlc file
        song_id = Path(mlc_file.filename).stem
        mlc_path = SONGS_DIR / mlc_file.filename
        
        with open(mlc_path, 'wb') as f:
            f.write(content)
        
        # Save audio file if provided
        if audio_file:
            audio_path = SONGS_DIR / audio_file.filename
            with open(audio_path, 'wb') as f:
                shutil.copyfileobj(audio_file.file, f)
            
            # Update .mlc with audio file reference
            mlc_data["meta"]["audio_file"] = audio_file.filename
            MLCFormat.save_to_file(mlc_data, str(mlc_path))
        
        return {
            "id": song_id,
            "title": mlc_data["meta"]["title"],
            "message": "Song uploaded successfully"
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in .mlc file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading song: {str(e)}")


@router.put("/songs/{song_id}")
async def update_song(song_id: str, mlc_data: dict):
    """
    Update song data.
    
    Args:
        song_id: Song ID
        mlc_data: Updated .mlc data
        
    Returns:
        Success message
    """
    mlc_file = SONGS_DIR / f"{song_id}.mlc"
    
    if not mlc_file.exists():
        raise HTTPException(status_code=404, detail="Song not found")
    
    try:
        # Validate data
        is_valid, error = MLCFormat.validate_mlc_data(mlc_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid .mlc data: {error}")
        
        # Save updated data
        MLCFormat.save_to_file(mlc_data, str(mlc_file))
        
        return {"message": "Song updated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating song: {str(e)}")


@router.delete("/songs/{song_id}")
async def delete_song(song_id: str):
    """
    Delete a song.
    
    Args:
        song_id: Song ID
        
    Returns:
        Success message
    """
    mlc_file = SONGS_DIR / f"{song_id}.mlc"
    
    if not mlc_file.exists():
        raise HTTPException(status_code=404, detail="Song not found")
    
    try:
        # Delete .mlc file
        mlc_file.unlink()
        
        # Delete associated audio file if exists
        mlc_data = MLCFormat.load_from_file(str(mlc_file))
        audio_file = mlc_data["meta"].get("audio_file")
        if audio_file:
            audio_path = SONGS_DIR / audio_file
            if audio_path.exists():
                audio_path.unlink()
        
        return {"message": "Song deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting song: {str(e)}")


@router.post("/songs/{song_id}/transpose")
async def transpose_song(song_id: str, semitones: int):
    """
    Get transposed version of a song.
    
    Args:
        song_id: Song ID
        semitones: Number of semitones to transpose
        
    Returns:
        Transposed song data
    """
    mlc_file = SONGS_DIR / f"{song_id}.mlc"
    
    if not mlc_file.exists():
        raise HTTPException(status_code=404, detail="Song not found")
    
    try:
        mlc_data = MLCFormat.load_from_file(str(mlc_file))
        song = Song(mlc_data, transpose=semitones)
        return song.to_dict()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transposing song: {str(e)}")


@router.post("/playback/load")
async def load_song(song_id: str):
    """
    Load a song for playback.
    
    Args:
        song_id: Song ID
        
    Returns:
        Success message
    """
    global current_song
    
    mlc_file = SONGS_DIR / f"{song_id}.mlc"
    
    if not mlc_file.exists():
        raise HTTPException(status_code=404, detail="Song not found")
    
    try:
        mlc_data = MLCFormat.load_from_file(str(mlc_file))
        current_song = Song(mlc_data)
        
        # Load audio file if exists
        audio_file = mlc_data["meta"].get("audio_file")
        if audio_file:
            audio_path = SONGS_DIR / audio_file
            if audio_path.exists():
                audio_engine.load(str(audio_path))
        
        return {"message": "Song loaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading song: {str(e)}")


@router.post("/playback/play")
async def play():
    """Start playback."""
    try:
        audio_engine.play()
        return {"message": "Playback started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting playback: {str(e)}")


@router.post("/playback/pause")
async def pause():
    """Pause playback."""
    try:
        audio_engine.pause()
        return {"message": "Playback paused"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error pausing playback: {str(e)}")


@router.post("/playback/stop")
async def stop():
    """Stop playback."""
    try:
        audio_engine.stop()
        return {"message": "Playback stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping playback: {str(e)}")


@router.post("/playback/seek")
async def seek(position: float):
    """
    Seek to position.
    
    Args:
        position: Position in seconds
    """
    try:
        audio_engine.seek(position)
        return {"message": f"Seeked to {position}s"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error seeking: {str(e)}")


@router.get("/playback/status")
async def get_playback_status():
    """Get current playback status."""
    return {
        "is_playing": audio_engine.is_playing(),
        "is_paused": audio_engine.is_paused(),
        "position": audio_engine.get_position(),
        "duration": audio_engine.get_duration()
    }

