"""Test to check if we're using a uv-based virtual environment."""

import os
import subprocess
import sys


def test_uv_environment():
    """Check if we're using a uv-based virtual environment."""
    # Check if we're in a virtual environment
    assert sys.prefix != sys.base_prefix, "Not running in a virtual environment"

    # Check if the virtual environment is in the expected location
    venv_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".venv"))
    assert sys.prefix.startswith(venv_path), f"Virtual environment not in expected location: {venv_path}"

    # Try to run uv to check if it's installed
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=True)
        assert result.returncode == 0, "uv is not installed or not working"
        print(f"uv version: {result.stdout.strip()}")
    except FileNotFoundError as err:
        print("uv is not installed or not in PATH")
        raise AssertionError("uv is not installed or not in PATH") from err
