# Development Setup

This document describes how to set up the development environment for this project.

## Requirements

- Python 3.10 or higher
- Git
- pip (Python package manager)

## Step 1: Clone the repository

```bash
git clone https://github.com/pkuppens/healthcare-aigent.git
cd healthcare-aigent
```

## Step 2: Create a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/MacOS
python -m venv .venv
source .venv/bin/activate
```

## Step 3: Install dependencies

Install the project in editable mode with development dependencies:

```bash
pip install -e ".[dev]"
```

This will install:
- All core project dependencies
- Development tools (pytest, ruff, mypy, pre-commit)
- The project itself in editable mode

## Step 4: Install pre-commit hooks

```bash
pre-commit install
```

To verify that the pre-commit hooks are working correctly, run:

```bash
pre-commit run --all-files
```

This will run the following checks on all files:
- ruff: Python linter and formatter
- ruff-format: Code formatting

## Step 5: Copy the .env file

```bash
cp .env.example .env
```

Fill in the appropriate values for the environment variables in the `.env` file.

## Step 6: Test the setup

Run the tests to verify that everything is installed correctly:

```bash
pytest
```

## Troubleshooting

If you encounter any issues during setup:

1. Verify that your Python version meets the requirements (3.10 or higher)
2. Ensure your virtual environment is activated
3. Try reinstalling dependencies with `pip install -e ".[dev]" --upgrade`
4. If pre-commit hooks aren't working, try `pre-commit clean` and reinstall

## Development workflow

1. Create a new branch for your feature/fix
2. Install pre-commit hooks (step 4)
3. Commit your changes (pre-commit hooks will run automatically)
4. Run tests before pushing
5. Create a pull request

## Git commit options

### Standard commit (recommended)
```bash
git add .
git commit -m "Your commit message"
```
This will run all pre-commit hooks before allowing the commit.

### Skip pre-commit hooks (not recommended)
```bash
git add .
git commit --no-verify -m "Your commit message"
```
This will skip all pre-commit hooks. Only use this in exceptional cases where you need to commit code that doesn't meet the project's standards. Remember to fix any issues before pushing to the repository, especially on the main branch.