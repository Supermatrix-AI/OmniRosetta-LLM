"""User-facing helpers that bridge to the OmniRosetta TranslateGenius module."""

from typing import Any, Dict, Iterable, Optional

from omnirosetta.modules.translategenius_omni import (
    TranslateGeniusOmni as OmniModule,
    TranslationRequest,
)


class TranslateGeniusOmni:
    """Facade exposing a simplified translation call pattern."""

    def __init__(self, module: Optional[OmniModule] = None) -> None:
        self.module = module or OmniModule()

    def translate(
        self,
        text: str,
        target_language: str,
        *,
        source_language: str = "auto",
        script_sample: Optional[str] = None,
        script_context: Optional[Dict[str, Any]] = None,
        knowledge_domains: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        """Invoke the OmniRosetta translator with ergonomic defaults."""

        request = TranslationRequest(
            source_language=source_language,
            target_language=target_language,
            content=text,
            script_sample=script_sample,
            script_context=dict(script_context or {}),
            knowledge_domains=list(knowledge_domains or []),
        )
        return self.module.translate(request)
