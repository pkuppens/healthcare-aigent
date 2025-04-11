# Continuous Integration and Deployment

This document describes the CI/CD processes for the Healthcare AI Agent project.

## CI Pipeline

The project uses GitHub Actions for continuous integration. The CI pipeline is configured in `.github/workflows/ci.yml`.

### Current CI Checks

1. **Dependency Installation**
   - Runs on Python 3.11
   - Uses UV package manager
   - Verifies core dependencies can be installed
   - Checks for import errors in key packages

### Running CI Locally

To run CI checks locally:

```bash
# Install UV if not already installed
pip install uv

# Install dependencies
uv pip install -e ".[dev]"

# Verify core dependencies
python -c "import crewai; import langchain; import pydantic; print('All core dependencies installed successfully')"
```

## Development Environment

### Python Version

The project is developed and tested primarily with Python 3.11. This version provides:
- Optimal performance improvements over Python 3.10
- Stable feature set
- Wide compatibility with dependencies
- Good tooling support

### Package Management

We use UV for package management because it provides:
- Faster installation times
- Better dependency resolution
- Improved caching
- Consistent environment creation

## Future CI Enhancements

Planned enhancements for the CI pipeline:

1. **Test Coverage**
   - Add pytest execution
   - Generate and upload coverage reports
   - Set minimum coverage thresholds

2. **Code Quality**
   - Add ruff linting checks
   - Add mypy type checking
   - Add pre-commit hook verification

3. **Documentation**
   - Build documentation
   - Verify documentation links
   - Check for broken references

4. **Security**
   - Dependency vulnerability scanning
   - Code security analysis
   - Secret scanning

## Deployment

Deployment processes will be documented here as they are implemented.

### Current Deployment Status

- Development environment: Manual deployment
- Staging environment: Not yet implemented
- Production environment: Not yet implemented

## Best Practices

1. **Before Pushing**
   - Run local tests
   - Verify dependency installation
   - Check code formatting
   - Update documentation if needed

2. **After CI Failure**
   - Check the GitHub Actions logs
   - Reproduce the issue locally
   - Fix the issue and verify locally
   - Push the fix and verify CI passes

3. **Dependency Updates**
   - Use UV for all package management
   - Update dependencies in pyproject.toml
   - Test with the new dependencies
   - Document any breaking changes 