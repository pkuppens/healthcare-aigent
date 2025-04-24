#!/bin/bash

# Exit on error
set -e

# Show current environment
echo "Current environment:"
echo "Project root: $(pwd)"
echo "Python version: $(python3 --version)"
echo "User: $(whoami)"
echo "System: $(uname -a)"

# Check if sudo access is available
echo "Checking sudo access..."
if ! sudo -n true 2>/dev/null; then
    echo "Sudo access is required. Please enter your sudo password when prompted."
    echo "Note: You can also use Ansible Vault for automated password handling."
    echo "See docs/Ansible.md for more information."
fi

# Run system setup playbook
echo "Running system setup playbook..."
echo "This will install required Python versions and UV package manager"
echo "You will be prompted for your sudo password if not already authenticated"
uv run ansible-playbook ansible/playbooks/setup_system.yml --ask-become-pass -v

# Run detailed virtual environment setup playbook
echo "Running detailed virtual environment setup playbook..."
echo "This will create virtual environments and install langflow"
echo "You will be prompted for your sudo password if not already authenticated"
uv run ansible-playbook ansible/playbooks/setup_python_envs_detailed.yml --ask-become-pass -v

echo "Setup complete! To activate an environment:"
echo "source .venv-py3.11/bin/activate  # For Python 3.11"
echo "source .venv-py3.12/bin/activate  # For Python 3.12"
echo "source .venv-py3.13/bin/activate  # For Python 3.13" 