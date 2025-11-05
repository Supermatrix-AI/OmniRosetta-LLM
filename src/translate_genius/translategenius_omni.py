"""Compatibility wrapper for legacy imports.

Historically, downstream projects imported ``TranslateGeniusOmni`` from the
``src.translate_genius`` namespace.  The new implementation lives under
``src.omnirosetta.modules.translategenius_omni``.  This module keeps the import
path stable while forwarding all functionality.
"""

from __future__ import annotations

from omnirosetta.modules.translategenius_omni import (  # noqa: F401 re-export
    SegmentTrace,
    TranslateGeniusOmni,
    TranslationRequest,
    TranslationResponse,
    TranslationValidationError,
)

__all__ = [
    "TranslateGeniusOmni",
    "TranslationRequest",
    "TranslationResponse",
    "SegmentTrace",
    "TranslationValidationError",
]
