"""
Tests for MLC file format handling.
"""

import pytest
import json
from pathlib import Path
from src.backend.models.mlc_format import MLCFormat


def test_create_empty_mlc():
    """Test creating empty MLC structure"""
    mlc = MLCFormat.create_empty_mlc(
        title="Test Song",
        artist="Test Artist",
        bpm=120,
        key="C"
    )
    
    assert mlc["version"] == "1.0.0"
    assert mlc["meta"]["title"] == "Test Song"
    assert mlc["meta"]["artist"] == "Test Artist"
    assert mlc["meta"]["bpm"] == 120
    assert mlc["meta"]["key"] == "C"
    assert mlc["sections"] == []


def test_validate_valid_mlc():
    """Test validating valid MLC data"""
    mlc = MLCFormat.create_empty_mlc()
    is_valid, error = MLCFormat.validate_mlc_data(mlc)
    
    assert is_valid is True
    assert error is None


def test_validate_missing_version():
    """Test validation fails with missing version"""
    mlc = {"meta": {}, "sections": []}
    is_valid, error = MLCFormat.validate_mlc_data(mlc)
    
    assert is_valid is False
    assert "version" in error


def test_validate_missing_meta():
    """Test validation fails with missing meta"""
    mlc = {"version": "1.0.0", "sections": []}
    is_valid, error = MLCFormat.validate_mlc_data(mlc)
    
    assert is_valid is False
    assert "meta" in error


def test_validate_missing_required_meta_field():
    """Test validation fails with missing required meta field"""
    mlc = {
        "version": "1.0.0",
        "meta": {
            "title": "Test"
            # Missing other required fields
        },
        "sections": []
    }
    is_valid, error = MLCFormat.validate_mlc_data(mlc)
    
    assert is_valid is False


def test_validate_invalid_sections():
    """Test validation fails with invalid sections"""
    mlc = MLCFormat.create_empty_mlc()
    mlc["sections"] = "not a list"
    
    is_valid, error = MLCFormat.validate_mlc_data(mlc)
    
    assert is_valid is False
    assert "list" in error


def test_validate_section_missing_fields():
    """Test validation fails with section missing required fields"""
    mlc = MLCFormat.create_empty_mlc()
    mlc["sections"] = [
        {
            "name": "Verse 1"
            # Missing other required fields
        }
    ]
    
    is_valid, error = MLCFormat.validate_mlc_data(mlc)
    
    assert is_valid is False


def test_save_and_load_mlc(tmp_path):
    """Test saving and loading MLC file"""
    # Create test data
    mlc = MLCFormat.create_empty_mlc(title="Test Song", artist="Test Artist")
    mlc["sections"] = [
        {
            "name": "Verse 1",
            "order": 1,
            "start_time": 0.0,
            "end_time": 10.0,
            "entries": [
                {
                    "word": "Test",
                    "start_time": 0.0,
                    "end_time": 1.0,
                    "chords": "C"
                }
            ]
        }
    ]
    
    # Save to file
    file_path = tmp_path / "test.mlc"
    MLCFormat.save_to_file(mlc, str(file_path))
    
    # Load from file
    loaded = MLCFormat.load_from_file(str(file_path))
    
    # Verify
    assert loaded["meta"]["title"] == "Test Song"
    assert loaded["meta"]["artist"] == "Test Artist"
    assert len(loaded["sections"]) == 1
    assert loaded["sections"][0]["name"] == "Verse 1"


def test_load_nonexistent_file():
    """Test loading non-existent file raises error"""
    with pytest.raises(FileNotFoundError):
        MLCFormat.load_from_file("nonexistent.mlc")


def test_save_invalid_mlc(tmp_path):
    """Test saving invalid MLC data raises error"""
    invalid_mlc = {"invalid": "data"}
    file_path = tmp_path / "invalid.mlc"
    
    with pytest.raises(ValueError):
        MLCFormat.save_to_file(invalid_mlc, str(file_path))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

