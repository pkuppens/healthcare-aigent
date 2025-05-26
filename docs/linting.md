# Linting Configuration

This project uses [Ruff](https://docs.astral.sh/ruff/) for code linting and formatting with permissive settings that focus on essential code quality while avoiding overly strict rules.

## Configuration

The linting configuration is defined in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 132
target-version = "py311"

[tool.ruff.lint]
# Enable basic error checking, import sorting, and simple fixes
select = [
    "E",    # pycodestyle errors
    "F",    # pyflakes
    "I",    # isort (import sorting)
    "UP",   # pyupgrade (simple modernization)
]
# Ignore specific rules that are too strict
ignore = [
    "E501",   # line too long (handled by formatter)
    "E203",   # whitespace before ':' (conflicts with black)
    "E402",   # module level import not at top of file
    "F401",   # imported but unused (can be useful for __init__.py)
    "F841",   # local variable assigned but never used
]

[tool.ruff.lint.isort]
# Configure import sorting
known-first-party = ["src"]
force-single-line = false
lines-after-imports = 2

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
skip-magic-trailing-comma = false
```

## Key Features

### Permissive Settings
- **Line length**: 132 characters (more generous than the default 88)
- **Ignored rules**: Common issues that don't affect code quality
- **Focus**: Essential errors, import organization, and basic formatting

### Enabled Rules
- **E**: Basic pycodestyle errors (syntax, indentation)
- **F**: Pyflakes (undefined variables, unused imports)
- **I**: Import sorting and organization
- **UP**: Simple Python modernization (f-strings, type hints)

### Import Organization
- Absolute imports are recognized with `src` as first-party
- Automatic import sorting and grouping
- Maintains readable import structure

## Running Linting

### Option 1: Using the Lint Script (Recommended)
```bash
python scripts/lint.py
```

This script runs:
1. `ruff check src/ --fix` - Check and auto-fix issues
2. `ruff format src/` - Format code consistently
3. `ruff check src/` - Final verification

### Option 2: Manual Commands
```bash
# Check and auto-fix issues
uv run ruff check src/ --fix

# Format code
uv run ruff format src/

# Check without fixing
uv run ruff check src/
```

### Option 3: Entry Point (After Installation)
```bash
# Install the package first
uv pip install -e .

# Then use the entry point
lint
```

## Integration with Development

### Pre-commit Hooks
The project includes pre-commit configuration. Install with:
```bash
pre-commit install
```

### IDE Integration
Most IDEs support Ruff integration:
- **VS Code**: Install the Ruff extension
- **PyCharm**: Configure Ruff as external tool
- **Vim/Neovim**: Use ruff-lsp or similar plugins

### CI/CD
Add to your CI pipeline:
```yaml
- name: Lint with Ruff
  run: |
    uv run ruff check src/
    uv run ruff format --check src/
```

## What Gets Fixed Automatically

- Import sorting and organization
- Trailing whitespace removal
- Consistent quote style (double quotes)
- Basic syntax improvements
- Simple modernization (e.g., f-string usage)

## What Doesn't Get Flagged

- Long lines (up to 132 characters)
- Unused variables in some contexts
- Complex type checking issues
- Advanced code complexity metrics
- Overly strict naming conventions

This configuration strikes a balance between code quality and developer productivity, focusing on issues that genuinely improve code maintainability while avoiding nitpicky rules that slow down development. 