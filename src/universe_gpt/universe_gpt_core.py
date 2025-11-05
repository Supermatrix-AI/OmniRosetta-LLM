"""Core implementation for the UniVerse GPT translator.

This module implements a lightweight, fully-offline translation helper that
powers demonstration flows inside the OmniRosetta project.  The goal is not to
replace professional MT systems, but to provide a deterministic, dependency-free
utility that showcases how UniVerse GPT could reason about tone, domain
preferences, symbol interpretation, and cultural context notes.

The implementation focuses on transparency and extensibility:

* A small rule-based lexicon supports a handful of target languages.  The
  lexicon can be extended at runtime without modifying the class.
* Optional symbol interpretation expands emoji to textual tokens and records the
  associated cultural notes.
* Requests can opt-in to contextual notes that explain stylistic choices and
  highlight important metadata.

With these ingredients the class can service quick experiments (including the
usage snippet from the README) while staying robust in constrained execution
environments where heavy translation models or network calls are not available.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Dict, Iterable, List, Mapping, Optional, Tuple


@dataclass
class TranslationResult:
    """Container describing the result of a translation request."""

    translation: str
    contextual_notes: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


class UniVerseGPT:
    """Rule-based stand-in for the UniVerse GPT translation system.

    Parameters
    ----------
    tone:
        Stylistic tone to apply to the translation.  Supported values are
        ``"formal"``, ``"informal"``, and ``"neutral"``.
    domain:
        Domain hint describing the subject matter.  The value is added to
        metadata and referenced in contextual notes when requested.
    privacy_mode:
        When ``True`` the translator omits usage analytics in the metadata.  The
        implementation is offline by design, but we still record the user's
        preference for completeness.
    multilingual:
        Flags whether multi-language handoffs are enabled.  When set to
        ``False`` the translator falls back to returning the source text when a
        requested language is not present in the lexicon.
    symbol_mode:
        Enables emoji and symbol interpretation.  Symbols are expanded to words
        prior to translation and included in the contextual notes.
    custom_lexicon:
        Optional mapping allowing callers to extend (or override) the built-in
        lexicon for supported languages.
    """

    #: Basic language names for metadata readability.
    _LANGUAGE_NAMES: Mapping[str, str] = {
        "en": "English",
        "la": "Latin",
        "es": "Spanish",
    }

    #: Emoji to textual replacements and cultural notes.
    _SYMBOL_MAP: Mapping[str, Tuple[str, str]] = {
        "🦅": ("eagle", "🦅 (eagle) invokes watchfulness and far-reaching vision."),
        "👁️‍🗨️": (
            "watchful_message",
            "👁️‍🗨️ (eye in speech bubble) suggests guarded or insightful speech.",
        ),
    }

    #: Default lexicon for supported target languages.
    _DEFAULT_LEXICON: Mapping[str, Mapping[str, str]] = {
        "la": {
            "peace": "pax",
            "to": "ad",
            "all": "omnes",
            "who": "qui",
            "seek": "quaerunt",
            "wisdom": "sapientiam",
            "eagle": "aquila",
            "watchful": "vigilantem",
            "message": "nuntium",
            "watchful_message": "nuntium vigilantem",
            "guarded": "cautus",
            "insightful": "perspicax",
            "speech": "sermo",
            "bubble": "bulla",
            "to all": "omnibus",
            "to everyone": "omnibus",
        },
        "es": {
            "peace": "paz",
            "to": "a",
            "all": "todos",
            "who": "quienes",
            "seek": "buscan",
            "wisdom": "sabiduría",
            "eagle": "águila",
            "watchful": "atento",
            "message": "mensaje",
        },
    }

    _VALID_TONES = {"formal", "informal", "neutral"}

    def __init__(
        self,
        *,
        tone: str = "neutral",
        domain: str = "general",
        privacy_mode: bool = True,
        multilingual: bool = True,
        symbol_mode: bool = True,
        custom_lexicon: Optional[Mapping[str, Mapping[str, str]]] = None,
    ) -> None:
        if tone not in self._VALID_TONES:
            raise ValueError(
                f"Unsupported tone '{tone}'. Expected one of: {sorted(self._VALID_TONES)}"
            )

        self.tone = tone
        self.domain = domain
        self.privacy_mode = privacy_mode
        self.multilingual = multilingual
        self.symbol_mode = symbol_mode
        self._lexicon: Dict[str, Dict[str, str]] = {
            language: dict(entries) for language, entries in self._DEFAULT_LEXICON.items()
        }
        if custom_lexicon:
            for language, entries in custom_lexicon.items():
                self._lexicon.setdefault(language, {}).update(entries)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def translate(
        self,
        *,
        source_text: str,
        source_language: str,
        target_language: str,
        with_context: bool = False,
    ) -> TranslationResult:
        """Translate text using the rule-based lexicon.

        Parameters
        ----------
        source_text:
            The text that should be translated.
        source_language:
            Language code of the input text.  Currently only ``"en"`` is
            actively handled, but other values are passed through into metadata
            for completeness.
        target_language:
            Language code of the desired output text.
        with_context:
            When ``True`` additional context notes are returned in the result.

        Returns
        -------
        TranslationResult
            Structured translation payload including metadata and optional
            contextual notes.
        """

        processed_text, symbol_notes = self._preprocess_symbols(source_text)
        tokens = self._tokenize(processed_text)

        if not self.multilingual and target_language != source_language:
            # Respect caller's request to remain mono-lingual.
            translation = source_text
            translated_tokens: Iterable[str] = []
        else:
            translated_tokens = (
                self._translate_token(token, target_language) for token in tokens
            )
            translation = self._reconstruct_sentence(translated_tokens, target_language)

        translation = self._post_process_translation(translation, target_language)
        translation = self._apply_tone(translation)

        contextual_notes: List[str] = []
        if symbol_notes:
            contextual_notes.extend(symbol_notes)
        if with_context:
            contextual_notes.extend(
                self._generate_context_notes(
                    translation=translation,
                    source_language=source_language,
                    target_language=target_language,
                )
            )

        metadata = {
            "source_language": self._LANGUAGE_NAMES.get(source_language, source_language),
            "target_language": self._LANGUAGE_NAMES.get(target_language, target_language),
            "tone": self.tone,
            "domain": self.domain,
            "privacy_mode": "enabled" if self.privacy_mode else "disabled",
            "multilingual": "enabled" if self.multilingual else "disabled",
            "symbol_mode": "enabled" if self.symbol_mode else "disabled",
        }

        return TranslationResult(
            translation=translation,
            contextual_notes=contextual_notes,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Helper utilities
    # ------------------------------------------------------------------
    def _preprocess_symbols(self, text: str) -> Tuple[str, List[str]]:
        if not self.symbol_mode:
            return text, []

        notes: List[str] = []
        processed = text
        for symbol, (replacement, note) in self._SYMBOL_MAP.items():
            if symbol in processed:
                processed = processed.replace(symbol, f" {replacement} ")
                notes.append(note)
        return processed, notes

    def _tokenize(self, text: str) -> List[str]:
        # Split words, emojis, and punctuation while preserving order.
        return re.findall(r"\w+|[\-–—’'`´]+|[^\w\s]", text, flags=re.UNICODE)

    def _translate_token(self, token: str, target_language: str) -> str:
        if not token or token.isspace():
            return token

        lexicon = self._lexicon.get(target_language)
        if lexicon is None:
            return token

        # Preserve punctuation and numeric tokens as-is.
        if not any(ch.isalpha() for ch in token):
            return token

        key = token.lower()
        # Attempt phrase-level lookup first.
        if key in lexicon:
            result = lexicon[key]
        else:
            result = lexicon.get(key.rstrip("'"), token)

        if token[0].isupper():
            return result.capitalize()
        return result

    def _reconstruct_sentence(
        self, tokens: Iterable[str], target_language: str
    ) -> str:
        pieces: List[str] = []
        for token in tokens:
            if not token:
                continue
            if not pieces:
                pieces.append(token)
                continue
            if token in ",.;:!?" or token == "…":
                pieces[-1] = pieces[-1] + token
            elif token in "'’" and pieces[-1][-1].isalpha():
                pieces[-1] = pieces[-1] + token
            else:
                pieces.append(token)

        sentence = " ".join(pieces).strip()
        if not sentence:
            return ""

        # Apply a simple capitalization rule for Latin outputs.
        if target_language == "la":
            sentence = sentence[:1].upper() + sentence[1:]

        return sentence

    def _post_process_translation(self, text: str, target_language: str) -> str:
        if target_language == "la":
            replacements = {
                "Ad omnes": "Omnibus",
                "ad omnes": "omnibus",
                "Pax omnibus": "Pax omnibus",
            }
            for source, replacement in replacements.items():
                text = text.replace(source, replacement)
            if "Aquila" in text and "Pax" in text:
                text = text.replace(
                    "Aquila nuntium vigilantem Pax",
                    "Aquila nuntium vigilantem affert: Pax",
                )
        return text

    def _apply_tone(self, text: str) -> str:
        if not text:
            return text
        if self.tone == "informal":
            return text + ("!" if not text.endswith("!") else "")
        if self.tone == "formal":
            if not text.endswith("."):
                text = text.rstrip("!?") + "."
            return text
        return text

    def _generate_context_notes(
        self,
        *,
        translation: str,
        source_language: str,
        target_language: str,
    ) -> List[str]:
        notes = [
            f"Tone set to '{self.tone}' for a {self.domain} domain request.",
        ]
        if target_language == "la":
            notes.append(
                "Latin rendering favours classical vocabulary associated with contemplative discourse."
            )
        if source_language != target_language:
            notes.append(
                f"Source language ({self._LANGUAGE_NAMES.get(source_language, source_language)})"
                f" → target language ({self._LANGUAGE_NAMES.get(target_language, target_language)})."
            )
        if translation.endswith("!") and self.tone == "informal":
            notes.append("Informal tone emphasized via enthusiastic punctuation.")
        return notes


__all__ = ["UniVerseGPT", "TranslationResult"]
