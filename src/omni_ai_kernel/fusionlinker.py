"""Data fusion helpers."""
from __future__ import annotations

from typing import Dict, Iterable


def fuse_scores(score_maps: Iterable[Dict[str, float]]) -> Dict[str, float]:
    """Aggregate scores from multiple engines by averaging."""

    totals: Dict[str, float] = {}
    counts: Dict[str, int] = {}
    for mapping in score_maps:
        for key, value in mapping.items():
            totals[key] = totals.get(key, 0.0) + value
            counts[key] = counts.get(key, 0) + 1
    return {key: totals[key] / counts[key] for key in totals}


__all__ = ["fuse_scores"]
