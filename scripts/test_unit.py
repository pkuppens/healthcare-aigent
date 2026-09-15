#!/usr/bin/env python3
"""Run the unit test suite (used by pre-commit and `uv run test-unit`).

Runs pytest in a subprocess with PYTHONUTF8=1 set. On Windows, `crewai`
transitively imports `litellm`, which opens a bundled JSON file without an
explicit encoding; without UTF-8 mode, Python falls back to the system
codepage (cp1252) and the import crashes with a UnicodeDecodeError before
any test runs. PYTHONUTF8 only takes effect if set before the interpreter
starts, so this has to launch a subprocess rather than set os.environ and
call pytest directly in-process.
"""

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).parent.parent

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    result = subprocess.run(["uv", "run", "pytest", "tests/unit", "-q"], cwd=project_root, env=env, check=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
