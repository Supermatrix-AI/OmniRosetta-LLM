"""Meta HybridBot ensemble forecaster."""
from __future__ import annotations

from typing import Iterable, List


class MetaHybridBot:
    """Combine multiple models by median aggregation."""

    def aggregate(self, forecasts: Iterable[Iterable[float]]) -> List[float]:
        series = [list(model) for model in forecasts]
        if not series:
            return []
        length = len(series[0])
        if any(len(model) != length for model in series):
            raise ValueError("All model forecasts must have the same length")

        aggregated: List[float] = []
        for idx in range(length):
            snapshot = sorted(model[idx] for model in series)
            mid = len(snapshot) // 2
            if len(snapshot) % 2 == 1:
                aggregated.append(snapshot[mid])
            else:
                aggregated.append((snapshot[mid - 1] + snapshot[mid]) / 2)
        return aggregated


__all__ = ["MetaHybridBot"]
