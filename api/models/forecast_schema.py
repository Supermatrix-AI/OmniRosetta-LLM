"""Forecasting payload schemas."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ForecastRequest:
    series: List[float] = field(default_factory=list)
    horizon: int = 1
    window: int = 3


__all__ = ["ForecastRequest"]
