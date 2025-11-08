"""Command line entry-points for OmniRosetta modules."""

from __future__ import annotations

import argparse
import json
from typing import Dict

from .modules.translategenius_omni import TranslateGeniusOmni, TranslationRequest


def _parse_glossary(glossary_args: list[str] | None) -> Dict[str, str]:
    glossary: Dict[str, str] = {}
    if not glossary_args:
        return glossary

    for item in glossary_args:
        if "=" not in item:
            raise argparse.ArgumentTypeError(
                "Glossary items must be in the form term=translation"
            )
        term, replacement = item.split("=", 1)
        glossary[term.strip()] = replacement.strip()
    return glossary


def translate_command(args: argparse.Namespace) -> None:
    glossary = _parse_glossary(args.glossary)
    translator = TranslateGeniusOmni(glossary=glossary or None)
    request = TranslationRequest(
        source_language=args.source,
        target_language=args.target,
        content=args.text,
        domain=args.domain,
        tone=args.tone,
    )
    response = translator.translate(request)

    if args.format == "text":
        print(response.translated_content)
    else:
        print(
            json.dumps(
                {
                    "module": response.module,
                    "source_language": response.source_language,
                    "detected_source_language": response.detected_source_language,
                    "target_language": response.target_language,
                    "translated_content": response.translated_content,
                    "confidence": response.confidence,
                    "notes": response.notes,
                },
                ensure_ascii=False,
                indent=2,
            )
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="OmniRosetta command line utilities",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    translate_parser = subparsers.add_parser(
        "translate", help="Run a translation via TranslateGenius Omni"
    )
    translate_parser.add_argument("text", help="Text to translate")
    translate_parser.add_argument(
        "--source",
        default="auto",
        help="Source language code or name (default: auto detect)",
    )
    translate_parser.add_argument(
        "--target",
        required=True,
        help="Target language code or name",
    )
    translate_parser.add_argument(
        "--domain",
        help="Optional domain hint (e.g., legal, medical)",
    )
    translate_parser.add_argument(
        "--tone",
        help="Optional tone hint (e.g., formal, friendly)",
    )
    translate_parser.add_argument(
        "--glossary",
        nargs="*",
        help="Term replacements applied after translation (term=translation)",
    )
    translate_parser.add_argument(
        "--format",
        choices={"text", "json"},
        default="json",
        help="Output format (default: json)",
    )
    translate_parser.set_defaults(func=translate_command)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
