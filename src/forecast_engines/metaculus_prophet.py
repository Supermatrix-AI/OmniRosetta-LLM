"""Prophet-style trend decomposition placeholder."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence


def decompose_trend(series: Sequence[float]) -> List[float]:
    """Return a centered moving average trend component."""

    if len(series) < 3:
        return list(series)
    trend: List[float] = []
    for idx in range(1, len(series) - 1):
        trend.append(sum(series[idx - 1 : idx + 2]) / 3)
    return [series[0]] + trend + [series[-1]]


@dataclass
class ProphetForecast:
    trend: List[float]
    residual: List[float]


def prophet_forecast(series: Sequence[float]) -> ProphetForecast:
    """Return a naive trend/residual decomposition."""

    trend = decompose_trend(series)
    residual = [value - trend[idx] for idx, value in enumerate(series)]
    return ProphetForecast(trend=trend, residual=residual)


__all__ = ["prophet_forecast", "ProphetForecast", "decompose_trend"]
