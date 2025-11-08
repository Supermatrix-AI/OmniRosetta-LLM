"""OmniRosetta package exposing modular AI interface stubs."""

from . import modules
from .cli import build_parser, main

__all__ = ["modules", "build_parser", "main"]
from .github import link_repo

__all__ = ["modules", "link_repo"]
