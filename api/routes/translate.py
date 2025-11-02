"""Translation API route handlers."""
from __future__ import annotations

from typing import Dict

from src.omni_translation.translate_genius import TranslateGenius


def handle_translation(payload: Dict[str, object]) -> Dict[str, object]:
    """Handle a translation request using the TranslateGenius helper."""

    dictionary = payload.get("dictionary", {})
    tokens = payload.get("tokens", [])
    translator = TranslateGenius(dictionary=dictionary)  # type: ignore[arg-type]
    translated = translator.translate_tokens(tokens)  # type: ignore[arg-type]
    return {"translated": translated}


__all__ = ["handle_translation"]
