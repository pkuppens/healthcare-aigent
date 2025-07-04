# Installation Guide

This guide explains how to install and set up the Healthcare AI Agent system for both users and developers.

## Prerequisites

- Python 3.11 (recommended) or Python 3.10/3.12
- Git
- UV package manager (recommended) or pip

> **Note**: Python 3.13 is not yet fully supported due to compatibility issues with langflow and its dependencies.

## Quick Installation (Users)

For users who want to quickly get started:

### 1. Clone the Repository

```bash
git clone https://github.com/pkuppens/healthcare-aigent.git
cd healthcare-aigent
```

### 2. Set Up Environment

```bash
# Create virtual environment
uv venv
# On Windows:
.venv\Scripts\activate
# On Unix/MacOS:
source .venv/bin/activate

# Install dependencies
uv sync --dev
```

### 3. Configure Environment

```bash
# Copy example configuration
cp .env.example .env
# Edit .env with your API keys and preferences
```

### 4. Run the System

```bash
# Start the backend service
python src/main.py

# Or use the entry point (after installation)
healthcare-aigent
```

## Development Installation

For developers who want to contribute or modify the code:

### 1. Clone and Setup

```bash
git clone https://github.com/pkuppens/healthcare-aigent.git
cd healthcare-aigent
```

### 2. Install UV Package Manager

If you don't have UV installed:

```bash
# On Windows
pip install uv

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/MacOS
python -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies

Install the project with development dependencies:

```bash
# Install in editable mode with development dependencies
uv sync --dev
```

This will install:
- All core project dependencies
- Development tools (pytest, ruff, mypy, pre-commit)
- The project itself in editable mode

### 5. Install Pre-commit Hooks

```bash
pre-commit install
```

To verify that the pre-commit hooks are working correctly:

```bash
pre-commit run --all-files
```

### 6. Configure Environment

```bash
cp .env.example .env
# Fill in the appropriate values for the environment variables in the .env file
```

### 7. Test the Setup

Run the tests to verify that everything is installed correctly:

```bash
pytest
```

## Alternative Installation Methods

### Using Pip Instead of UV

If you prefer using pip:

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### Development Container

For a consistent development environment across different machines:

1. Install [Docker](https://www.docker.com/products/docker-desktop/)
2. Install [Visual Studio Code](https://code.visualstudio.com/) or Cursor
3. Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension
4. Open the project and click "Reopen in Container" when prompted

The development container includes Python 3.11, Git, GitHub CLI, UV package manager, and pre-configured extensions.

## Project Structure

The project uses absolute imports throughout:

```
src/
├── __init__.py
├── main.py              # Main entry point
├── agents/              # Agent definitions
├── tasks/               # Task definitions
├── llm_config.py        # LLM configuration
├── utils.py             # Utility functions
└── tools/               # Tool modules
    ├── __init__.py
    ├── medical_tools.py
    ├── web_tools.py
    └── database_tools.py
```

## Running the Application

### Using the Entry Point

After installation, you can run the application using the configured entry point:

```bash
healthcare-aigent
```

### Direct Python Execution

You can also run the main module directly:

```bash
python -m src.main
```

### From the Source File

```bash
python src/main.py
```

## Development Workflow

### Standard Development Process

1. Create a new branch for your feature/fix
2. Install pre-commit hooks (if not already done)
3. Make your changes with appropriate tests
4. Commit your changes (pre-commit hooks will run automatically)
5. Run tests before pushing: `pytest`
6. Create a pull request

### Git Commit Options

**Standard commit (recommended):**
```bash
git add .
git commit -m "Your commit message"
```
This will run all pre-commit hooks before allowing the commit.

**Skip pre-commit hooks (not recommended):**
```bash
git add .
git commit --no-verify -m "Your commit message"
```
Only use this in exceptional cases. Fix any issues before pushing to the repository.

### Running Tests and Linting

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src

# Run linting
python scripts/lint.py

# Or manually with UV
uv run ruff check src/ --fix
uv run ruff format src/

# Or using the entry point (after installation)
lint
```

## Import System

This project uses **absolute imports** throughout. All imports follow the pattern:

```python
# Correct - absolute imports
from src.agents import create_medical_crew
from src.tools.medical_tools import MedicalTerminologyTool

# Incorrect - relative imports (not used)
from .agents import create_medical_crew
from .tools.medical_tools import MedicalTerminologyTool
```

## Troubleshooting

### Import Errors

If you encounter import errors like:
```
ImportError: attempted relative import with no known parent package
```

This means the package is not installed in editable mode. Run:
```bash
uv sync --dev
```

### Module Not Found

If you get "Module not found" errors, ensure:
1. The package is installed in editable mode
2. You're running from the correct directory
3. Your Python path includes the project root

### Environment Issues

Make sure you're using the correct Python environment:
```bash
# Check Python version
python --version

# Check if package is installed
pip list | grep healthcare-aigent

# Verify UV installation
uv --version
```

### Pre-commit Hook Issues

If pre-commit hooks aren't working:
1. Try `pre-commit clean` and reinstall: `pre-commit install`
2. Run manually: `pre-commit run --all-files`
3. Check that your virtual environment is activated

### UV-specific Issues

If you encounter issues with UV:
1. Verify UV is installed and in your PATH: `uv --version`
2. Try reinstalling dependencies: `uv sync --dev --upgrade`
3. For VS Code integration, ensure `python.packageManager` is set to `uv` in settings

## Advanced Setup Options

### Multiple Python Versions

For testing compatibility with different Python versions, you can create separate environments:

```bash
# Create environments for different Python versions
python3.11 -m venv .venv-py3.11
python3.12 -m venv .venv-py3.12

# Activate and install in each
source .venv-py3.11/bin/activate
uv sync --dev
deactivate

source .venv-py3.12/bin/activate
uv sync --dev
deactivate
```

### Using Ansible for Automated Setup

For automated environment setup across multiple machines, see the Ansible playbooks in the `ansible/` directory:

```bash
# Run system setup (requires sudo)
uv run ansible-playbook ansible/playbooks/setup_system.yml --ask-become-pass

# Run Python environment setup
uv run ansible-playbook ansible/playbooks/setup_python_envs.yml
```

For more details, see [docs/Ansible.md](docs/Ansible.md).

## Next Steps

After installation:

1. **Configure your environment**: Edit the `.env` file with your API keys and preferences
2. **Read the documentation**: Check the `docs/` folder for detailed guides
3. **Run test scenarios**: Try `python notebooks/run_crewai_llm.py`
4. **Explore the codebase**: Start with `src/main.py` to understand the entry point

For detailed technical information, see [Technical Implementation](docs/technical_implementation.md). 