"""Design assistance API route handler."""
from __future__ import annotations

from typing import Dict

from src.architecture_ai.architech_ai import DesignBrief, summarize_brief


def handle_design(payload: Dict[str, object]) -> Dict[str, object]:
    """Summarize a design brief provided by the client."""

    brief = DesignBrief(
        style=str(payload.get("style", "modern")),
        square_meters=float(payload.get("square_meters", 100)),
        requirements=list(payload.get("requirements", [])),
    )
    return summarize_brief(brief)


__all__ = ["handle_design"]
