"""Compile project Python files without walking Git internals."""

from __future__ import annotations

import py_compile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_PARTS = {".git", ".venv", "__pycache__", "browser", "logs"}


def iter_python_files() -> list[Path]:
    """Return Python source files that belong to the application/test code."""
    return sorted(
        path
        for path in PROJECT_ROOT.rglob("*.py")
        if not EXCLUDED_PARTS.intersection(path.relative_to(PROJECT_ROOT).parts)
    )


def main() -> None:
    """Compile all project Python files and print each checked path."""
    for path in iter_python_files():
        relative_path = path.relative_to(PROJECT_ROOT)
        print(f"Compiling {relative_path}")
        py_compile.compile(str(path), doraise=True)


if __name__ == "__main__":
    main()
