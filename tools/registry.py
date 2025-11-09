"""Utility helpers for OmniRosetta tool and module registries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_REGISTRY_PATH = PROJECT_ROOT / "config" / "module_links.json"


TOOLS: Dict[str, str] = {
    "web_search": "duckduckgo-search",
    "code_exec": "python-sandbox",
    "doc_reader": "pdfplumber",
    "forecast": "chronopredict",
    "decode": "diwa15_rosetta",
}


def load_module_registry(path: Path = MODULE_REGISTRY_PATH) -> Dict[str, Dict[str, str]]:
    """Load module metadata from the JSON registry file."""

    if not path.exists():
        return {}

    data = json.loads(path.read_text())
    modules = data.get("modules", [])
    if not isinstance(modules, list):  # pragma: no cover - defensive guard
        raise ValueError("The module registry must contain a 'modules' list.")

    registry: Dict[str, Dict[str, str]] = {}
    for entry in modules:
        if not isinstance(entry, dict):
            continue
        module_name = entry.get("module")
        if not module_name:
            continue
        registry[module_name] = entry

    return registry
