"""Command-line utility for registering OmniRosetta modules.

This script centralizes the bookkeeping for external repositories and
local entry points that power OmniRosetta's modular architecture.

Running the command updates ``config/module_links.json`` with metadata
about a module.  The resulting registry can be consumed by other tools
or documentation generators that need to know where each component
lives and how it should be described.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = PROJECT_ROOT / "config" / "module_links.json"


@dataclass
class ModuleLink:
    """Metadata describing how a module is linked into the project."""

    module: str
    repo: str
    branch: str
    path: str
    desc: str
    license: str
    ethics: str
    contact: str

    def to_serializable(self) -> Dict[str, str]:
        """Return a JSON-serializable representation of the metadata."""

        return asdict(self)


class ModuleRegistry:
    """Simple JSON-backed storage for module link metadata."""

    def __init__(self, registry_path: Path = DEFAULT_REGISTRY_PATH) -> None:
        self.registry_path = registry_path
        self._data: Dict[str, List[Dict[str, str]]] = {"modules": []}
        self._load()

    def _load(self) -> None:
        if not self.registry_path.exists():
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            return

        try:
            self._data = json.loads(self.registry_path.read_text())
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
            raise ValueError(
                f"Malformed JSON in registry file: {self.registry_path}"
            ) from exc

        if not isinstance(self._data, dict):
            raise ValueError(
                "Module registry must be a JSON object with a 'modules' list."
            )

        modules = self._data.setdefault("modules", [])
        if not isinstance(modules, list):
            raise ValueError("The 'modules' entry in the registry must be a list.")

    def update(self, module_link: ModuleLink) -> bool:
        """Insert or update the supplied module metadata.

        Returns ``True`` when a new module was added and ``False`` when an
        existing entry was updated.
        """

        modules = self._data.setdefault("modules", [])
        assert isinstance(modules, list)

        for index, entry in enumerate(modules):
            if not isinstance(entry, dict):
                continue
            if entry.get("module") == module_link.module:
                modules[index] = module_link.to_serializable()
                return False

        modules.append(module_link.to_serializable())
        return True

    def write(self) -> None:
        self.registry_path.write_text(
            json.dumps(self._data, indent=2, sort_keys=True) + "\n"
        )


def link_module(
    module: str,
    repo: str,
    branch: str,
    path: str,
    desc: str,
    license: str,
    ethics: str,
    contact: str,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
) -> None:
    """Register a module and display a friendly summary."""

    module_path = Path(path)
    if not module_path.is_absolute():
        module_path = (PROJECT_ROOT / module_path).resolve()

    try:
        stored_path = str(module_path.relative_to(PROJECT_ROOT))
    except ValueError:
        stored_path = str(module_path)

    module_link = ModuleLink(
        module=module,
        repo=repo,
        branch=branch,
        path=stored_path,
        desc=desc,
        license=license,
        ethics=ethics,
        contact=contact,
    )

    registry = ModuleRegistry(registry_path)
    created = registry.update(module_link)
    registry.write()

    status = "created" if created else "updated"
    print(f"🔗 Linking module: {module_link.module} ({status})")
    print(f"📂 Repo: {module_link.repo} ({module_link.branch})")
    print(f"📁 Path: {module_link.path}")
    print(f"📝 Description: {module_link.desc}")
    print(f"📜 License: {module_link.license} | 🌐 Ethics: {module_link.ethics}")
    print(f"✉️ Contact: {module_link.contact}")
    print(f"💾 Registry: {registry_path}")

    if not module_path.exists():
        print(
            "⚠️  Warning: the provided path does not exist on disk. "
            "Ensure the module directory has been created."
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Register or update OmniRosetta module metadata",
    )
    parser.add_argument("--module", required=True, help="Module identifier")
    parser.add_argument("--repo", required=True, help="Source repository URL")
    parser.add_argument("--branch", required=True, help="Repository branch name")
    parser.add_argument(
        "--path",
        required=True,
        help="Path to the module within this repository (relative or absolute)",
    )
    parser.add_argument("--desc", required=True, help="Human-readable description")
    parser.add_argument("--license", required=True, help="License identifier")
    parser.add_argument(
        "--ethics", required=True, help="Ethics or compliance designation"
    )
    parser.add_argument("--contact", required=True, help="Maintainer contact info")
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY_PATH,
        help="Optional override for the registry file location",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = vars(parser.parse_args())
    registry_path = args.pop("registry")
    link_module(registry_path=registry_path, **args)


if __name__ == "__main__":
    main()
import argparse

def link_module(module, repo, branch, path, desc, license, ethics, contact):
    print(f"🔗 Linking module: {module}")
    print(f"📂 Repo: {repo} ({branch})")
    print(f"📁 Path: {path}")
    print(f"📝 Description: {desc}")
    print(f"📜 License: {license} | 🌐 Ethics: {ethics}")
    print(f"✉️ Contact: {contact}")
    # Add GitHub API integration, pull check, or automation logic here


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--module")
    parser.add_argument("--repo")
    parser.add_argument("--branch")
    parser.add_argument("--path")
    parser.add_argument("--desc")
    parser.add_argument("--license")
    parser.add_argument("--ethics")
    parser.add_argument("--contact")
    args = parser.parse_args()

    link_module(**vars(args))
