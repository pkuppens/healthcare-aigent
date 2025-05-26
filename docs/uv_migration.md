# UV Dependency Management Migration

This document explains the migration from `requirements.txt` to `uv` for dependency management.

## Changes Made

### 1. Dependency Management Strategy
- **Before**: Fixed versions using `==` for stability
- **After**: Minimum versions using `>=` for latest security updates
- **Rationale**: As a library project, we want to allow users to get the latest compatible versions with security updates

### 2. File Structure Changes
- **Removed**: `requirements.txt` - All dependencies now managed in `pyproject.toml`
- **Removed**: `uv.lock` from version control - Added to `.gitignore` (already present)
- **Updated**: `pyproject.toml` with consolidated dependencies

### 3. Dependency Installation Commands

#### Old Commands (pip-based)
```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

#### New Commands (uv-based)
```bash
# Install all dependencies including development
uv sync --dev

# Install only production dependencies
uv sync

# Update all dependencies to latest compatible versions
uv sync --dev --upgrade
```

### 4. Managing Dependencies

#### Adding Dependencies
```bash
# Add a production dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Add with version constraint
uv add "package-name>=1.0.0"
```

#### Removing Dependencies
```bash
uv remove package-name
```

#### Updating Dependencies
```bash
# Update all dependencies
uv sync --upgrade

# Update specific dependency
uv add "package-name>=2.0.0"
```

## Benefits of This Approach

### For Library Projects
1. **Security**: Users get latest security updates automatically
2. **Compatibility**: Broader version ranges reduce dependency conflicts
3. **Flexibility**: Users can choose their preferred versions within constraints

### UV Advantages
1. **Speed**: Significantly faster than pip
2. **Reliability**: Better dependency resolution
3. **Modern**: Built-in support for `pyproject.toml`
4. **Lock Files**: Optional lock files for reproducible builds (excluded for libraries)

## Migration Steps for Developers

If you have an existing environment:

1. **Clean your environment**:
   ```bash
   # Deactivate and remove old virtual environment
   deactivate
   rm -rf .venv  # or rmdir /s .venv on Windows
   ```

2. **Create new environment with uv**:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Unix/MacOS:
   source .venv/bin/activate
   ```

3. **Install dependencies with uv**:
   ```bash
   uv sync --dev
   ```

4. **Verify installation**:
   ```bash
   pytest
   ```

## Configuration

The UV configuration is defined in `pyproject.toml`:

```toml
[tool.uv]
required-version = ">=0.1.0"
resolution = "highest"  # Always use latest compatible versions
compile-bytecode = true
dev-dependencies = [
    # Development dependencies listed here
]
```

## Notes

- `uv.lock` is excluded from version control for library projects
- Dependencies use minimum version constraints (`>=`) for security updates
- Development dependencies are clearly separated in `pyproject.toml`
- The project maintains compatibility with Python 3.11+ as specified in `requires-python` 