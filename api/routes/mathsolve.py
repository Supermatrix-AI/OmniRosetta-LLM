"""Math solving API route handler."""
from __future__ import annotations

from typing import Dict

from src.omnimath.omni_math_gpt import batch_mean, solve_linear


def handle_math(payload: Dict[str, object]) -> Dict[str, object]:
    """Solve small math tasks."""

    response: Dict[str, object] = {}
    if "linear" in payload:
        coeffs = payload["linear"]
        response["linear_solution"] = solve_linear(coeffs[0], coeffs[1])  # type: ignore[index]
    if "mean" in payload:
        response["mean"] = batch_mean(payload["mean"])  # type: ignore[arg-type]
    return response


__all__ = ["handle_math"]
