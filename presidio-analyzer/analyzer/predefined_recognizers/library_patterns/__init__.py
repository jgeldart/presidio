from .library_pattern_recognizer import LibraryPatternRecognizer

import os
from pathlib import Path
import json

def load_pattern_library(location=None):
    """
    Load a directory of library patterns
    """
    if location is None:
        location = os.path.dirname(__file__)

    # Load all JSON files from the location
    location_path = Path(location)
    library = [
        LibraryPatternRecognizer(
            json.loads(pattern_file.read_text(encoding="UTF-8"))
        ) for pattern_file in location_path.glob("*.json")
    ]

    return library
