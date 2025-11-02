"""Configuration helpers for the API."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class APIConfig:
    project_name: str = "OmniRosetta API"
    version: str = "0.1.0"


__all__ = ["APIConfig"]
