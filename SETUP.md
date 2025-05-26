# Development Setup

This document describes how to set up the development environment for this project.

## Requirements

- Python 3.11 (recommended) or Python 3.10/3.12
- Git
- uv (Python package manager) - Install from https://github.com/astral-sh/uv

> **Note**: Python 3.13 is not yet fully supported due to compatibility issues with langflow and its dependencies.
We include it in our test matrix to detect when these issues are resolved.

## Option 1: Local Setup

### Step 1: Clone the repository

```bash
git clone https://github.com/pkuppens/healthcare-aigent.git
cd healthcare-aigent
```

### Step 2: Set up uv (Windows)

To make uv your default package manager on Windows, you can:

1. Add uv to your PATH if not already done
2. Create a PowerShell profile (if you don't have one):
```powershell
if (!(Test-Path -Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}
```

3. Add these aliases to your PowerShell profile ($PROFILE):
```powershell
Set-Alias -Name pip -Value uv
Set-Alias -Name python -Value uv
```

4. Restart your PowerShell or run:
```powershell
. $PROFILE
```

### Step 3: Create a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/MacOS
python -m venv .venv
source .venv/bin/activate
```

### Step 4: Install dependencies

Install the project with development dependencies:

```bash
uv sync --dev
```

This will install:
- All core project dependencies
- Development tools (pytest, ruff, mypy, pre-commit)
- The project itself in editable mode

### Step 5: Install pre-commit hooks

```bash
pre-commit install
```

To verify that the pre-commit hooks are working correctly, run:

```bash
pre-commit run --all-files
```

This will run the following checks on all files:
- ruff: Python linter and formatter
- ruff-format: Code formatting

### Step 6: Copy the .env file

```bash
cp .env.example .env
```

Fill in the appropriate values for the environment variables in the `.env` file.

### Step 7: Test the setup

Run the tests to verify that everything is installed correctly:

```bash
pytest
```

## Option 2: Development Container

For a consistent development environment across different machines and operating systems, you can use the included development container configuration.

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension for VS Code

### Setup

1. Open the project in VS Code
2. Click the "Reopen in Container" button when prompted, or use the command palette (F1) and select "Remote-Containers: Reopen in Container"
3. VS Code will build the container and set up the development environment

The development container includes:
- Python 3.11
- Git
- GitHub CLI
- UV package manager
- Pre-configured VS Code extensions and settings

## Option 3: Test Matrix

To test compatibility with different Python versions, you can use the included test matrix script.

### Prerequisites

- Multiple Python versions installed (3.10, 3.11, 3.12)
- UV package manager

### Running the Test Matrix

```bash
python tests/test_matrix.py
```

This script will:
1. Create separate virtual environments for each Python version
2. Install the project dependencies using `uv`
3. Run the tests in each environment
4. Provide a summary of the results

## Using UV with VS Code

To configure VS Code to use UV instead of pip:

1. Install the UV package manager if you haven't already:
   ```bash
   pip install uv
   ```

2. Configure VS Code to use UV as the package manager:
   - Open VS Code settings (File > Preferences > Settings)
   - Search for "python.packageManager"
   - Set it to "uv"

3. When creating a new virtual environment, VS Code will now use UV instead of pip.

4. For existing projects, you can manually install dependencies with UV:
   ```bash
   uv sync --dev
   ```

### Troubleshooting UV with VS Code

If you encounter issues with VS Code using UV:

1. **VS Code doesn't recognize UV**: Make sure UV is installed and in your PATH. You can verify this by running `uv --version` in a terminal.

2. **Package installation fails**: Try running the installation command manually in a terminal to see the error message.

3. **VS Code still uses pip**: Check your VS Code settings to ensure `python.packageManager` is set to `uv`. You may need to restart VS Code after changing this setting.

4. **Virtual environment issues**: If VS Code creates a virtual environment with pip instead of UV, you can manually create a virtual environment and then point VS Code to it:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # or source .venv/bin/activate on Unix/MacOS
   uv sync --dev
   ```
   Then in VS Code, select the Python interpreter from the `.venv` directory.

## Python Version

For detailed information about Python version requirements and recommendations, see [Development Environment](docs/development_environment.md#python-version).

## Troubleshooting

If you encounter any issues during setup:

1. Verify that your Python version meets the requirements (3.11 recommended)
2. Ensure your virtual environment is activated
3. Try reinstalling dependencies with `uv sync --dev --upgrade`
4. If pre-commit hooks aren't working, try `pre-commit clean` and reinstall

## Development workflow

1. Create a new branch for your feature/fix
2. Install pre-commit hooks (step 5)
3. Commit your changes (pre-commit hooks will run automatically)
4. Run tests before pushing
5. Create a pull request

## Git commit options

### Standard commit (recommended)
```bash
git add .
git commit -m "Your commit message"
```
This will run all pre-commit hooks before allowing the commit.

### Skip pre-commit hooks (not recommended)
```bash
git add .
git commit --no-verify -m "Your commit message"
```
This will skip all pre-commit hooks. Only use this in exceptional cases where you need to commit code that doesn't meet the project's standards. Remember to fix any issues before pushing to the repository, especially on the main branch.