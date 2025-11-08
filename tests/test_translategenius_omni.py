"""Test-suite for the TranslateGenius Omni module."""

from omnirosetta.modules.translategenius_omni import (
    TranslateGeniusOmni,
    TranslationRequest,
    UnsupportedLanguageError,
)


def test_direct_translation_from_english_to_spanish() -> None:
    translator = TranslateGeniusOmni()
    request = TranslationRequest(source_language="en", target_language="es", content="hello")

    response = translator.translate(request)

    assert response.translated_content == "hola"
    assert "source=en" in response.notes
    assert "target=es" in response.notes


def test_auto_detects_source_language() -> None:
    translator = TranslateGeniusOmni()
    request = TranslationRequest(
        source_language="auto",
        target_language="en",
        content="¿Cómo estás?",
    )

    response = translator.translate(request)

    assert response.detected_source_language == "es"
    assert response.translated_content == "how are you?"


def test_glossary_terms_override_memory_entries() -> None:
    translator = TranslateGeniusOmni(glossary={"bonjour": "salut"})
    request = TranslationRequest(source_language="en", target_language="fr", content="hello")

    response = translator.translate(request)

    assert response.translated_content == "salut"
    assert "glossary_applied=true" in response.notes


def test_unsupported_language_pair_raises() -> None:
    translator = TranslateGeniusOmni()
    request = TranslationRequest(source_language="en", target_language="jp", content="hello")

    try:
        translator.translate(request)
    except UnsupportedLanguageError as error:
        assert "jp" in str(error)
    else:  # pragma: no cover - guard against silent success
        raise AssertionError("Unsupported language did not raise an error")


def test_batch_translation_preserves_order() -> None:
    translator = TranslateGeniusOmni()
    requests = [
        TranslationRequest(source_language="en", target_language="es", content="hello"),
        TranslationRequest(source_language="en", target_language="fr", content="thank you"),
    ]

    responses = translator.batch_translate(requests)

    assert [response.translated_content for response in responses] == ["hola", "merci"]
