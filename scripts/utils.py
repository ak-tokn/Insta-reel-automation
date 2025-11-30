"""
Utility functions for StoicAlgo
Common helper functions used across modules.
"""

import os
import json
import random
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional


def load_json(filepath: str) -> Dict:
    """Load JSON file and return as dictionary."""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_json(data: Dict, filepath: str):
    """Save dictionary to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def load_settings() -> Dict:
    """Load the main settings file."""
    settings_path = Path(__file__).parent.parent / "config" / "settings.json"
    return load_json(settings_path)


def get_env_var(key: str, default: str = None) -> str:
    """Get environment variable with optional default."""
    value = os.environ.get(key, default)
    if value is None:
        raise ValueError(f"Environment variable {key} not set")
    return value


def ensure_dir(path: str) -> Path:
    """Ensure directory exists, create if not."""
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID for tracking."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_suffix = hashlib.md5(
        str(random.random()).encode()
    ).hexdigest()[:6]
    return f"{prefix}_{timestamp}_{random_suffix}" if prefix else f"{timestamp}_{random_suffix}"


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_file_list(directory: str, extensions: List[str] = None) -> List[Path]:
    """Get list of files in directory, optionally filtered by extension."""
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    
    files = []
    for f in dir_path.iterdir():
        if f.is_file():
            if extensions is None:
                files.append(f)
            elif f.suffix.lower() in extensions:
                files.append(f)
    
    return files


def weighted_random_choice(options: List[Any], weights: List[float]) -> Any:
    """Select from options based on weights."""
    return random.choices(options, weights=weights, k=1)[0]


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_filename(filename: str) -> str:
    """Clean a string to be safe for use as filename."""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    return filename.strip()


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


def wrap_text(text: str, max_width: int) -> List[str]:
    """Wrap text to fit within max width (character count)."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines


def get_timestamp_filename(prefix: str, extension: str) -> str:
    """Generate a filename with timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.{extension}"


class Timer:
    """Context manager for timing operations."""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, *args):
        self.elapsed = (datetime.now() - self.start_time).total_seconds()
    
    def __str__(self):
        if self.elapsed:
            return f"{self.name}: {format_duration(self.elapsed)}"
        return f"{self.name}: not completed"


if __name__ == "__main__":
    # Test utilities
    print("Project root:", get_project_root())
    print("Generated ID:", generate_id("test"))
    print("Timestamp filename:", get_timestamp_filename("video", "mp4"))
    
    # Test text wrapping
    test_text = "The impediment to action advances action. What stands in the way becomes the way."
    wrapped = wrap_text(test_text, 30)
    print("Wrapped text:")
    for line in wrapped:
        print(f"  {line}")
    
    # Test timer
    import time
    with Timer("Sleep test") as t:
        time.sleep(0.5)
    print(t)
