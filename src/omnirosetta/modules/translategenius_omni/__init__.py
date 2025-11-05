"""Core TranslateGenius Omni interfaces.

This module provides a lightweight-yet-structured translation pipeline that can
run without heavyweight model dependencies while still exposing the
configuration surfaces needed by future multilingual model integrations.  The
goal is to provide a *usable* fallback for development and testing while also
documenting the orchestration hooks that production systems can extend.

The implementation favours transparency and debuggability: every translation
response includes detection metadata, per-segment traces, and confidence
signals that downstream agents can use for human-in-the-loop review.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import re
from typing import Any, Dict, Iterable, List, MutableMapping, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants and lightweight resources
# ---------------------------------------------------------------------------


LANGUAGE_ALIASES: Dict[str, Tuple[str, ...]] = {
    "en": ("en", "eng", "english"),
    "es": ("es", "spa", "spanish", "español"),
    "fr": ("fr", "fra", "fre", "french", "français"),
    "de": ("de", "ger", "deu", "german", "deutsch"),
    "hi": ("hi", "hin", "hindi"),
    "ta": ("ta", "tam", "tamil"),
}


TRANSLATION_MEMORY: Dict[Tuple[str, str], Dict[str, str]] = {
    ("en", "es"): {
        "hello": "hola",
        "world": "mundo",
        "thank": "gracias",
        "you": "tú",
        "peace": "paz",
        "water": "agua",
        "friend": "amigo",
    },
    ("es", "en"): {
        "hola": "hello",
        "mundo": "world",
        "gracias": "thank you",
        "paz": "peace",
        "agua": "water",
        "amigo": "friend",
    },
    ("en", "fr"): {
        "hello": "bonjour",
        "world": "monde",
        "friend": "ami",
        "peace": "paix",
        "water": "eau",
    },
    ("fr", "en"): {
        "bonjour": "hello",
        "monde": "world",
        "ami": "friend",
        "paix": "peace",
        "eau": "water",
    },
    ("en", "de"): {
        "hello": "hallo",
        "world": "welt",
        "friend": "freund",
        "peace": "frieden",
        "water": "wasser",
    },
    ("de", "en"): {
        "hallo": "hello",
        "welt": "world",
        "freund": "friend",
        "frieden": "peace",
        "wasser": "water",
    },
    ("en", "hi"): {
        "hello": "नमस्ते",
        "world": "दुनिया",
        "friend": "दोस्त",
        "peace": "शांति",
        "water": "पानी",
    },
    ("hi", "en"): {
        "नमस्ते": "hello",
        "दुनिया": "world",
        "दोस्त": "friend",
        "शांति": "peace",
        "पानी": "water",
    },
    ("en", "ta"): {
        "hello": "வணக்கம்",
        "world": "உலகம்",
        "friend": "நண்பன்",
        "peace": "சமாதானம்",
        "water": "தண்ணீர்",
    },
    ("ta", "en"): {
        "வணக்கம்": "hello",
        "உலகம்": "world",
        "நண்பன்": "friend",
        "சமாதானம்": "peace",
        "தண்ணீர்": "water",
    },
}


SCRIPT_RANGES: Dict[str, Tuple[int, int]] = {
    "ta": (0x0B80, 0x0BFF),  # Tamil block
    "hi": (0x0900, 0x097F),  # Devanagari block
}


# ---------------------------------------------------------------------------
# Dataclasses & domain models
# ---------------------------------------------------------------------------


@dataclass
class TranslationRequest:
    """Describe the multilingual translation payload."""

    target_language: str
    content: str
    source_language: Optional[str] = None
    context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SegmentTrace:
    """Captures how an individual segment was translated."""

    source_segment: str
    translated_segment: str
    applied_strategy: str


@dataclass
class TranslationResponse:
    """Structured response for TranslateGenius Omni."""

    module: str
    detected_language: str
    target_language: str
    translated_content: str
    confidence: float
    segments: List[SegmentTrace]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Render the response as a serialisable dictionary."""

        return {
            "module": self.module,
            "detected_language": self.detected_language,
            "target_language": self.target_language,
            "translated_content": self.translated_content,
            "confidence": self.confidence,
            "segments": [
                {
                    "source_segment": segment.source_segment,
                    "translated_segment": segment.translated_segment,
                    "applied_strategy": segment.applied_strategy,
                }
                for segment in self.segments
            ],
            "metadata": self.metadata,
        }

    def to_json(self, *, indent: Optional[int] = 2) -> str:
        """Serialise the response as JSON for CLI or logging outputs."""

        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


class TranslationValidationError(ValueError):
    """Raised when the translation request is invalid."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def normalise_language_code(code: Optional[str]) -> Optional[str]:
    """Return an ISO-like 2-letter language code if possible."""

    if code is None:
        return None

    normalised = code.strip().lower()
    for canonical, aliases in LANGUAGE_ALIASES.items():
        if normalised == canonical or normalised in aliases:
            return canonical
    return normalised or None


def detect_language(text: str) -> Tuple[str, float]:
    """Guess a language with a heuristic confidence score."""

    text_lower = text.lower()
    if not text_lower.strip():
        return "unknown", 0.0

    # Script-aware detection first (Tamil & Devanagari).
    for language, (start, end) in SCRIPT_RANGES.items():
        if any(start <= ord(char) <= end for char in text):
            return language, 0.95

    keyword_sets: Dict[str, Iterable[str]] = {
        "en": ("the", "and", "is"),
        "es": (" el ", " la ", " y ", " es "),
        "fr": (" le ", " la ", " et ", " est "),
        "de": (" der ", " die ", " und ", " ist "),
        "hi": (" है", " और", "यह"),
    }

    best_match = "unknown"
    best_score = 0.2

    padded = f" {text_lower} "
    for language, keywords in keyword_sets.items():
        score = sum(1 for token in keywords if token in padded)
        if score > best_score:
            best_match = language
            best_score = score

    if best_match == "unknown":
        return "unknown", 0.1

    return best_match, min(best_score / 3.0, 0.9)


def split_segments(text: str) -> List[str]:
    """Split a paragraph into roughly sentence-like segments."""

    segments = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", text) if segment.strip()]
    return segments or [text.strip()]


def translate_tokens(
    tokens: List[str],
    memory: MutableMapping[str, str],
) -> Tuple[str, str]:
    """Translate tokens using the provided memory.

    Returns the translated string and a string describing the strategy used.
    """

    translated_tokens: List[str] = []
    strategy = "memory"

    for token in tokens:
        stripped = re.sub(r"\W+", "", token)
        if not stripped:
            translated_tokens.append(token)
            continue

        key = stripped.lower()
        translated = memory.get(key)
        if translated is None:
            strategy = "memory+copy"
            translated = stripped

        if stripped.istitle():
            translated = translated.capitalize()
        elif stripped.isupper():
            translated = translated.upper()

        translated_tokens.append(token.replace(stripped, translated))

    return "".join(translated_tokens), strategy


# ---------------------------------------------------------------------------
# TranslateGenius Omni implementation
# ---------------------------------------------------------------------------


class TranslateGeniusOmni:
    """Multilingual translation pipeline with traceable fallbacks."""

    module_name = "TranslateGenius Omni"

    def __init__(
        self,
        *,
        translation_memory: Optional[Dict[Tuple[str, str], Dict[str, str]]] = None,
    ) -> None:
        self._memory = translation_memory or TRANSLATION_MEMORY

    # Public API ---------------------------------------------------------

    @property
    def supported_languages(self) -> List[str]:
        """Return the canonical language codes known by the translator."""

        supported = sorted({code for pair in self._memory for code in pair})
        return supported

    def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate between the detected source language and the target."""

        validated = self._validate_request(request)
        source_language = validated["source_language"]

        memory_key = (source_language, validated["target_language"])
        memory = self._memory.get(memory_key, {})

        segments = []
        translated_parts = []
        for segment in split_segments(request.content):
            tokens = re.findall(r"\w+|\W+", segment)
            translated_segment, strategy = translate_tokens(tokens, memory)
            segments.append(
                SegmentTrace(
                    source_segment=segment,
                    translated_segment=translated_segment,
                    applied_strategy=strategy,
                )
            )
            translated_parts.append(translated_segment)

        detection_confidence = validated["confidence"]
        # If we had to fall back to copying words, reduce the confidence a bit.
        if any(trace.applied_strategy != "memory" for trace in segments):
            detection_confidence = max(0.1, detection_confidence - 0.15)

        metadata = {
            "source_language": source_language,
            "target_language": validated["target_language"],
            "context": request.context,
            "request_metadata": request.metadata,
            "memory_size": len(memory),
        }

        return TranslationResponse(
            module=self.module_name,
            detected_language=source_language,
            target_language=validated["target_language"],
            translated_content=" ".join(translated_parts),
            confidence=round(detection_confidence, 2),
            segments=segments,
            metadata=metadata,
        )

    # Internal utilities -------------------------------------------------

    def _validate_request(self, request: TranslationRequest) -> Dict[str, Any]:
        """Normalise inputs and check whether the translator can run."""

        if not isinstance(request.content, str) or not request.content.strip():
            raise TranslationValidationError("Translation content must be a non-empty string.")

        target = normalise_language_code(request.target_language)
        if not target:
            raise TranslationValidationError("Target language is required.")

        if target not in self.supported_languages:
            raise TranslationValidationError(
                f"Target language '{request.target_language}' is not supported. "
                f"Supported languages: {', '.join(self.supported_languages)}"
            )

        if request.source_language:
            source = normalise_language_code(request.source_language)
            if not source:
                raise TranslationValidationError(
                    f"Unrecognised source language '{request.source_language}'."
                )
            confidence = 0.95
        else:
            source, confidence = detect_language(request.content)
            if source == "unknown":
                # Fallback to assuming English for compatibility, but report low confidence.
                source = "en"
                confidence = 0.1

        if source == target:
            raise TranslationValidationError("Source and target languages must differ.")

        if (source, target) not in self._memory:
            # Create a view that mirrors word-for-word when no explicit memory exists.
            self._memory.setdefault((source, target), {})

        return {"source_language": source, "target_language": target, "confidence": confidence}


__all__ = [
    "TranslateGeniusOmni",
    "TranslationRequest",
    "TranslationResponse",
    "SegmentTrace",
    "TranslationValidationError",
]
