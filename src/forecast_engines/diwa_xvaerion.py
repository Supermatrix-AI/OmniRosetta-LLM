"""Diwa Xvaerion synthetic data generator."""
from __future__ import annotations

from dataclasses import dataclass
from random import random
from typing import List


@dataclass
class SyntheticEvent:
    name: str
    probability: float


class DiwaXvaerion:
    """Generate synthetic events with pseudo-random probabilities."""

    def generate(self, labels: List[str]) -> List[SyntheticEvent]:
        events = [SyntheticEvent(name=label, probability=round(random(), 2)) for label in labels]
        return events


__all__ = ["DiwaXvaerion", "SyntheticEvent"]
