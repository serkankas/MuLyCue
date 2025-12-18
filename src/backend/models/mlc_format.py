"""
MLC file format parser and writer for MuLyCue.
Handles reading and writing .mlc files (JSON-based format).
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
import aiofiles


class MLCFormat:
    """
    Handler for .mlc file format.
    Provides methods to read, write, and validate .mlc files.
    """
    
    VERSION = "1.0.0"
    
    @staticmethod
    def validate_mlc_data(data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate .mlc file data structure.
        
        Args:
            data: Parsed .mlc data
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check version
        if "version" not in data:
            return False, "Missing 'version' field"
        
        # Check meta
        if "meta" not in data:
            return False, "Missing 'meta' field"
        
        meta = data["meta"]
        required_meta_fields = ["title", "bpm", "key", "duration"]
        for field in required_meta_fields:
            if field not in meta:
                return False, f"Missing required meta field: {field}"
        
        # Check sections
        if "sections" not in data:
            return False, "Missing 'sections' field"
        
        if not isinstance(data["sections"], list):
            return False, "'sections' must be a list"
        
        # Validate each section
        for i, section in enumerate(data["sections"]):
            if "name" not in section:
                return False, f"Section {i} missing 'name'"
            if "start_time" not in section:
                return False, f"Section {i} missing 'start_time'"
            if "end_time" not in section:
                return False, f"Section {i} missing 'end_time'"
            if "entries" not in section:
                return False, f"Section {i} missing 'entries'"
            
            # Validate entries
            for j, entry in enumerate(section["entries"]):
                if "start_time" not in entry:
                    return False, f"Section {i}, entry {j} missing 'start_time'"
                if "end_time" not in entry:
                    return False, f"Section {i}, entry {j} missing 'end_time'"
        
        return True, None
    
    @staticmethod
    def load_from_file(file_path: str) -> Dict[str, Any]:
        """
        Load .mlc file synchronously.
        
        Args:
            file_path: Path to .mlc file
            
        Returns:
            Parsed .mlc data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
            ValueError: If .mlc data is invalid
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        is_valid, error = MLCFormat.validate_mlc_data(data)
        if not is_valid:
            raise ValueError(f"Invalid .mlc file: {error}")
        
        return data
    
    @staticmethod
    async def load_from_file_async(file_path: str) -> Dict[str, Any]:
        """
        Load .mlc file asynchronously.
        
        Args:
            file_path: Path to .mlc file
            
        Returns:
            Parsed .mlc data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
            ValueError: If .mlc data is invalid
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            content = await f.read()
            data = json.loads(content)
        
        is_valid, error = MLCFormat.validate_mlc_data(data)
        if not is_valid:
            raise ValueError(f"Invalid .mlc file: {error}")
        
        return data
    
    @staticmethod
    def save_to_file(data: dict, file_path: str) -> None:
        """
        Save .mlc data to file synchronously.
        
        Args:
            data: .mlc data to save
            file_path: Path to save file
            
        Raises:
            ValueError: If .mlc data is invalid
        """
        is_valid, error = MLCFormat.validate_mlc_data(data)
        if not is_valid:
            raise ValueError(f"Invalid .mlc data: {error}")
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    async def save_to_file_async(data: dict, file_path: str) -> None:
        """
        Save .mlc data to file asynchronously.
        
        Args:
            data: .mlc data to save
            file_path: Path to save file
            
        Raises:
            ValueError: If .mlc data is invalid
        """
        is_valid, error = MLCFormat.validate_mlc_data(data)
        if not is_valid:
            raise ValueError(f"Invalid .mlc data: {error}")
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        content = json.dumps(data, indent=2, ensure_ascii=False)
        async with aiofiles.open(path, 'w', encoding='utf-8') as f:
            await f.write(content)
    
    @staticmethod
    def create_empty_mlc(
        title: str = "Untitled",
        artist: str = "Unknown",
        bpm: int = 120,
        key: str = "C",
        time_signature: str = "4/4"
    ) -> dict:
        """
        Create an empty .mlc file structure.
        
        Args:
            title: Song title
            artist: Artist name
            bpm: Beats per minute
            key: Musical key
            time_signature: Time signature
            
        Returns:
            Empty .mlc data structure
        """
        return {
            "version": MLCFormat.VERSION,
            "meta": {
                "title": title,
                "artist": artist,
                "album": "",
                "year": None,
                "genre": "",
                "bpm": bpm,
                "key": key,
                "time_signature": time_signature,
                "transpose": 0,
                "capo": 0,
                "duration": 0.0,
                "audio_file": None,
                "prefer_notation": "sharp"
            },
            "sections": []
        }

