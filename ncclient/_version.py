"""Version compatibility shim for ncclient.

This keeps the historical ``get_versions()['version']`` API while using
hatch-vcs as the build backend source of truth.
"""

from __future__ import annotations

from importlib import metadata
from pathlib import Path
import re
import subprocess
from typing import Any, Dict, Optional


def _from_installed_metadata() -> Optional[str]:
    try:
        return metadata.version("ncclient")
    except metadata.PackageNotFoundError:
        return None


def _from_git_describe() -> str:
    root = Path(__file__).resolve().parents[1]
    try:
        described = subprocess.check_output(
            [
                "git",
                "describe",
                "--tags",
                "--long",
                "--dirty",
                "--always",
                "--match",
                "v[0-9]*",
            ],
            cwd=str(root),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return "0+unknown"

    match = re.match(
        r"^v(?P<tag>\d+(?:\.\d+)*)((?:-(?P<distance>\d+)-g(?P<sha>[0-9a-f]+))?)(?P<dirty>-dirty)?$",
        described,
    )
    if not match:
        return "0+unknown"

    tag = match.group("tag")
    distance = match.group("distance")
    sha = match.group("sha")
    dirty = match.group("dirty")

    if distance is None or sha is None:
        return tag

    local = f"{distance}.g{sha}"
    if dirty:
        local = f"{local}.dirty"
    return f"{tag}+{local}"


def get_versions() -> Dict[str, Any]:
    version = _from_installed_metadata() or _from_git_describe()
    return {
        "version": version,
        "full-revisionid": None,
        "dirty": ".dirty" in version,
        "error": None,
        "date": None,
    }
