#!/bin/bash

# Exit on error
set -e

# Clean up existing environments
echo "Cleaning up existing environments..."
rm -rf .venv .venvs

# Install required Python versions if not present
echo "Checking Python versions..."
for version in 3.11 3.12 3.13; do
    if ! command -v python$version &> /dev/null; then
        echo "Installing Python $version..."
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt update
        sudo apt install -y python$version python$version-venv python$version-dev
    fi
done

# Install UV if not present
if ! command -v uv &> /dev/null; then
    echo "Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Install Ansible if not present
if ! command -v ansible &> /dev/null; then
    echo "Installing Ansible..."
    uv pip install ansible
fi

# Run the playbook
echo "Running Ansible playbook..."
uv run ansible-playbook ansible/playbooks/setup_python_envs.yml -v

echo "Setup complete! To activate an environment:"
echo "source .venv-py3.11/bin/activate  # For Python 3.11"
echo "source .venv-py3.12/bin/activate  # For Python 3.12"
echo "source .venv-py3.13/bin/activate  # For Python 3.13" 