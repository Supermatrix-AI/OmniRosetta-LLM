"""Simple vault synchronization primitives."""
from __future__ import annotations

from typing import Dict


class VaultSync:
    """Maintain key-value snapshots for shared state."""

    def __init__(self) -> None:
        self.state: Dict[str, str] = {}

    def update(self, key: str, value: str) -> None:
        self.state[key] = value

    def snapshot(self) -> Dict[str, str]:
        return dict(self.state)


__all__ = ["VaultSync"]
