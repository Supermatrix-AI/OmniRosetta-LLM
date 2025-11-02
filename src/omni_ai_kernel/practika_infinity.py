"""Prototype knowledge graph operations."""
from __future__ import annotations

from typing import Dict, Set


class PractikaInfinity:
    """Maintain a simple adjacency mapping for concept graphs."""

    def __init__(self) -> None:
        self.graph: Dict[str, Set[str]] = {}

    def link(self, source: str, target: str) -> None:
        self.graph.setdefault(source, set()).add(target)

    def neighbors(self, node: str) -> Set[str]:
        return self.graph.get(node, set())


__all__ = ["PractikaInfinity"]
