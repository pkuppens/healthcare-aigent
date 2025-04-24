#!/bin/bash

# Exit on error
set -e

# Show current environment
echo "Current environment:"
echo "Project root: $(pwd)"
echo "Python version: $(python3 --version)"
echo "User: $(whoami)"

# Run system setup playbook
echo "Running system setup playbook..."
uv run ansible-playbook ansible/playbooks/setup_system.yml -v

# Run virtual environment setup playbook
echo "Running virtual environment setup playbook..."
uv run ansible-playbook ansible/playbooks/setup_python_envs.yml -v

echo "Setup complete! To activate an environment:"
echo "source .venv-py3.11/bin/activate  # For Python 3.11"
echo "source .venv-py3.12/bin/activate  # For Python 3.12"
echo "source .venv-py3.13/bin/activate  # For Python 3.13" 