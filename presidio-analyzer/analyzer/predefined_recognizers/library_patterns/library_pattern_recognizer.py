from analyzer import Pattern
from analyzer import PatternRecognizer

from collections import defaultdict
import re

import formulas

PARSER = formulas.Parser()
FUNCTIONS = formulas.get_functions()

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

        name = self._safe_get(library_pattern, "name")
        supported_entity = library_pattern["entity"]
        supported_language = self._safe_get(library_pattern, "language", default="en")

        patterns = []
        patterns = [Pattern(pattern["name"],
                            pattern["regex"],
                            pattern["score"])
                    for pattern in self._safe_get(library_pattern, "patterns", default=[])]

        # Build checksums
        checksums = []
        for pattern in self._safe_get(library_pattern, "patterns", default=[]):
            possible_checksum = self._safe_get(pattern, "checksum")
            possible_sanitizer = self._safe_get(pattern, "sanitizer")
            if possible_checksum is not None:
                try:
                    check = {
                        "formula": PARSER.ast("={0}".format(possible_checksum))[1].compile()
                    }
                    if possible_sanitizer is not None:
                        check["sanitization_regex"] = re.compile("[{0}]".format(re.escape(possible_sanitizer)))

                    checksums.append(check)
                except Exception as e:
                    pass

        self._checksums = checksums

        context_phrases = self._safe_get(library_pattern, "contextPhrases")
        black_list = self._safe_get(library_pattern, "blackList")

        super().__init__(name=name,
                            supported_entity=supported_entity,
                            supported_language=supported_language,
                            black_list=black_list,
                            patterns=patterns,
                            context=context_phrases)

    def _safe_get(self, pattern_dict, key, default=None):
        if key in pattern_dict.keys():
            return pattern_dict[key]
        else:
            return default

    def validate_result(self, pattern_text):
        """
        Run a checksum calculation if one is defined for the text
        """
        if len(self._checksums) != 0:
            validated = False
            for check in self._checksums:
                if "sanitization_regex" in check.keys():
                    sanitized_pattern = check["sanitization_regex"].sub("", pattern_text)
                else:
                    sanitized_pattern = pattern_text

                digit_sequence = [int(c) for c in sanitized_pattern]

                formula = check["formula"]

                prepared_inputs = [ self._prepare_input(input, digit_sequence) for input in formula.inputs ]
                result = formula(*prepared_inputs).item()

                validated = validated or result
            return validated
        else:
            return None

    def _prepare_input(self, input, digits):
        if ":" in input:
            start, end = input.split(":")
            return digits[(int(start[1:])-1):(int(end[1:]))]
        else:
            return digits[(int(input[1:])-1)]
