"""GitHub integration utilities for OmniRosetta."""

from __future__ import annotations

from typing import Dict, Union

import requests

ResponseDict = Dict[str, Union[str, bool]]


def link_repo(repo_name: str, github_token: str, user: str = "supermatrix-ai", branch: str = "main") -> ResponseDict:
    """Link GPT OCI to a GitHub repository to enable code exploration and editing.

    Parameters
    ----------
    repo_name:
        Name of the GitHub repository (e.g., "omnirosetta-llm").
    github_token:
        Personal access token with ``repo`` access permissions.
    user:
        GitHub username or organization that owns the repository. Defaults to "supermatrix-ai".
    branch:
        Repository branch to interact with. Defaults to "main".

    Returns
    -------
    dict
        Metadata confirming repository linkage and current HEAD information. Contains an ``"error"``
        key when the repository could not be linked.
    """

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    repo_url = f"https://api.github.com/repos/{user}/{repo_name}"

    try:
        response = requests.get(repo_url, headers=headers, timeout=10)
    except requests.RequestException as exc:  # pragma: no cover - network issues
        return {"error": f"Failed to reach GitHub API: {exc}"}

    if response.status_code != 200:
        return {"error": f"Repository '{repo_name}' not found or token invalid."}

    repo_data = response.json()
    default_branch = repo_data.get("default_branch", "main")
    target_branch = branch or default_branch

    branch_url = f"https://api.github.com/repos/{user}/{repo_name}/branches/{target_branch}"
    branch_response = requests.get(branch_url, headers=headers, timeout=10)

    if branch_response.status_code != 200:
        return {"error": f"Branch '{target_branch}' not found."}

    commit_sha = branch_response.json()["commit"]["sha"]

    return {
        "linked": True,
        "repo": f"{user}/{repo_name}",
        "branch": target_branch,
        "head_commit": commit_sha,
        "message": (
            f"Connected to repository '{repo_name}' at branch '{target_branch}' "
            f"(HEAD: {commit_sha})"
        ),
    }


__all__ = ["link_repo"]
