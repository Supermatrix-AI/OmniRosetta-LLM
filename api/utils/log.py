"""Logging utilities for the API layer."""
from __future__ import annotations

from datetime import datetime
from typing import List


def format_log(message: str) -> str:
    timestamp = datetime.utcnow().isoformat()
    return f"[{timestamp}] {message}"


def batch_logs(messages: List[str]) -> List[str]:
    return [format_log(message) for message in messages]


__all__ = ["format_log", "batch_logs"]
