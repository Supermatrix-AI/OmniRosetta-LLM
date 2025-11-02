"""Data schemas for Diwa decoder API payloads."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DecodeRequest:
    glyphs: List[str] = field(default_factory=list)
    library: Dict[str, str] = field(default_factory=dict)


__all__ = ["DecodeRequest"]
