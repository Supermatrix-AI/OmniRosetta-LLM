"""Scenario-based forecasting heuristics."""
from __future__ import annotations

from typing import Dict, Iterable


class OraculusVantarium:
    """Allocates probabilities across qualitative scenarios."""

    def normalize(self, scenarios: Dict[str, float]) -> Dict[str, float]:
        total = sum(value for value in scenarios.values() if value > 0)
        if total == 0:
            return {name: 0.0 for name in scenarios}
        return {name: value / total for name, value in scenarios.items() if value > 0}

    def merge_weights(self, primary: Dict[str, float], adjustments: Iterable[Dict[str, float]]) -> Dict[str, float]:
        """Combine scenario weights and re-normalize the distribution."""

        combined: Dict[str, float] = dict(primary)
        for adjustment in adjustments:
            for name, weight in adjustment.items():
                combined[name] = combined.get(name, 0.0) + weight
        return self.normalize(combined)


__all__ = ["OraculusVantarium"]
