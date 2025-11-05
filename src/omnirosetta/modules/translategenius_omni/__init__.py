"""TranslateGenius Omni module linking translation, synthesis, and symbol decoding."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class TranslationRequest:
    """Describe the multilingual translation payload."""

    source_language: str
    target_language: str
    content: str
    domain: Optional[str] = None
    tone: Optional[str] = None
    include_symbol_notes: bool = False
    context: Optional[str] = None


@dataclass
class SynthesisRequest:
    """Describe a knowledge synthesis task spanning multiple languages."""

    prompt: str
    languages: Sequence[str]
    focus: Optional[str] = None
    references: Optional[Sequence[str]] = None


@dataclass
class SymbolDecodingRequest:
    """Define a symbol decoding task grounded in cultural lexicons."""

    content: Optional[str] = None
    symbols: Optional[Sequence[str]] = None
    culture: Optional[str] = None
    speculative: bool = False


@dataclass
class TranslationMemoryEntry:
    """Minimal translation memory trace for auditing."""

    source_language: str
    target_language: str
    source_text: str
    translated_text: str
    domain: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OmniTranslationResponse:
    """Structured response returned by :class:`TranslateGeniusOmni`."""

    module: str
    source_language: str
    target_language: str
    translated_content: str
    confidence: float
    alignments: List[Tuple[str, str]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        """Convert the response into a serialisable payload."""

        return {
            "module": self.module,
            "source_language": self.source_language,
            "target_language": self.target_language,
            "translated_content": self.translated_content,
            "confidence": round(self.confidence, 3),
            "alignments": self.alignments,
            "notes": self.notes,
            "diagnostics": self.diagnostics,
        }


@dataclass
class SymbolDecodingResult:
    """Represent the output of a symbol decoding routine."""

    module: str
    culture: Optional[str]
    interpretations: List[Dict[str, Any]]
    speculative: bool

    def to_payload(self) -> Dict[str, Any]:
        """Convert the result into a serialisable payload."""

        return {
            "module": self.module,
            "culture": self.culture,
            "interpretations": self.interpretations,
            "speculative": self.speculative,
        }


# ---------------------------------------------------------------------------
# Heuristic knowledge stores
# ---------------------------------------------------------------------------


LANGUAGE_ALIASES: Dict[str, str] = {
    "english": "en",
    "en": "en",
    "spanish": "es",
    "es": "es",
    "hindi": "hi",
    "hi": "hi",
    "tamil": "ta",
    "ta": "ta",
    "sanskrit": "sa",
    "sa": "sa",
    "french": "fr",
    "fr": "fr",
    "sumerian": "sux",
    "sux": "sux",
}


LANGUAGE_DISPLAY_NAMES: Dict[str, str] = {
    "en": "English",
    "es": "Spanish",
    "hi": "Hindi",
    "ta": "Tamil",
    "sa": "Sanskrit",
    "fr": "French",
    "sux": "Sumerian",
}


SAMPLE_DICTIONARIES: Dict[Tuple[str, str], Dict[str, str]] = {
    ("en", "es"): {
        "hello": "hola",
        "world": "mundo",
        "river": "río",
        "sun": "sol",
        "moon": "luna",
    },
    ("en", "ta"): {
        "hello": "வணக்கம்",
        "world": "உலகம்",
        "knowledge": "அறிவு",
        "river": "ஆறு",
    },
    ("en", "hi"): {
        "hello": "नमस्ते",
        "world": "दुनिया",
        "knowledge": "ज्ञान",
        "water": "जल",
    },
    ("es", "en"): {
        "hola": "hello",
        "mundo": "world",
        "conocimiento": "knowledge",
    },
}


SYMBOL_LEXICON: Dict[str, Dict[str, Any]] = {
    "INDUS_FISH": {
        "meaning": "Abundance, fertility, and riverine trade routes in Indus iconography",
        "culture": "Indus Valley",
        "sources": ["Marshall 1931", "Mahadevan 1977"],
    },
    "INDUS_UNICORN": {
        "meaning": "Mythic beast symbolising elite guild authority",
        "culture": "Indus Valley",
        "sources": ["Parpola 1994"],
    },
    "RONGORONGO_MANU": {
        "meaning": "Bird-man cycle, ritual stewardship of Makemake",
        "culture": "Rongorongo",
        "sources": ["Barthel 1958"],
    },
    "SUMERIAN_DINGIR": {
        "meaning": "Divine determinative marking celestial or revered entities",
        "culture": "Sumerian Cuneiform",
        "sources": ["Kramer 1961"],
    },
}


SYNTHESIS_TEMPLATES: Dict[str, List[str]] = {
    "cultural": [
        "Highlight ritual context and socio-ecological relevance.",
        "Surface cross-lingual cognates or shared metaphors.",
        "Document ethical considerations for stewardship and transmission.",
    ],
    "scientific": [
        "Summarise the hypothesis or key mechanism succinctly.",
        "Detail evidence chains or experimental provenance.",
        "Map open questions suitable for collaborative follow-up.",
    ],
}


# ---------------------------------------------------------------------------
# TranslateGenius Omni orchestrator
# ---------------------------------------------------------------------------


class TranslateGeniusOmni:
    """Multiversal translation bridge for the OmniRosetta ecosystem."""

    def __init__(self) -> None:
        self.translation_memory: List[TranslationMemoryEntry] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def translate(self, request: TranslationRequest) -> Dict[str, Any]:
        """Translate between source and target languages.

        The method uses heuristic dictionaries to emulate the orchestration
        normally provided by production-scale models.  Each translation is
        captured in a lightweight memory for downstream audits.
        """

        source = self._normalise_language(request.source_language)
        target = self._normalise_language(request.target_language)

        translated_text, alignments = self._run_translation(
            request.content, source, target
        )

        confidence = self._estimate_confidence(request.content, alignments)

        notes: List[str] = []
        symbol_result: Optional[SymbolDecodingResult] = None
        if request.include_symbol_notes:
            symbol_result = self.decode_symbols(
                SymbolDecodingRequest(content=request.content, culture=request.domain)
            )
            if symbol_result.interpretations:
                notes.append("Symbolic annotations included in diagnostics.")

        diagnostics: Dict[str, Any] = {
            "domain": request.domain,
            "tone": request.tone,
            "context": request.context,
            "alignment_pairs": len(alignments),
        }

        if symbol_result is not None:
            diagnostics["symbolic_interpretations"] = symbol_result.interpretations

        response = OmniTranslationResponse(
            module="TranslateGenius Omni",
            source_language=self._language_display_name(source),
            target_language=self._language_display_name(target),
            translated_content=translated_text,
            confidence=confidence,
            alignments=alignments,
            notes=notes,
            diagnostics=diagnostics,
        )

        self.translation_memory.append(
            TranslationMemoryEntry(
                source_language=source,
                target_language=target,
                source_text=request.content,
                translated_text=translated_text,
                domain=request.domain,
                metadata={"tone": request.tone, "confidence": confidence},
            )
        )

        return response.to_payload()

    def synthesize(self, request: SynthesisRequest) -> Dict[str, Any]:
        """Generate a multilingual synthesis brief."""

        languages = [self._language_display_name(self._normalise_language(lang)) for lang in request.languages]
        template_key = (request.focus or "cultural").lower()
        template = SYNTHESIS_TEMPLATES.get(template_key, SYNTHESIS_TEMPLATES["cultural"])

        segments = []
        for idx, instruction in enumerate(template, start=1):
            segments.append(f"{idx}. {instruction}")

        references = list(request.references or [])
        payload = {
            "module": "TranslateGenius Omni",
            "summary": request.prompt.strip(),
            "focus": request.focus or "cultural",
            "languages": languages,
            "instructions": segments,
        }
        if references:
            payload["references"] = references

        return payload

    def decode_symbols(self, request: SymbolDecodingRequest) -> SymbolDecodingResult:
        """Decode symbolic annotations with cultural grounding."""

        requested_symbols = set(
            symbol.upper().strip() for symbol in request.symbols or [] if symbol
        )

        if request.content:
            requested_symbols.update(self._extract_symbols(request.content))

        interpretations: List[Dict[str, Any]] = []
        for symbol in sorted(requested_symbols):
            lexeme = SYMBOL_LEXICON.get(symbol)
            if lexeme:
                interpretations.append(
                    {
                        "symbol": symbol,
                        "meaning": lexeme["meaning"],
                        "culture": lexeme["culture"],
                        "confidence": 0.78 if not request.speculative else 0.65,
                        "sources": lexeme["sources"],
                    }
                )
            else:
                interpretations.append(
                    {
                        "symbol": symbol,
                        "meaning": None,
                        "culture": request.culture,
                        "confidence": 0.2,
                        "notes": "Symbol not present in core lexicon; requires expert review.",
                    }
                )

        return SymbolDecodingResult(
            module="TranslateGenius Omni",
            culture=request.culture,
            interpretations=interpretations,
            speculative=request.speculative,
        )

    def batch_translate(
        self, request: TranslationRequest, targets: Iterable[str]
    ) -> Dict[str, Any]:
        """Translate the same content into multiple target languages."""

        results = []
        for target in targets:
            payload = self.translate(
                TranslationRequest(
                    source_language=request.source_language,
                    target_language=target,
                    content=request.content,
                    domain=request.domain,
                    tone=request.tone,
                    include_symbol_notes=request.include_symbol_notes,
                    context=request.context,
                )
            )
            results.append(payload)

        return {
            "module": "TranslateGenius Omni",
            "mode": "batch",
            "source_language": self._language_display_name(
                self._normalise_language(request.source_language)
            ),
            "translations": results,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _normalise_language(self, language: str) -> str:
        normalised = LANGUAGE_ALIASES.get(language.lower())
        if not normalised:
            return language.lower()
        return normalised

    def _language_display_name(self, code: str) -> str:
        return LANGUAGE_DISPLAY_NAMES.get(code, code.upper())

    def _run_translation(
        self, content: str, source: str, target: str
    ) -> Tuple[str, List[Tuple[str, str]]]:
        if source == target:
            return content, []

        dictionary = SAMPLE_DICTIONARIES.get((source, target), {})
        tokens = re.findall(r"\w+|\s+|[^\w\s]", content, re.UNICODE)
        alignments: List[Tuple[str, str]] = []
        translated_tokens: List[str] = []

        for token in tokens:
            if token.isspace():
                translated_tokens.append(token)
                continue

            lower = token.lower()
            translated = dictionary.get(lower)
            if translated:
                translated = self._preserve_case(token, translated)
                alignments.append((token, translated))
                translated_tokens.append(translated)
                continue

            # Default fall-back keeps the token while flagging target language.
            translated_tokens.append(f"{token}")

        translated_text = "".join(translated_tokens)
        return translated_text, alignments

    def _estimate_confidence(
        self, content: str, alignments: Sequence[Tuple[str, str]]
    ) -> float:
        tokens = [token for token in re.findall(r"\w+", content, re.UNICODE)]
        if not tokens:
            return 1.0
        coverage = len(alignments) / len(tokens)
        return min(1.0, 0.5 + 0.5 * coverage)

    def _extract_symbols(self, content: str) -> Iterable[str]:
        pattern = re.compile(r"\[\[(?:SYMBOL:)?([A-Z0-9_\- ]+)\]\]")
        return (match.group(1).strip().replace(" ", "_") for match in pattern.finditer(content))

    def _preserve_case(self, source_token: str, translated_token: str) -> str:
        if source_token.isupper():
            return translated_token.upper()
        if source_token.istitle():
            return translated_token.title()
        return translated_token

