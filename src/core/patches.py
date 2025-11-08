"""Utility helpers for lightweight content patching operations."""


def gpt_patch_bugfix(content: str) -> str:
    """Ensure the OCI patch marker is present in ``content``.

    Args:
        content: The textual content to patch.

    Returns:
        The patched content. If the marker is already present the text is
        returned unchanged; otherwise, the marker is appended.
    """

    marker = "# Patched by OCI"
    if marker not in content:
        content = f"{content}\n\n{marker}: Resolved logic issue"
    return content
