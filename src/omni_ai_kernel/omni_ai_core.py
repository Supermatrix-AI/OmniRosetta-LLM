"""Core coordination utilities for Omni AI Kernel."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict


@dataclass
class KernelModule:
    name: str
    handler: Callable[..., object]


@dataclass
class OmniAIKernel:
    """Registry for lightweight module handlers."""

    modules: Dict[str, KernelModule] = field(default_factory=dict)

    def register(self, name: str, handler: Callable[..., object]) -> None:
        self.modules[name] = KernelModule(name=name, handler=handler)

    def dispatch(self, name: str, *args, **kwargs) -> object:
        if name not in self.modules:
            raise KeyError(f"Module '{name}' is not registered")
        return self.modules[name].handler(*args, **kwargs)


__all__ = ["KernelModule", "OmniAIKernel"]
