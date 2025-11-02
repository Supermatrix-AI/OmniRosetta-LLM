"""Metaculus Maverick: lightweight expert-override forecaster."""
from __future__ import annotations

from typing import Dict, Iterable


class MetaculusMaverick:
    """Combine crowd predictions with expert overrides using weighted averages."""

    def __init__(self, crowd_weight: float = 0.7) -> None:
        if not 0 <= crowd_weight <= 1:
            raise ValueError("crowd_weight must be between 0 and 1")
        self.crowd_weight = crowd_weight

    def blend(self, crowd: float, expert: float) -> float:
        """Blend crowd and expert forecasts."""

        return self.crowd_weight * crowd + (1 - self.crowd_weight) * expert

    def batch_blend(self, crowd_series: Iterable[float], expert_series: Iterable[float]) -> Dict[str, float]:
        """Blend sequences of forecasts and return summary statistics."""

        crowd_list = list(crowd_series)
        expert_list = list(expert_series)
        if len(crowd_list) != len(expert_list):
            raise ValueError("Series must have the same length")

        blended = [self.blend(c, e) for c, e in zip(crowd_list, expert_list)]
        if not blended:
            return {"mean": 0.0, "max": 0.0, "min": 0.0}
        return {"mean": sum(blended) / len(blended), "max": max(blended), "min": min(blended)}


__all__ = ["MetaculusMaverick"]
