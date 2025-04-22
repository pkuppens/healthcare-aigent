# Claude Code Best Practices

## Introduction

This document combines the best practices from Anthropic's Claude Code Best Practices guide with
our existing project documentation. It serves as a comprehensive guide for working with Claude
in our development environment.

Original source:
https://www.anthropic.com/claude-code

However, it wasn't Windows compatible at the time of this writing, so this can be ignored for now.

## Language Requirements

All code, documentation, and comments in this project must be written in English. This includes:
- Source code and comments
- Test files and test documentation
- Project documentation
- Commit messages
- Issue descriptions and comments
- Pull request descriptions and comments

## Development Environment

### Python Version
- Use Python 3.11.8 or higher
- Always use a virtual environment
- Use `uv` for package management instead of `pip`

### IDE Configuration
- Use VS Code or Cursor with the following settings:
  ```json
  {
    "python.packageManager": "uv",
    "python.terminal.activateEnvironment": true
  }
  ```

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

## Testing Strategy

### Test-Driven Development (TDD)
1. Write tests first
2. Implement minimum code to pass tests
3. Refactor while keeping tests passing
4. Add more tests for additional functionality

### Test Categories
- Unit Tests: Test individual components in isolation
- Integration Tests: Test component interactions
- LLM Tests: Test LLM connectivity and responses

### Test Structure
- Use Arrange-Act-Assert pattern
- One assertion concept per test
- Meaningful test names
- Comprehensive docstrings

## Working with Claude

### Best Practices
1. **Be Specific and Clear**
   - Provide clear, specific instructions
   - Include relevant context and constraints
   - Specify the desired output format

2. **Use Examples**
   - Provide examples of desired input/output
   - Show error cases and edge cases
   - Include real-world scenarios

3. **Iterative Development**
   - Start with simple implementations
   - Gradually add complexity
   - Test and validate at each step

4. **Error Handling**
   - Specify error handling requirements
   - Include fallback strategies
   - Document error conditions

5. **Documentation**
   - Write clear docstrings
   - Include usage examples
   - Document edge cases and limitations

### Quick Commands for Claude
- **Define tests for [component/feature]**: Start TDD process
- **Implement tests for [component/feature]**: Implement defined tests
- **Implement code for [component/feature]**: Implement functionality
- **Run and fix tests for [component/feature]**: Test and debug
- **Review and refactor [component/feature]**: Improve code quality

## Version Control

### Commit Guidelines
1. **Atomic Commits**: Each commit should represent a single logical change
2. **Descriptive Messages**: Follow the format:
   ```
   <type>(<scope>): <subject>

   <body>

   <footer>

   Out-of-scope:
   - <item1>
   - <item2>
   ```
3. **Commit Types**:
   - feat: New feature
   - fix: Bug fix
   - docs: Documentation changes
   - style: Code style changes
   - refactor: Code refactoring
   - test: Adding or modifying tests
   - chore: Maintenance tasks

## Contradictions and Resolutions

### 1. Package Management
- **Anthropic**: Recommends using `pip`
- **Our Project**: Uses `uv` for faster package management
- **Resolution**: Continue using `uv` as it provides significant performance benefits and is already
integrated into our development environment.

### 2. Python Version
- **Anthropic**: No specific version requirement
- **Our Project**: Requires Python 3.11.8 or higher
- **Resolution**: Maintain our Python 3.11.8 requirement as it provides better performance and features.

### 3. Testing Approach
- **Anthropic**: Focuses on general testing principles
- **Our Project**: Uses TDD with Vibe Coding (TDVC)
- **Resolution**: Continue using TDVC as it provides a structured yet flexible approach that works
well with AI assistance.

### 4. Documentation Style
- **Anthropic**: More general documentation guidelines
- **Our Project**: More specific documentation requirements
- **Resolution**: Maintain our specific documentation requirements while incorporating general
guidelines from Anthropic where they add value.

## Conclusion

This document provides a comprehensive guide for working with Claude in our development environment.
By following these best practices, we can ensure high-quality, maintainable code that meets our
project's requirements while leveraging Claude's capabilities effectively.
