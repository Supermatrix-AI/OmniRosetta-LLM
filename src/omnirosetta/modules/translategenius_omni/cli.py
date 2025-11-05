"""Command-line interface for the TranslateGenius Omni module.

The CLI is intentionally dependency-light so that contributors can quickly test
multilingual flows without provisioning heavyweight model checkpoints.  It is
implemented as a thin wrapper over :class:`TranslateGeniusOmni` and mirrors the
structured response emitted by the module.
"""

from __future__ import annotations

import argparse
import sys
from typing import Iterable, Optional

from . import TranslateGeniusOmni, TranslationRequest


def build_parser() -> argparse.ArgumentParser:
    """Return an :class:`argparse.ArgumentParser` configured for the CLI."""

    parser = argparse.ArgumentParser(
        description="Run the TranslateGenius Omni lightweight translator.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("text", help="Input text to translate")
    parser.add_argument("--target", required=True, help="Target language code (e.g. es, fr, ta)")
    parser.add_argument("--source", help="Optional source language code")
    parser.add_argument("--context", help="Optional context string for logging")
    parser.add_argument(
        "--metadata",
        nargs="*",
        default=(),
        help="Optional key=value pairs that annotate the translation request.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON instead of returning a minified payload.",
    )
    return parser


def parse_metadata(pairs: Iterable[str]) -> dict:
    """Parse key=value metadata entries from the CLI."""

    metadata = {}
    for entry in pairs:
        if "=" not in entry:
            raise SystemExit(f"Invalid metadata entry '{entry}'. Expected format key=value")
        key, value = entry.split("=", 1)
        metadata[key] = value
    return metadata


def main(argv: Optional[Iterable[str]] = None) -> int:
    """Entry-point used by ``python -m`` and console scripts."""

    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    translator = TranslateGeniusOmni()
    metadata = parse_metadata(args.metadata)
    request = TranslationRequest(
        source_language=args.source,
        target_language=args.target,
        content=args.text,
        context=args.context,
        metadata=metadata,
    )

    response = translator.translate(request)
    json_payload = response.to_json(indent=2 if args.pretty else None)
    print(json_payload)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
