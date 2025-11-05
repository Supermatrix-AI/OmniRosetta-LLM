"""Unit tests for the TranslateGenius Omni module."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


from omnirosetta.modules.translategenius_omni import (  # noqa: E402 module import
    SegmentTrace,
    TranslateGeniusOmni,
    TranslationRequest,
    TranslationValidationError,
)


def test_translation_round_trip_basic_english_to_spanish() -> None:
    translator = TranslateGeniusOmni()
    request = TranslationRequest(target_language="es", content="Hello world")
    response = translator.translate(request)

    assert response.translated_content.strip().startswith("Hola")
    assert response.detected_language == "en"
    assert response.target_language == "es"
    assert response.confidence > 0
    assert any(isinstance(segment, SegmentTrace) for segment in response.segments)


def test_translation_requires_different_languages() -> None:
    translator = TranslateGeniusOmni()
    request = TranslationRequest(target_language="en", content="Hello", source_language="en")

    try:
        translator.translate(request)
    except TranslationValidationError as error:
        assert "must differ" in str(error)
    else:  # pragma: no cover - defensive, makes the assertion explicit
        raise AssertionError("Expected a TranslationValidationError to be raised")


def test_cli_parser_handles_metadata_entries() -> None:
    from omnirosetta.modules.translategenius_omni import cli

    parser = cli.build_parser()
    args = parser.parse_args(["Hello", "--target", "es", "--metadata", "domain=general"])
    assert args.metadata == ["domain=general"]

    metadata = cli.parse_metadata(args.metadata)
    assert metadata == {"domain": "general"}
