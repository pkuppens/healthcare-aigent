#!/usr/bin/env python3
"""Linting script for the healthcare-aigent project."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status.

    Args:
        cmd: Command to run as list of strings
        description: Description of what the command does

    Returns:
        True if command succeeded, False otherwise
    """
    print(f"Running {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error in {description}:")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def main():
    """Main linting function."""
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"

    print(f"Linting project at: {project_root}")
    print(f"Source directory: {src_path}")

    # Change to project root
    import os

    os.chdir(project_root)

    success = True

    # Run Ruff check with auto-fix
    if not run_command(["uv", "run", "ruff", "check", "src/", "--fix"], "Ruff check with auto-fix"):
        success = False

    # Run Ruff formatter
    if not run_command(["uv", "run", "ruff", "format", "src/"], "Ruff formatting"):
        success = False

    # Final check without auto-fix
    if not run_command(["uv", "run", "ruff", "check", "src/"], "Final Ruff check"):
        success = False

    if success:
        print("\n✅ All linting checks passed!")
        return 0
    else:
        print("\n❌ Some linting checks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
