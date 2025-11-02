"""Ethics-aware translation utilities."""
from __future__ import annotations

from typing import Iterable


SENSITIVE_TOPICS = {"hate", "violence", "self-harm"}


def check_ethics(text: str) -> bool:
    """Return True if text does not contain sensitive topics."""

    tokens = {token.lower() for token in text.split()}
    return SENSITIVE_TOPICS.isdisjoint(tokens)


def filter_batch(texts: Iterable[str]) -> list[str]:
    """Filter out texts that fail the ethics check."""

    return [text for text in texts if check_ethics(text)]


__all__ = ["SENSITIVE_TOPICS", "check_ethics", "filter_batch"]
