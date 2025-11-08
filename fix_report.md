# TranslateGenius Omni remediation summary

- **Structure:** Consolidated the historical `src/translate_genius/translategenius_omni.py` shim with the modern implementation and exposed CLI entry-points via `src/omnirosetta/cli.py`.
- **Dependencies:** Declared `pytest` under optional development and testing extras for consistent local validation.
- **Imports:** Centralised exports in `omnirosetta.__init__` and guarded re-export modules with `__all__` definitions.
- **Errors:** Added explicit exception types for unsupported languages and empty payloads, ensuring downstream agents can catch translation failures.
- **Actions:** Implemented a command line workflow supporting glossary overrides and JSON output, mirroring the requested CLI refresh.
- **API:** Delivered dataclass-based request/response models, deterministic translation memory, language auto-detection and batch helpers with comprehensive unit tests.
