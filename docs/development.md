# Development Guidelines

## Code Quality

### Linting and Formatting
```bash
# Check code with ruff
ruff check .

# Format code with ruff
ruff format .

# Type checking with mypy
mypy src/
```

### Pre-commit Hooks
The project uses pre-commit hooks to ensure code quality before commits:
```yaml
# .pre-commit-config.yaml
repos:
-   repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
    -   id: ruff
        args: [--fix]
    -   id: ruff-format
```

### Configuration Files
- `pyproject.toml`: Project metadata and tool configurations
- `.ruff.toml`: Ruff linting and formatting rules
- `mypy.ini`: Type checking configuration

## Package Management with UV

This project uses `uv` for package management, which is significantly faster than traditional `pip`. UV is configured in the following ways:

1. **Project Configuration**: The `pyproject.toml` file includes UV configuration:
   ```toml
   [tool.uv]
   required-version = ">=0.1.0"
   resolution = "highest"
   compile-bytecode = true
   ```

2. **Environment Variables**: The `.env` file includes:
   ```
   UV_PYTHON=3.11
   ```

3. **Global Configuration**: A `.uvrc` file in the project root:
   ```
   [uv]
   python = "3.11"
   ```

4. **VS Code Configuration**: The `.vscode/settings.json` file includes:
   ```json
   "python.packageManager": "uv",
   "python.terminal.activateEnvironment": true
   ```

### Using UV with VS Code

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
   uv pip install -e ".[dev]"
   ```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit      # Unit tests only
pytest -m integration  # Integration tests only
pytest -m llm       # LLM tests only

# Generate coverage report
pytest --cov=src --cov-report=html
```

### Test Configuration
```ini
# tests/pytest.ini
[pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    llm: LLM connectivity tests
testpaths = tests
python_files = test_*.py
```

### Test Categories
See [Testing Strategy](testing.md) for detailed information about:
- Unit Tests
- Integration Tests
- LLM Tests
- Test Examples
- Best Practices

## Development Workflow

1. **Setup**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # or venv\Scripts\activate on Windows

   # Install dependencies with UV
   uv pip install -e ".[dev]"
   ```

2. **Code Changes**
   - Create feature branch
   - Make changes
   - Run tests and checks
   - Commit with descriptive message
   - Create pull request

3. **Code Review**
   - Ensure all tests pass
   - Verify code quality checks
   - Review documentation updates
   - Check for security concerns

4. **Deployment**
   - Update version numbers
   - Update changelog
   - Create release tag
   - Deploy to production

## Best Practices

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings
- Keep functions focused
- Use meaningful names

### Documentation
- Update README for major changes
- Document new features
- Keep API documentation current
- Add examples for complex features

### Version Control
- Use semantic versioning
- Write clear commit messages
- Keep commits focused
- Use feature branches
- Review before merging

### Security
- Keep dependencies updated
- Follow security best practices
- Handle sensitive data properly
- Implement proper access controls

## Resources
- [Python Style Guide](https://peps.python.org/pep-0008/)
- [Ruff Documentation](https://beta.ruff.rs/docs/)
- [pytest Documentation](https://docs.pytest.org/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [UV Documentation](https://github.com/astral-sh/uv) 