"""Forecast API route handler."""
from __future__ import annotations

from typing import Dict

from src.chrono_predict.chrono_predict_ultra import ChronoPredictor


def handle_forecast(payload: Dict[str, object]) -> Dict[str, object]:
    """Return predictions using the ChronoPredictor moving average."""

    series = payload.get("series", [])
    horizon = int(payload.get("horizon", 1))
    window = int(payload.get("window", 3))

    predictor = ChronoPredictor(window=window)
    result = predictor.forecast(series=series, horizon=horizon)  # type: ignore[arg-type]
    return {"predictions": result.predictions, "window": result.window}


__all__ = ["handle_forecast"]
