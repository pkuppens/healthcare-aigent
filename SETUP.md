# Development Setup

This document describes how to set up the development environment for this project.

## Requirements

- Python 3.10 or higher
- Git
- pip (Python package manager)

## Step 1: Clone the repository

```bash
git clone <repository-url>
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

```bash
pip install -r requirements.txt
```

## Step 4: Install pre-commit hooks

```bash
pre-commit install
```

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
3. Try reinstalling dependencies with `pip install -r requirements.txt --upgrade`
4. If pre-commit hooks aren't working, try `pre-commit clean` and reinstall

## Development workflow

1. Create a new branch for your feature/fix
2. Install pre-commit hooks (step 4)
3. Commit your changes (pre-commit hooks will run automatically)
4. Run tests before pushing
5. Create a pull request 