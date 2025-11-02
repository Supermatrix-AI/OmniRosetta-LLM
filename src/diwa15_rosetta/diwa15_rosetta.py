"""Utilities for interpreting ancient scripts using heuristic mappings.

This module contains lightweight helpers intended to serve as placeholders for
future machine learning models. The goal is to provide a friendly API surface
for experimentation during early repository bootstrapping.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple


@dataclass
class GlyphMapping:
    """Represents a candidate mapping between a glyph and a phonetic value."""

    glyph: str
    transliteration: str
    confidence: float = field(default=0.5)

    def to_tuple(self) -> Tuple[str, str, float]:
        """Return a tuple representation used by simple scoring functions."""

        return self.glyph, self.transliteration, self.confidence


class RosettaDecoder:
    """Provides simple decoding utilities for experimental pipelines."""

    def __init__(self, symbol_library: Dict[str, str] | None = None) -> None:
        self.symbol_library: Dict[str, str] = symbol_library or {}

    def register_symbols(self, pairs: Iterable[Tuple[str, str]]) -> None:
        """Register glyph-to-transliteration pairs in the internal library."""

        for glyph, transliteration in pairs:
            self.symbol_library[glyph] = transliteration

    def decode_text(self, glyph_sequence: Iterable[str]) -> List[GlyphMapping]:
        """Decode a glyph sequence using the known symbol library.

        Unknown glyphs are returned with a best-effort transliteration equal to
        the glyph itself and a reduced confidence score.
        """

        mappings: List[GlyphMapping] = []
        for glyph in glyph_sequence:
            transliteration = self.symbol_library.get(glyph, glyph)
            confidence = 0.9 if glyph in self.symbol_library else 0.2
            mappings.append(GlyphMapping(glyph, transliteration, confidence))
        return mappings

    @staticmethod
    def score_alignment(mappings: Iterable[GlyphMapping]) -> float:
        """Score the alignment quality on a [0, 1] scale."""

        scored = list(mappings)
        if not scored:
            return 0.0
        return sum(mapping.confidence for mapping in scored) / len(scored)

    @staticmethod
    def generate_notes(mappings: Iterable[GlyphMapping]) -> str:
        """Produce a short textual summary of decoding confidence."""

        scored = list(mappings)
        if not scored:
            return "No glyphs provided."

        avg_conf = RosettaDecoder.score_alignment(scored)
        high_conf = [m for m in scored if m.confidence >= 0.75]
        low_conf = [m for m in scored if m.confidence < 0.5]

        parts = [f"Average confidence: {avg_conf:.2f}."]
        if high_conf:
            high_list = ", ".join(m.glyph for m in high_conf)
            parts.append(f"High certainty glyphs: {high_list}.")
        if low_conf:
            low_list = ", ".join(m.glyph for m in low_conf)
            parts.append(f"Review suggested for: {low_list}.")
        return " ".join(parts)


__all__ = ["GlyphMapping", "RosettaDecoder"]
