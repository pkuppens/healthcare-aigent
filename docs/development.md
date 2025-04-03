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
# pytest.ini
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
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows

   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
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