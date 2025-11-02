"""Rule-inspired utilities for the Mahadevan Decoder module."""
from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List


def ngram_frequencies(sequence: Iterable[str], n: int = 2) -> Dict[str, int]:
    """Compute n-gram frequencies for a sequence of glyph tokens."""

    tokens = list(sequence)
    if n <= 0:
        raise ValueError("n must be positive")
    if len(tokens) < n:
        return {}

    counter: Counter[str] = Counter()
    for idx in range(len(tokens) - n + 1):
        ngram = "".join(tokens[idx : idx + n])
        counter[ngram] += 1
    return dict(counter)


def suggest_roots(tokens: Iterable[str], lexicon: Dict[str, str]) -> List[str]:
    """Suggest possible lexical roots from a lexicon mapping."""

    suggestions: List[str] = []
    for token in tokens:
        if token in lexicon:
            suggestions.append(lexicon[token])
    return suggestions


__all__ = ["ngram_frequencies", "suggest_roots"]
