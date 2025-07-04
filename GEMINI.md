# GEMINI.md - Operational Directives and Coding Conventions

This document outlines the rules, conventions, and operational guidelines for me, the Gemini AI assistant, while working on this project.
Its purpose is to ensure my contributions are safe, predictable, and aligned with the project's standards.

## 1. Core Principles

- **Primary Goal**: My main objective is to act as a collaborative partner, helping to develop high-quality, well-documented, and production-ready code.
- **Safety and Confirmation**: My highest priority is the safety and integrity of your project.
I use git branch and commit strategies during operation to maintain the integrity of the main branch.
When I am on main branch, I switch to a feature branch. I do not switch further.
Before humans review, I stage files, and after acceptance, I commit files before continuing.

## 2. File System and Shell Operations

- **Permissions**: I have permissive rights on branches to create, read, edit, and delete files and directories within the project's scope. I can also execute shell commands.
- **Safeguard**: On branches I can modify the file system (e.g., `rm`, `del`, `mv`, `git reset`), I will log this with a clear explanation of what the command does and what its impact will be. I will use the correct git commands.

## 3. Code Quality and Documentation Standards

I will write code that is not just functional but also robust, maintainable, and easy for other developers to understand.

### 3.1. Production-Ready Code

- **Robustness**: I will write code that anticipates and handles potential errors gracefully. This includes adding `try...except`with small granularity and explicit error catching, for I/O, network requests, and other operations that might fail.
- **Configuration**: I will avoid hardcoding sensitive information or configuration values. I will use the project's existing configuration system (e.g., `.env` files, `config` modules).
- **Logging**: I will use the project's established logging framework to provide clear and informative messages about the system's execution. I will add INFO logging to functions that face the user or cross component boundaries. I will add DEBUG logging for internal function calls.

### 3.2. Documentation Philosophy

- **Clarity over Brevity**: Documentation is a first-class citizen. I will write clear, comprehensive documentation for all new code.
- **File-Level Docstrings**: Every new Python file (`.py`) will begin with a module-level docstring that explains the file's purpose, its responsibilities, and a brief overview of its contents.
- **Class-Level Docstrings**: Every new class will have a docstring explaining its purpose, what it models or manages, and its key attributes or methods.
- **Function-Level Docstrings**: Every new public function or method will have a detailed docstring that at least covers argument and result types, and possible raised errors.

### 3.3. Docstring Style

For interfacing functions (User, API, cross-boundary), use Google Style function docstrings:

#### **Google Style (Recommended)**

**Example:**
```python
def my_function(param1: int, param2: str) -> bool:
    """Does something interesting and returns a result.

    This function demonstrates the Google docstring format. It describes what
    the function does, its arguments, and what it returns.

    Args:
        param1: The first parameter, which is an integer.
        param2: The second parameter, which is a string.

    Returns:
        True if the operation was successful, False otherwise.
    (Yields: in case of a generator function)
        
        
    Raises:
        ValueError: If param1 is a negative number.
    """
    if param1 < 0:
        raise ValueError("param1 cannot be negative")
    return True
```

**Note on API Docstrings**: For customer-facing API endpoints (e.g., in FastAPI), the docstring will also include one or more `Examples` in a format compatible with FastAPI's automatic documentation generation. This makes the API self-documenting and easier to use.

**Example for FastAPI:**
```python
@app.post("/items/")
async def create_item(item: Item):
    """
    Creates a new item.

    - **name**: The name of the item.
    - **price**: The price of the item.

    Example:
        {
            "name": "My Item",
            "price": 10.50
        }
    """
    return item
```

#### **Trivial functions**

For (near) trivial functions that are only used internally, I will be more verbose:

**Example:**
```python
def validate_minimum_age(age: int, minimum_age: int = 18) -> bool:
    """Validate an age against a minimum_age that defaults to 18"""
    return age >= minimum_age
```


## 4. Coding Style and Formatting

Consistency in coding style is key to a maintainable codebase.

- **Linter & Formatter**: I will use `Ruff` for all Python code formatting and linting, adhering to the rules defined in the project's `pyproject.toml`. I will run `ruff format` and `ruff check --fix` on any code I modify.
- **Line Length**: I will adhere to a maximum line length of **132 characters**, as requested.
- **Type Hinting**: All new functions, methods, and variables will include type hints using the standard `typing` module. This improves code clarity, enables static analysis, and helps prevent bugs. If `ruff` complaints that Dict should be replaced with dict, I will follow that rule.

### 4.1. Import Style

- **Preference for Absolute Imports**: I will prefer absolute imports over relative imports. For example, I will use `from src.tasks.summarize_task import GenerateSummaryTask` instead of `from .summarize_task import GenerateSummaryTask`. This makes the code more explicit and easier to understand, especially in larger projects.

## 5. Version Control

- **Commits**: I will write clear and descriptive commit messages, preferring concise, well-structured summaries. If the project follows a convention (e.g., Conventional Commits), I will adhere to it. I will analyze the existing `git log` to match the established style. I will use a git commit command that allows multi-line message that also works on Windows command terminal, e.g. multiple -m commands for linefeeds.
- **Process**: After making changes and running `ruff` checks, I will stage the modified files using `git add`. I will then present the staged changes (`git diff --staged`) and a proposed `git commit` command. The commit message will be formatted as a single string with `\n` for line breaks to ensure command-line compatibility. This provides a clear checkpoint for your review and execution.

---

This document is a living set of rules. You can ask me to update or change these guidelines at any time.
