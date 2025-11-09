"""Utility helpers for applying patches to GitHub repositories via the REST API."""

from __future__ import annotations

import base64
from typing import Callable, Dict, Optional

import requests


def connect_and_patch_github_repo(
    repo_name: str,
    github_token: str,
    username: str = "supermatrix-ai",
    branch: str = "main",
    target_file_path: str = "src/omnirosetta/modules/diwa15_rosetta/__init__.py",
    patch_function: Optional[Callable[[str], str]] = None,
    commit_message: str = "OCI patch via Codex Command",
) -> Dict[str, str]:
    """Fetch a file from GitHub, apply a patch, and commit the result.

    Parameters
    ----------
    repo_name:
        Repository name (e.g., ``"omnirosetta-llm"``).
    github_token:
        GitHub personal access token that authorizes the requests.
    username:
        GitHub username or organisation that owns the repository.
    branch:
        Target branch for the patch.
    target_file_path:
        Path of the file to update inside the repository.
    patch_function:
        Callable that accepts the original file content and returns the
        modified content. If ``None`` is provided, the function returns an
        error.
    commit_message:
        Commit message to use when updating the file.

    Returns
    -------
    dict
        Dictionary describing the outcome of the patch operation. Contains an
        ``error`` key when the request fails.
    """

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    if patch_function is None:
        return {"error": "No patch function provided."}

    file_url = (
        f"https://api.github.com/repos/{username}/{repo_name}/contents/{target_file_path}?ref={branch}"
    )
    response = requests.get(file_url, headers=headers, timeout=30)
    if response.status_code != 200:
        return {"error": "Failed to fetch file.", "details": response.json()}

    file_data = response.json()
    sha = file_data["sha"]
    original_content = base64.b64decode(file_data["content"]).decode("utf-8")

    patched_content = patch_function(original_content)
    if patched_content == original_content:
        return {"status": "No changes made to the file."}

    update_response = requests.put(
        file_url,
        headers=headers,
        json={
            "message": commit_message,
            "content": base64.b64encode(patched_content.encode("utf-8")).decode("utf-8"),
            "sha": sha,
            "branch": branch,
        },
        timeout=30,
    )

    if update_response.status_code != 200:
        return {"error": "Failed to commit change.", "details": update_response.json()}

    commit_sha = update_response.json().get("commit", {}).get("sha", "")
    return {
        "status": "Patch applied successfully",
        "file": target_file_path,
        "commit": commit_sha,
        "message": commit_message,
    }
