"""Utility helpers for applying lightweight post-processing patches."""

def sample_patch_function(content: str) -> str:
    """Append a verification footer when missing."""
    if "# Patched by OCI" not in content:
        content += "\n\n# Patched by OCI - Verified"
    return content
