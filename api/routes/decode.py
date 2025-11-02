"""Decoding API route handler."""
from __future__ import annotations

from typing import Dict

from src.diwa15_rosetta.diwa15_rosetta import RosettaDecoder


def handle_decode(payload: Dict[str, object]) -> Dict[str, object]:
    """Decode glyph sequences using the RosettaDecoder."""

    glyphs = payload.get("glyphs", [])
    library = payload.get("library", {})
    decoder = RosettaDecoder(symbol_library=library)  # type: ignore[arg-type]
    mappings = decoder.decode_text(glyph_sequence=glyphs)  # type: ignore[arg-type]
    return {
        "mappings": [mapping.to_tuple() for mapping in mappings],
        "score": decoder.score_alignment(mappings),
    }


__all__ = ["handle_decode"]
