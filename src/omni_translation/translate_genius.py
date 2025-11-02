"""Rule-based translation helper."""
from __future__ import annotations

from typing import Dict, Iterable, List


class TranslateGenius:
    """Perform dictionary-based translations with fallbacks."""

    def __init__(self, dictionary: Dict[str, str]) -> None:
        self.dictionary = dictionary

    def translate_tokens(self, tokens: Iterable[str]) -> List[str]:
        return [self.dictionary.get(token, token) for token in tokens]


__all__ = ["TranslateGenius"]
