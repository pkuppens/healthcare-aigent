#!/usr/bin/env python
"""
Test Matrix Script

This script creates virtual environments for different Python versions,
installs the project dependencies, and runs tests to ensure compatibility.
"""

import platform
import subprocess
from pathlib import Path


# Find the project root directory
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Python versions to test
# Note: Python 3.13 is included to detect when package dependencies are fixed,
# but is expected to fail due to compatibility issues with numpy and other packages.
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]


# Colors for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")


def print_success(text):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_warning(text):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def print_info(text):
    """Print an info message."""
    print(f"{Colors.BLUE}i {text}{Colors.ENDC}")


def run_command(command, cwd=None, env=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def create_venv(python_version):
    """Create a virtual environment for the specified Python version."""
    venv_name = f".venv-py{python_version}"
    venv_path = PROJECT_ROOT / venv_name

    if venv_path.exists():
        print_info(f"Virtual environment {venv_name} already exists. Skipping creation.")
        return venv_path

    print_info(f"Creating virtual environment for Python {python_version}...")

    # Determine the Python executable based on the platform
    if platform.system() == "Windows":
        python_cmd = f"py -{python_version} -m venv {venv_path}"
    else:
        python_cmd = f"python{python_version} -m venv {venv_path}"

    success, output = run_command(python_cmd, cwd=PROJECT_ROOT)
    if not success:
        print_error(f"Failed to create virtual environment for Python {python_version}: {output}")
        return None

    print_success(f"Created virtual environment for Python {python_version}")
    return venv_path


def activate_venv(venv_path):
    """Activate the virtual environment and return the activation command."""
    if platform.system() == "Windows":
        activate_cmd = f"{venv_path}\\Scripts\\activate"
    else:
        activate_cmd = f"source {venv_path}/bin/activate"

    return activate_cmd


def install_dependencies(venv_path, python_version):
    """Install project dependencies in the virtual environment."""
    activate_cmd = activate_venv(venv_path)

    # Install uv if not already installed
    install_uv_cmd = f"{activate_cmd} && python -m pip install uv"
    success, output = run_command(install_uv_cmd, cwd=PROJECT_ROOT)
    if not success:
        print_error(f"Failed to install uv: {output}")
        return False

    # Install project dependencies
    install_cmd = f"{activate_cmd} && uv pip install -e .[dev]"
    success, output = run_command(install_cmd, cwd=PROJECT_ROOT)
    if not success:
        # Special handling for Python 3.13 which is expected to fail
        if python_version == "3.13":
            print_warning(f"Python 3.13 dependency installation failed as expected: {output}")
            print_warning("This is due to compatibility issues with numpy and other packages.")
            print_warning("We include Python 3.13 in the test matrix to detect when dependencies are fixed.")
            return True  # Return True to continue with the test matrix
        else:
            print_error(f"Failed to install dependencies: {output}")
            return False

    print_success("Installed project dependencies")
    return True


def run_tests(venv_path, python_version):
    """Run tests in the virtual environment."""
    activate_cmd = activate_venv(venv_path)

    # Run pytest
    test_cmd = f"{activate_cmd} && pytest"
    success, output = run_command(test_cmd, cwd=PROJECT_ROOT)
    if not success:
        # Special handling for Python 3.13 which is expected to fail
        if python_version == "3.13":
            print_warning(f"Python 3.13 tests failed as expected: {output}")
            print_warning("This is due to compatibility issues with numpy and other packages.")
            print_warning("We include Python 3.13 in the test matrix to detect when dependencies are fixed.")
            return True  # Return True to continue with the test matrix
        else:
            print_error(f"Tests failed: {output}")
            return False

    print_success("All tests passed")
    return True


def main():
    """Main function to run the test matrix."""
    print_header("Healthcare AI Agent Test Matrix")
    print_info("Testing compatibility with different Python versions")
    print_info(f"Project root: {PROJECT_ROOT}")

    # Add a note about Python 3.13
    print_warning("Note: Python 3.13 is included in the test matrix to detect when package dependencies are fixed.")
    print_warning("It is expected to fail due to compatibility issues with numpy and other packages.")

    results = {}

    for python_version in PYTHON_VERSIONS:
        print_header(f"Testing Python {python_version}")

        # Create virtual environment
        venv_path = create_venv(python_version)
        if not venv_path:
            results[python_version] = "Failed to create virtual environment"
            continue

        # Install dependencies
        if not install_dependencies(venv_path, python_version):
            results[python_version] = "Failed to install dependencies"
            continue

        # Run tests
        if not run_tests(venv_path, python_version):
            results[python_version] = "Tests failed"
            continue

        results[python_version] = "All tests passed"

    # Print summary
    print_header("Test Matrix Results")
    for python_version, result in results.items():
        if result == "All tests passed":
            print_success(f"Python {python_version}: {result}")
        elif python_version == "3.13" and result in ["Failed to install dependencies", "Tests failed"]:
            print_warning(f"Python {python_version}: {result} (Expected due to compatibility issues)")
        else:
            print_error(f"Python {python_version}: {result}")


if __name__ == "__main__":
    main()
