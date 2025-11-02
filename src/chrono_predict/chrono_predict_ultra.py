"""Time-series forecasting helpers for the Chrono Predict Ultra module."""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable, List, Sequence


@dataclass
class ForecastResult:
    """Simple container for forecasted values and diagnostics."""

    predictions: List[float]
    window: int

    def to_dict(self) -> dict[str, object]:
        return {"predictions": self.predictions, "window": self.window}


class ChronoPredictor:
    """Implements a lightweight moving-average forecaster."""

    def __init__(self, window: int = 3) -> None:
        if window <= 0:
            raise ValueError("Window must be positive")
        self.window = window

    def forecast(self, series: Sequence[float], horizon: int = 1) -> ForecastResult:
        """Generate a naive moving average forecast for the given horizon."""

        if horizon <= 0:
            raise ValueError("Horizon must be positive")
        if len(series) < self.window:
            raise ValueError("Not enough observations for the configured window")

        history = list(series)
        predictions: List[float] = []
        for _ in range(horizon):
            window_values = history[-self.window :]
            next_value = mean(window_values)
            predictions.append(next_value)
            history.append(next_value)
        return ForecastResult(predictions=predictions, window=self.window)

    @staticmethod
    def rolling_average(series: Iterable[float], window: int) -> List[float]:
        """Compute a rolling average across the provided series."""

        series_list = list(series)
        if window <= 0:
            raise ValueError("Window must be positive")
        if len(series_list) < window:
            return []

        avgs: List[float] = []
        for idx in range(window, len(series_list) + 1):
            avgs.append(mean(series_list[idx - window : idx]))
        return avgs


__all__ = ["ChronoPredictor", "ForecastResult"]
