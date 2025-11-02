"""Image feature processing helpers for glyph analysis."""
from __future__ import annotations

from typing import Iterable, List


def normalize_scores(scores: Iterable[float]) -> List[float]:
    values = list(scores)
    total = sum(values)
    if total == 0:
        return [0.0 for _ in values]
    return [value / total for value in values]


__all__ = ["normalize_scores"]
