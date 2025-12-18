"""
Timing and BPM calculation utilities for MuLyCue.
"""


def bpm_to_beat_duration(bpm: int) -> float:
    """
    Convert BPM to beat duration in seconds.
    
    Args:
        bpm: Beats per minute
        
    Returns:
        Duration of one beat in seconds
    """
    return 60.0 / bpm


def beat_duration_to_bpm(duration: float) -> int:
    """
    Convert beat duration to BPM.
    
    Args:
        duration: Duration of one beat in seconds
        
    Returns:
        Beats per minute
    """
    return int(60.0 / duration)


def time_to_beats(time: float, bpm: int) -> float:
    """
    Convert time in seconds to number of beats.
    
    Args:
        time: Time in seconds
        bpm: Beats per minute
        
    Returns:
        Number of beats
    """
    beat_duration = bpm_to_beat_duration(bpm)
    return time / beat_duration


def beats_to_time(beats: float, bpm: int) -> float:
    """
    Convert number of beats to time in seconds.
    
    Args:
        beats: Number of beats
        bpm: Beats per minute
        
    Returns:
        Time in seconds
    """
    beat_duration = bpm_to_beat_duration(bpm)
    return beats * beat_duration


def time_to_measures(time: float, bpm: int, time_signature: tuple[int, int] = (4, 4)) -> float:
    """
    Convert time to number of measures.
    
    Args:
        time: Time in seconds
        bpm: Beats per minute
        time_signature: Time signature as (beats_per_measure, beat_unit)
        
    Returns:
        Number of measures
    """
    beats = time_to_beats(time, bpm)
    beats_per_measure = time_signature[0]
    return beats / beats_per_measure


def format_time(seconds: float) -> str:
    """
    Format time in seconds to MM:SS format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string (MM:SS)
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def format_time_ms(seconds: float) -> str:
    """
    Format time in seconds to MM:SS.mmm format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string (MM:SS.mmm)
    """
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"

