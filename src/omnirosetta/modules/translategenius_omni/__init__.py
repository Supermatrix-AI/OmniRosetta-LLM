"""TranslateGenius Omni module for universal translation."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping, Optional


class TranslationError(RuntimeError):
    """Base error raised for issues during the translation workflow."""


class UnsupportedLanguageError(TranslationError):
    """Raised when a language code or name is not supported by the module."""


@dataclass(frozen=True)
class TranslationRequest:
    """Describe the multilingual translation payload."""

    source_language: str
    target_language: str
    content: str
    domain: Optional[str] = None
    tone: Optional[str] = None


@dataclass(frozen=True)
class TranslationResponse:
    """Representation of a translation result with traceability metadata."""

    module: str
    source_language: str
    target_language: str
    detected_source_language: str
    original_content: str
    translated_content: str
    confidence: float
    notes: List[str]


LanguageCode = str


def _normalise_key(value: str) -> str:
    """Normalise user-provided language identifiers for lookups."""

    return value.strip().replace("-", "_").lower()


class TranslateGeniusOmni:
    """Deterministic, dependency-free translation orchestrator.

    The goal of this reference implementation is to provide a small yet
    featureful layer that mirrors a production-grade translation system while
    remaining self-contained for open-source distribution.  It includes:

    * language normalisation with aliases (``"english"`` → ``"en"``)
    * translation-memory backed lookups for fast unit testing
    * glossary term injection to keep domain-specific nouns stable
    * optional auto-detection for the source language when omitted
    * rich response metadata to aid downstream orchestration

    The design makes it trivial to swap in a neural machine translation
    backend by overriding :meth:`_lookup_translation` with model calls.
    """

    #: language aliases recognised by the orchestrator
    _LANGUAGE_ALIASES: Mapping[str, LanguageCode] = {
        "en": "en",
        "eng": "en",
        "english": "en",
        "es": "es",
        "spa": "es",
        "spanish": "es",
        "fr": "fr",
        "fra": "fr",
        "french": "fr",
        "hi": "hi",
        "hin": "hi",
        "hindi": "hi",
        "ta": "ta",
        "tam": "ta",
        "tamil": "ta",
    }

    #: default translation memory for unit tests and offline usage
    _DEFAULT_TRANSLATION_MEMORY: Mapping[
        tuple[LanguageCode, LanguageCode], Mapping[str, str]
    ] = {
        ("en", "es"): {
            "hello": "hola",
            "thank you": "gracias",
            "good morning": "buenos días",
            "how are you?": "¿cómo estás?",
        },
        ("es", "en"): {
            "hola": "hello",
            "gracias": "thank you",
            "buenos días": "good morning",
            "¿cómo estás?": "how are you?",
        },
        ("en", "fr"): {
            "hello": "bonjour",
            "thank you": "merci",
            "good morning": "bonjour",
            "how are you?": "comment ça va ?",
        },
        ("fr", "en"): {
            "bonjour": "hello",
            "merci": "thank you",
            "comment ça va ?": "how are you?",
        },
        ("en", "ta"): {
            "hello": "வணக்கம்",
            "thank you": "நன்றி",
            "good morning": "காலை வணக்கம்",
        },
        ("ta", "en"): {
            "வணக்கம்": "hello",
            "நன்றி": "thank you",
            "காலை வணக்கம்": "good morning",
        },
        ("en", "hi"): {
            "hello": "नमस्ते",
            "thank you": "धन्यवाद",
            "good morning": "सुप्रभात",
        },
        ("hi", "en"): {
            "नमस्ते": "hello",
            "धन्यवाद": "thank you",
            "सुप्रभात": "good morning",
        },
    }

    _LANGUAGE_TOKEN_HINTS: Mapping[LanguageCode, tuple[str, ...]] = {
        "es": ("¿", "¡", "gracias", "buenos", "hola"),
        "fr": ("ç", "é", "bonjour", "merci"),
        "hi": ("नमस्ते", "धन्यवाद", "प्रभात"),
        "ta": ("வணக்கம்", "நன்றி", "காலை"),
    }

    def __init__(
        self,
        *,
        translation_memory: Optional[
            Mapping[tuple[LanguageCode, LanguageCode], Mapping[str, str]]
        ] = None,
        glossary: Optional[Mapping[str, str]] = None,
        default_source_language: LanguageCode = "en",
        default_confidence: float = 0.65,
    ) -> None:
        self._translation_memory = dict(self._DEFAULT_TRANSLATION_MEMORY)
        if translation_memory:
            self._translation_memory.update(
                {key: dict(value) for key, value in translation_memory.items()}
            )
        self._glossary: Dict[str, str] = {
            term.lower(): replacement for term, replacement in (glossary or {}).items()
        }
        self._default_source_language = self._normalise_language(default_source_language)
        self._default_confidence = default_confidence

    def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate between source and target languages.

        Parameters
        ----------
        request:
            Translation parameters including content and language metadata.

        Returns
        -------
        TranslationResponse
            Object containing the translated content with provenance metadata.

        Raises
        ------
        UnsupportedLanguageError
            If the source or target language is not supported.
        TranslationError
            On unexpected failures while performing the lookup.
        """

        if not request.content:
            raise TranslationError("Translation content must not be empty.")

        detected_source = self._resolve_source_language(
            request.source_language, request.content
        )
        target = self._normalise_language(request.target_language)

        translated = self._lookup_translation(detected_source, target, request.content)

        translated = self._apply_glossary(translated)

        notes = self._build_notes(detected_source, target, request)

        return TranslationResponse(
            module="TranslateGenius Omni",
            source_language=request.source_language,
            target_language=target,
            detected_source_language=detected_source,
            original_content=request.content,
            translated_content=translated,
            confidence=self._default_confidence,
            notes=notes,
        )

    def batch_translate(self, requests: Iterable[TranslationRequest]) -> List[TranslationResponse]:
        """Translate a collection of requests, preserving order."""

        return [self.translate(request) for request in requests]

    def _resolve_source_language(self, declared: str, content: str) -> LanguageCode:
        if declared.strip().lower() in {"auto", "detect"}:
            return self._detect_language(content)
        return self._normalise_language(declared)

    def _normalise_language(self, language: str) -> LanguageCode:
        key = _normalise_key(language)
        try:
            return self._LANGUAGE_ALIASES[key]
        except KeyError as exc:  # pragma: no cover - defensive
            raise UnsupportedLanguageError(f"Unsupported language: {language!r}") from exc

    def _detect_language(self, content: str) -> LanguageCode:
        lowered = content.lower()
        for language, hints in self._LANGUAGE_TOKEN_HINTS.items():
            if any(hint.strip() and hint.strip() in lowered for hint in hints):
                return language
        return self._default_source_language

    def _lookup_translation(
        self, source: LanguageCode, target: LanguageCode, content: str
    ) -> str:
        if source == target:
            return content

        key = (source, target)
        memory = self._translation_memory.get(key)
        if not memory:
            raise UnsupportedLanguageError(
                f"Translation memory does not contain pair {source!r} → {target!r}."
            )

        stripped_content = content.strip()
        lower_content = stripped_content.lower()

        # Direct match first for deterministic results
        if lower_content in memory:
            return memory[lower_content]

        # Word-by-word lookup with graceful fallback
        translated_words: List[str] = []
        for token in stripped_content.split():
            translated_words.append(memory.get(token.lower(), token))

        return self._preserve_capitalisation(stripped_content, " ".join(translated_words))

    def _apply_glossary(self, text: str) -> str:
        if not self._glossary:
            return text

        transformed = text
        for term, replacement in self._glossary.items():
            transformed = self._replace_case_insensitive(transformed, term, replacement)
        return transformed

    def _build_notes(
        self, source: LanguageCode, target: LanguageCode, request: TranslationRequest
    ) -> List[str]:
        notes = [f"source={source}", f"target={target}"]
        if request.domain:
            notes.append(f"domain={request.domain}")
        if request.tone:
            notes.append(f"tone={request.tone}")
        if self._glossary:
            notes.append("glossary_applied=true")
        return notes

    @staticmethod
    @lru_cache(maxsize=64)
    def _preserve_capitalisation(original: str, translated: str) -> str:
        if not original:
            return translated
        if original[0].isupper():
            return translated[:1].upper() + translated[1:]
        return translated

    @staticmethod
    def _replace_case_insensitive(text: str, term: str, replacement: str) -> str:
        lower_text = text.lower()
        lower_term = term.lower()
        start = 0
        result = text
        while True:
            index = lower_text.find(lower_term, start)
            if index == -1:
                break
            result = result[:index] + replacement + result[index + len(term) :]
            lower_text = result.lower()
            start = index + len(replacement)
        return result


__all__ = [
    "TranslateGeniusOmni",
    "TranslationRequest",
    "TranslationResponse",
    "TranslationError",
    "UnsupportedLanguageError",
]
