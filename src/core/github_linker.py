"""Utilities for linking the local repository to a GitHub remote.

The :func:`link_repo` helper performs basic validation on the provided
repository information, configures the git remote and persists a small
metadata record so the project can report which remote it is associated
with.  Access tokens are never persisted in plain text; only a hash and a
redacted preview are stored for auditing purposes.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


_REPO_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
_USER_PATTERN = re.compile(r"^[A-Za-z0-9-]+$")
_TOKEN_PATTERN = re.compile(r"^gh[pous]_[A-Za-z0-9]{20,}$")


@dataclass
class LinkResult:
    """Summary of the link operation."""

    remote: str
    remote_name: str
    repo_path: Path
    token_hint: str
    recorded: bool

    def as_dict(self) -> Dict[str, str]:
        return {
            "remote": self.remote,
            "remote_name": self.remote_name,
            "repo_path": str(self.repo_path),
            "token_hint": self.token_hint,
            "recorded": str(self.recorded).lower(),
        }


def _redact_token(token: str) -> str:
    visible = 4
    if len(token) <= visible * 2:
        return "*" * len(token)
    return f"{token[:visible]}{'*' * (len(token) - 2 * visible)}{token[-visible:]}"


def _repo_root(start: Optional[Path] = None) -> Path:
    path = Path(start or __file__).resolve()
    for candidate in [path] + list(path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise FileNotFoundError("Unable to determine repository root — '.git' not found.")


def _load_records(store_path: Path) -> Dict[str, List[Dict[str, str]]]:
    if not store_path.exists():
        return {"links": []}
    try:
        with store_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Existing link registry is not valid JSON: {store_path}") from exc


def _write_records(store_path: Path, records: Dict[str, List[Dict[str, str]]]) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    with store_path.open("w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=2, sort_keys=True)
        fh.write("\n")


def _update_registry(
    store_path: Path,
    repo_name: str,
    user: str,
    remote_url: str,
    token: str,
) -> bool:
    records = _load_records(store_path)
    entry = {
        "repo": repo_name,
        "user": user,
        "remote": remote_url,
        "token_hash": hashlib.sha256(token.encode("utf-8")).hexdigest(),
        "token_hint": _redact_token(token),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    existing = next((item for item in records["links"] if item["repo"] == repo_name and item["user"] == user), None)
    if existing:
        if existing == entry:
            return False
        records["links"] = [item if item is not existing else entry for item in records["links"]]
    else:
        records["links"].append(entry)
    _write_records(store_path, records)
    return True


def _configure_remote(repo_path: Path, remote_name: str, remote_url: str) -> None:
    get_cmd = ["git", "remote", "get-url", remote_name]
    result = subprocess.run(
        get_cmd,
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        set_cmd = ["git", "remote", "set-url", remote_name, remote_url]
        subprocess.run(set_cmd, cwd=repo_path, check=True)
    else:
        add_cmd = ["git", "remote", "add", remote_name, remote_url]
        subprocess.run(add_cmd, cwd=repo_path, check=True)


def link_repo(
    repo_name: str,
    github_token: str,
    user: str,
    *,
    remote_name: str = "origin",
    repo_path: Optional[Path] = None,
    registry_path: Optional[Path] = None,
) -> LinkResult:
    """Link the current repository to a GitHub remote.

    Parameters
    ----------
    repo_name:
        The GitHub repository name.
    github_token:
        A GitHub personal access token. Only a hashed representation is
        stored to avoid leaking secrets.
    user:
        The GitHub username or organisation that owns the repository.
    remote_name:
        Which git remote name to configure. Defaults to ``origin``.
    repo_path:
        Optional override for the repository root. If omitted the
        function walks up from the current file to locate ``.git``.
    registry_path:
        Optional override for where the link metadata should be stored.

    Returns
    -------
    LinkResult
        A dataclass describing the configured remote and whether the
        metadata registry was updated.
    """

    if not repo_name or not _REPO_PATTERN.fullmatch(repo_name):
        raise ValueError("repo_name must contain only alphanumeric characters, dots, underscores or hyphens.")
    if not user or not _USER_PATTERN.fullmatch(user):
        raise ValueError("user must contain only alphanumeric characters or hyphens.")
    if not github_token or not _TOKEN_PATTERN.fullmatch(github_token):
        raise ValueError("github_token does not match the expected GitHub token format.")

    root = _repo_root(repo_path)
    remote_url = f"https://github.com/{user}/{repo_name}.git"
    _configure_remote(root, remote_name, remote_url)

    registry = registry_path or (root / "config" / "github_links.json")
    recorded = _update_registry(registry, repo_name, user, remote_url, github_token)

    return LinkResult(
        remote=remote_url,
        remote_name=remote_name,
        repo_path=root,
        token_hint=_redact_token(github_token),
        recorded=recorded,
    )


__all__ = ["link_repo", "LinkResult"]
