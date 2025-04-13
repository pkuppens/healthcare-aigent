# Test-Driven Development with Vibe Coding (TDVC)

## Introduction

Test-Driven Development (TDD) with Vibe Coding, TDVC for short, is an approach that combines the structured methodology of TDD with the intuitive, flow-based development style of Vibe Coding. This document outlines the process, best practices, and examples based on our experience with the healthcare-aigent project.

## Language Requirements

All code, documentation, and comments in this project must be written in English. This includes:
- Source code and comments
- Test files and test documentation
- Project documentation
- Commit messages
- Issue descriptions and comments
- Pull request descriptions and comments

This requirement ensures consistency and makes the codebase accessible to a global development community.

## Quick Commands for Agentic Chat

When working with AI assistants, you can use these short commands to guide the TDVC process:

- **Define tests for [component/feature]**: Start the TDVC process by defining tests for a specific component or feature
- **Implement tests for [component/feature]**: Implement the tests that were defined in the previous step
- **Implement code for [component/feature]**: Implement the actual code to make the tests pass
- **Run and fix tests for [component/feature]**: Run the tests and fix any issues that arise
- **Review and refactor [component/feature]**: Review the code and tests, and refactor as needed

These commands can be used in sequence to guide the AI assistant through the TDVC process.

## The TDD with Vibe Coding Process

### 1. Analysis and Requirements Review

Before writing any code or tests, take time to understand and challenge the requirements:

- **Question the requirements**: Are they clear, complete, and necessary?
- **Identify edge cases**: What happens when inputs are invalid or at boundaries?
- **Consider alternatives**: Is there a simpler approach that would meet the needs?
- **Define acceptance criteria**: What specific outcomes indicate success?

### 2. Test Definition Phase

The first phase focuses entirely on defining tests without implementing the functionality:

- **Write test docstrings first**: Clearly document what each test verifies
- **Define test structure**: Arrange-Act-Assert pattern with clear sections
- **Include edge cases**: Tests for error conditions and boundary values
- **Group related tests**: Organize tests in logical classes or modules
- **Use meaningful test names**: Names should describe the behavior being tested

### 3. Test Implementation Phase

Once tests are defined, implement the tests to verify they fail appropriately:

- **Mock dependencies**: Use appropriate mocking to isolate the component
- **Patch at the correct location**: Patch where objects are used, not where they're defined
- **Verify mock calls**: Check that mocks are called with expected parameters
- **Order assertions logically**: Check basic properties before detailed behavior
- **Run tests to confirm they fail**: Tests should fail in the expected way

### 4. Implementation Phase

Only after tests are defined and failing appropriately, implement the functionality:

- **Implement the minimum code to make tests pass**: Don't add extra functionality
- **Refactor as needed**: Improve code quality while keeping tests passing
- **Run tests frequently**: Verify changes don't break existing functionality
- **Iterate**: Add more tests for additional functionality as needed

## Best Practices for TDD with Vibe Coding

### Test Documentation

- **Module-level docstrings**: Explain the purpose of the test module
- **Class-level docstrings**: Describe the component being tested
- **Test-level docstrings**: Document what each test verifies, including:
  - What behavior is being tested
  - What conditions are being verified
  - What the expected outcome is
  - Any special considerations or edge cases

### Test Structure

- **Arrange-Act-Assert pattern**: Clearly separate setup, execution, and verification
- **One assertion concept per test**: Each test should verify one specific behavior
- **Meaningful test data**: Use realistic data that represents actual usage
- **Proper isolation**: Tests should not depend on each other

### Mocking Strategy

- **Patch at the correct location**: Patch where objects are used, not where they're defined
- **Mock at the appropriate level**: Don't mock implementation details
- **Verify mock interactions**: Check that mocks are called with expected parameters
- **Use context managers for patching**: `with patch(...)` for cleaner code

### Test Organization

- **Group related tests**: Use test classes to organize related tests
- **Consistent naming**: Use consistent naming conventions for tests
- **Logical ordering**: Order tests from simple to complex
- **Clear test hierarchy**: Organize tests in a logical hierarchy

## Examples from Our Project

### Example 1: LLM Factory Tests

```python
"""Unit tests for the LLM factory.

This module contains tests for the LLMFactory class, which is responsible for creating
instances of different LLM types based on configuration settings. The tests verify that
the factory correctly handles various LLM types, providers, and fallback scenarios.
"""

class TestLLMFactory:
    """Test cases for the LLMFactory class.

    These tests verify that the factory correctly creates LLM instances based on
    configuration settings and handles various edge cases appropriately.
    """

    def test_create_local_fast_llm(self):
        """Test creating a local fast LLM.

        Verifies that:
        1. The factory correctly creates a local fast LLM instance using Ollama
        2. The correct model name (llama3) and temperature (0.7) are used
        3. The provider is set to 'ollama'
        """
        # Arrange
        mock_ollama = MagicMock(spec=OllamaLLM)
        mock_ollama.provider = "ollama"

        # Act
        with patch.dict(LLMFactory._provider_map, {"ollama": lambda **kwargs: mock_ollama}):
            llm = LLMFactory.create_llm(llm_type=LLMType.LOCAL_FAST)

        # Assert
        assert isinstance(llm, BaseLLM)
        assert llm.provider == "ollama"
        assert isinstance(llm, MagicMock)
        assert llm is mock_ollama
```

### Example 2: LLM Adapter Tests

```python
"""Unit tests for LLM adapters.

This module contains tests for the LLM adapter classes that provide a unified interface
for different LLM providers (OpenAI and Ollama). The tests verify that the adapters
correctly initialize, configure, and interact with their respective LLM backends.
"""

class TestOpenAILLM:
    """Test cases for the OpenAI LLM adapter.

    These tests verify that the OpenAILLM adapter correctly initializes and interacts
    with the OpenAI API through the langchain ChatOpenAI class.
    """

    @patch("langchain_openai.ChatOpenAI")
    def test_initialization_with_api_key(self, mock_chat_openai):
        """Test initialization with explicit API key.

        Verifies that:
        1. The adapter correctly initializes with a provided API key
        2. The model name and temperature are set correctly
        3. The provider is correctly identified as 'openai'
        4. The underlying ChatOpenAI is initialized with the correct parameters
        """
        # Arrange
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance

        # Act
        llm = OpenAILLM(model_name="gpt-4", temperature=TEST_TEMPERATURE_LOW, api_key="test-key")

        # Assert
        mock_chat_openai.assert_called_once_with(
            model="gpt-4", 
            temperature=TEST_TEMPERATURE_LOW, 
            openai_api_key="test-key"
        )
        assert llm.model_name == "gpt-4"
        assert llm.temperature == TEST_TEMPERATURE_LOW
        assert llm.provider == "openai"
```

## Common Pitfalls and Solutions

### Pitfall 1: Patching at the Wrong Location

**Problem**: Tests fail because mocks aren't being called.

**Solution**: Patch where objects are used, not where they're defined. For example, when testing the `LLMFactory`, patch the `_provider_map` directly rather than trying to patch the LLM classes.

```python
# Incorrect
@patch("src.llm.ollama_llm.OllamaLLM")
def test_create_local_fast_llm(self, mock_ollama_llm):
    # This won't work because the factory uses the class from _provider_map

# Correct
def test_create_local_fast_llm(self):
    mock_ollama = MagicMock(spec=OllamaLLM)
    mock_ollama.provider = "ollama"
    
    with patch.dict(LLMFactory._provider_map, {"ollama": lambda **kwargs: mock_ollama}):
        llm = LLMFactory.create_llm(llm_type=LLMType.LOCAL_FAST)
```

### Pitfall 2: Overly Specific Assertions

**Problem**: Tests are brittle and fail when implementation details change.

**Solution**: Focus on behavior rather than implementation details. Test what the component does, not how it does it.

```python
# Incorrect
mock_ollama_llm.assert_called_once_with(
    model_name="llama3",
    temperature=0.7,
    base_url="http://localhost:11434"
)

# Correct
assert isinstance(llm, BaseLLM)
assert llm.provider == "ollama"
assert isinstance(llm, MagicMock)
assert llm is mock_ollama
```

### Pitfall 3: Insufficient Test Documentation

**Problem**: Tests are hard to understand and maintain.

**Solution**: Write comprehensive docstrings that explain what each test verifies.

```python
# Incorrect
def test_create_local_fast_llm(self):
    # Test creating a local fast LLM

# Correct
def test_create_local_fast_llm(self):
    """Test creating a local fast LLM.

    Verifies that:
    1. The factory correctly creates a local fast LLM instance using Ollama
    2. The correct model name (llama3) and temperature (0.7) are used
    3. The provider is set to 'ollama'
    """
```

## TDD with Vibe Coding Workflow

### Step 1: Define Requirements and Acceptance Criteria

Before writing any code, define clear requirements and acceptance criteria:

- What is the component supposed to do?
- What are the inputs and expected outputs?
- What are the edge cases and error conditions?
- What are the performance requirements?

### Step 2: Write Test Definitions

Define tests that verify the requirements:

- Write test docstrings that clearly explain what each test verifies
- Define the test structure using the Arrange-Act-Assert pattern
- Include tests for edge cases and error conditions
- Group related tests in logical classes or modules

### Step 3: Implement Tests

Implement the tests to verify they fail appropriately:

- Mock dependencies to isolate the component
- Patch at the correct location
- Verify mock calls
- Order assertions logically
- Run tests to confirm they fail in the expected way

### Step 4: Implement Functionality

Implement the minimum code to make the tests pass:

- Focus on making the tests pass, not on adding extra functionality
- Refactor as needed to improve code quality
- Run tests frequently to verify changes don't break existing functionality
- Iterate by adding more tests for additional functionality

### Step 5: Review and Refactor

Review the code and tests, and refactor as needed:

- Ensure tests are clear and maintainable
- Verify that tests cover all requirements
- Check for any edge cases that might be missing
- Refactor code to improve quality while keeping tests passing

### Step 6: Commit Changes

Commit your changes following these guidelines:

#### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>

Out-of-scope:
- <item1>
- <item2>
```

Where:
- **type**: The type of change (feat, fix, docs, style, refactor, test, chore)
- **scope**: The part of the codebase affected (optional)
- **subject**: A concise description of the change
- **body**: A more detailed explanation of the change (optional)
- **footer**: References to issues or pull requests (optional)
- **Out-of-scope**: Items that were considered but intentionally not included in this commit (optional)

#### Commit Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or modifying tests
- **chore**: Maintenance tasks

#### Commit Guidelines

1. **Atomic Commits**: Each commit should represent a single logical change.
2. **Descriptive Messages**: Commit messages should clearly describe what was changed and why.
3. **Reference Issues**: When applicable, reference issue numbers in commit messages.
4. **Keep Commits Small**: Avoid large commits that mix multiple changes.
5. **Use TODO Comments**: For incomplete implementations in code, use `# TODO:` comments to make them easily discoverable.
6. **Document Out-of-scope Items**: For complex changes, document what was intentionally not included.
7. **Apply Simple Fixes**: Pre-commit will check ruff linting, ruff format and ruff check --fix may be applied.

#### Example Commit Messages

```
feat(llm): add circuit breaker pattern for LLM connectivity

Implement a circuit breaker pattern to prevent unnecessary timeouts and retries
when LLM services are known to be unavailable. This improves system resilience
and performance.

- Add CircuitBreaker class with configurable thresholds
- Implement availability checks for Ollama and OpenAI
- Add caching to reduce redundant checks
- Fix type errors in time difference calculations

Closes #123

Out-of-scope:
- Implementing retry mechanism with exponential backoff
- Adding metrics collection for circuit breaker state changes
```

```
fix(circuit_breaker): fix type errors in time difference calculations

Add proper null checks for _last_failure_time to prevent type errors when
calculating time differences.

Closes #124

Out-of-scope:
- Refactoring the entire time tracking mechanism
```

#### Commit Workflow

1. **Stage Changes**: Use `git add` to stage specific files or changes.
2. **Run Pre-commit Hooks**: Execute `pre-commit run --files <staged_files>` to run linting and other checks.
3. **Fix Simple Issues**: Address any simple linting or formatting issues identified by the pre-commit hooks.
4. **Relax Complex Checks**: For more complex linting violations that don't add business value, consider relaxing the specific checks.
5. **Review Changes**: Use `git diff --staged` to review staged changes.
6. **Write Commit Message**: Follow the format above to write a descriptive commit message.
7. **Commit Changes**: Use `git commit -m` to commit with the message.
8. **Push Changes**: Use `git push` to push changes to the remote repository.

## Conclusion

TDD with Vibe Coding provides a structured yet flexible approach to software development that emphasizes quality, maintainability, and clarity. By focusing on tests first and implementing functionality only after tests are defined, we can ensure that our code meets the requirements and is robust against edge cases and errors.

The key to success is clear documentation, proper test structure, and a focus on behavior rather than implementation details. By following these practices, we can create high-quality, maintainable code that meets the needs of our users. 