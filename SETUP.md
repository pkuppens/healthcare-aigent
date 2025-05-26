# Development Setup

This document describes advanced development setup options and tools for this project. For basic installation instructions, see [INSTALL.md](INSTALL.md).

## Requirements

- Python 3.11 (recommended) or Python 3.10/3.12
- Git
- UV package manager - Install from https://github.com/astral-sh/uv

> **Note**: Python 3.13 is not yet fully supported due to compatibility issues with langflow and its dependencies.
We include it in our test matrix to detect when these issues are resolved.

## Basic Development Setup

For standard development setup, follow the [Development Installation](INSTALL.md#development-installation) section in the main installation guide.

## Advanced Development Options

### Option 1: Multiple Python Version Testing

For testing compatibility across different Python versions:

#### Prerequisites

- Multiple Python versions installed (3.10, 3.11, 3.12)
- UV package manager

#### Setup Multiple Environments

```bash
# Create environments for different Python versions
python3.10 -m venv .venv-py3.10
python3.11 -m venv .venv-py3.11
python3.12 -m venv .venv-py3.12

# Install dependencies in each environment
for version in 3.10 3.11 3.12; do
    source .venv-py$version/bin/activate
    uv sync --dev
    deactivate
done
```

#### Running the Test Matrix

```bash
python tests/test_matrix.py
```

This script will:
1. Create separate virtual environments for each Python version
2. Install the project dependencies using `uv`
3. Run the tests in each environment
4. Provide a summary of the results

### Option 2: Development Container

For a consistent development environment across different machines and operating systems, you can use the included development container configuration.

#### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Visual Studio Code](https://code.visualstudio.com/) or Cursor
- [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension

#### Setup

1. Open the project in VS Code or Cursor
2. Click the "Reopen in Container" button when prompted, or use the command palette (F1) and select "Remote-Containers: Reopen in Container"
3. The editor will build the container and set up the development environment

The development container includes:
- Python 3.11
- Git
- GitHub CLI
- UV package manager
- Pre-configured editor extensions and settings

For more details, see [.devcontainer/README.md](.devcontainer/README.md).

### Option 3: Automated Setup with Ansible

For automated environment setup across multiple machines, use the included Ansible playbooks.

#### Prerequisites

- Ansible installed
- Sudo access (for system package installation)

#### Setup

```bash
# Run system setup (installs Python versions and UV)
uv run ansible-playbook ansible/playbooks/setup_system.yml --ask-become-pass

# Run Python environment setup (creates virtual environments)
uv run ansible-playbook ansible/playbooks/setup_python_envs.yml
```

For detailed Ansible setup instructions, see [docs/Ansible.md](docs/Ansible.md).

## UV Package Manager Configuration

### Setting UV as Default (Windows)

To make UV your default package manager on Windows:

1. Add UV to your PATH if not already done
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

### Using UV with VS Code/Cursor

To configure your editor to use UV instead of pip:

1. Install the UV package manager if you haven't already:
   ```bash
   pip install uv
   ```

2. Configure the editor to use UV as the package manager:
   - Open editor settings (File > Preferences > Settings)
   - Search for "python.packageManager"
   - Set it to "uv"

3. When creating a new virtual environment, the editor will now use UV instead of pip.

4. For existing projects, you can manually install dependencies with UV:
   ```bash
   uv sync --dev
   ```

#### Troubleshooting UV with Editors

If you encounter issues:

1. **Editor doesn't recognize UV**: Make sure UV is installed and in your PATH. Verify with `uv --version`.

2. **Package installation fails**: Try running the installation command manually in a terminal to see the error message.

3. **Editor still uses pip**: Check your editor settings to ensure `python.packageManager` is set to `uv`. You may need to restart the editor.

4. **Virtual environment issues**: If the editor creates a virtual environment with pip instead of UV, manually create one and point the editor to it:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # or source .venv/bin/activate on Unix/MacOS
   uv sync --dev
   ```
   Then select the Python interpreter from the `.venv` directory in your editor.

## Development Workflow

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality. These are automatically installed during development setup.

To run pre-commit hooks manually:
```bash
pre-commit run --all-files
```

The hooks include:
- ruff: Python linter and formatter
- ruff-format: Code formatting

### Git Commit Options

#### Standard commit (recommended)
```bash
git add .
git commit -m "Your commit message"
```
This will run all pre-commit hooks before allowing the commit.

#### Skip pre-commit hooks (not recommended)
```bash
git add .
git commit --no-verify -m "Your commit message"
```
This will skip all pre-commit hooks. Only use this in exceptional cases where you need to commit code that doesn't meet the project's standards. Remember to fix any issues before pushing to the repository, especially on the main branch.

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_specific.py
```

### Linting and Formatting

```bash
# Using the provided script (recommended)
python scripts/lint.py

# Or manually with UV
uv run ruff check src/ --fix
uv run ruff format src/

# Or using the entry point (after installation)
lint
```

## Troubleshooting Development Setup

### Common Issues

1. **Python version not found**: Verify that your Python version meets the requirements (3.11 recommended)
2. **Virtual environment activation fails**: Ensure your virtual environment is created correctly
3. **Dependency installation fails**: Try reinstalling with `uv sync --dev --upgrade`
4. **Pre-commit hooks not working**: Try `pre-commit clean` and reinstall with `pre-commit install`

### Environment Verification

```bash
# Check Python version
python --version

# Check UV installation
uv --version

# Check virtual environment
which python  # Should point to your virtual environment

# Check installed packages
pip list | grep healthcare-aigent
```

## Python Version Details

For detailed information about Python version requirements and recommendations, see [Development Environment](docs/development_environment.md#python-version).

## Related Documentation

- [Installation Guide](INSTALL.md) - Basic installation instructions
- [Technical Implementation](docs/technical_implementation.md) - Architecture and implementation details
- [Ansible Setup](docs/Ansible.md) - Automated environment setup
- [Development Container](.devcontainer/README.md) - Container-based development