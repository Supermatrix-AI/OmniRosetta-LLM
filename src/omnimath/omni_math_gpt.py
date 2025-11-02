"""Lightweight math reasoning helpers."""
from __future__ import annotations

from typing import Iterable, List


def solve_linear(a: float, b: float) -> float:
    """Solve a linear equation of the form ax + b = 0."""

    if a == 0:
        raise ValueError("Coefficient 'a' must be non-zero")
    return -b / a


def batch_mean(values: Iterable[float]) -> float:
    """Return the arithmetic mean of the provided values."""

    values_list: List[float] = list(values)
    if not values_list:
        raise ValueError("values must not be empty")
    return sum(values_list) / len(values_list)


__all__ = ["solve_linear", "batch_mean"]
