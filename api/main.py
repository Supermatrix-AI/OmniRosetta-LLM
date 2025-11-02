"""Entry point for the OmniRosetta API service."""
from __future__ import annotations

from typing import Callable, Dict

from .routes import decode, design, forecast, mathsolve, translate


def create_app() -> Dict[str, Callable[..., object]]:
    """Return a lightweight representation of available routes."""

    return {
        "translate": translate.handle_translation,
        "forecast": forecast.handle_forecast,
        "decode": decode.handle_decode,
        "mathsolve": mathsolve.handle_math,
        "design": design.handle_design,
    }


__all__ = ["create_app"]
