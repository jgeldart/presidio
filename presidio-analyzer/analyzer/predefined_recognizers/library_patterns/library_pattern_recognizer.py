from analyzer import Pattern
from analyzer import PatternRecognizer

from collections import defaultdict
import re

from py_expression_eval import Parser

PARSER = Parser()

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
                lhs, rhs = possible_checksum.split("==")
                check = {
                    "lhs": PARSER.parse(lhs),
                    "rhs": PARSER.parse(rhs)
                }
                if possible_sanitizer is not None:
                    check["sanitization_regex"] = re.compile("[{0}]".format(re.escape(possible_sanitizer)))

                checksums.append(check)
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
                    santized_pattern = check["sanitization_regex"].sub("", pattern_text)
                else:
                    santized_pattern = pattern_text

                variable_dict = { 'd{0}'.format(i):int(c) for i, c in enumerate(santized_pattern) if c.isdigit() }
                lhs = check["lhs"].evaluate(variable_dict)
                rhs = check["rhs"].evaluate(variable_dict)
                validated = validated or (lhs == rhs)
            return validated
        else:
            return None
