"""Read-only Git metadata for imported projects."""
import os
from pathlib import Path
import shutil
import subprocess


def current_branch(root):
    """Return the checked-out branch, or None for non-Git/detached projects."""
    executable = shutil.which("git")
    if not executable:
        return None
    try:
        result = subprocess.run(
            [executable, "-C", str(Path(root)), "symbolic-ref", "--quiet", "--short", "HEAD"],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8", errors="replace", timeout=2,
            creationflags=0x08000000 if os.name == "nt" else 0,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    branch = result.stdout.strip()
    return branch or None
