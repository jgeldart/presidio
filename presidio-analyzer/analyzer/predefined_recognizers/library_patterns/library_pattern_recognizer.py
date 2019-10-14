from analyzer import Pattern
from analyzer import PatternRecognizer

from collections import defaultdict

class LibraryPatternRecognizer(PatternRecognizer):
    """
    Helper to construct a pattern recognizer from a dictionary
    obtained from a JSON file that is part of a pattern library.
    """

    def __init__(self, library_pattern=defaultdict()):
        """
        Uses the library pattern to initialize self as a
        pattern recognizer.
        """

        supported_entity = library_pattern["entity"]

        patterns = []
        if library_pattern["patterns"] is not None:
            patterns = [Pattern(pattern["name"],
                                pattern["regex"],
                                pattern["score"])
                        for pattern in library_pattern["patterns"]]

        context_phrases = library_pattern["contextPhrases"]
        super().__init__(supported_entity=supported_entity,
                            patterns=patterns,
                            context=context_phrases)
