"""Backwards-compatible shim for the TranslateGenius Omni module.

This module existed in earlier iterations of the repository as a lightweight
placeholder.  The production-ready implementation now lives under
``src/omnirosetta/modules/translategenius_omni``.  To keep older imports working
while consolidating the codebase, we simply re-export the modern classes.
"""

from omnirosetta.modules.translategenius_omni import (  # noqa: F401
    TranslateGeniusOmni,
    TranslationRequest,
    TranslationResponse,
    TranslationError,
    UnsupportedLanguageError,
)

__all__ = [
    "TranslateGeniusOmni",
    "TranslationRequest",
    "TranslationResponse",
    "TranslationError",
    "UnsupportedLanguageError",
]
