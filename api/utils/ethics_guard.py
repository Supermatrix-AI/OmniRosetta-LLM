"""Basic ethics guard used by the API."""
from __future__ import annotations

from typing import Iterable

from src.omni_translation.oci_omni_conscious import check_ethics


def ensure_safe(texts: Iterable[str]) -> bool:
    return all(check_ethics(text) for text in texts)


__all__ = ["ensure_safe"]
