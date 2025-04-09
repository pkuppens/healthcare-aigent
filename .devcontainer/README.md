# Development Container Configuration

This directory contains configuration files for the development container used in this project. The development container provides a consistent development environment across different machines and operating systems.

## Files

- `devcontainer.json`: Configuration file for VS Code and Cursor development containers
- `Dockerfile`: Definition of the container image used for development

## Usage

### VS Code

1. Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension
2. Open the project in VS Code
3. Click the "Reopen in Container" button when prompted

### Cursor

1. Open the project in Cursor
2. Click the "Reopen in Container" button when prompted

## Features

The development container includes:

- Python 3.11
- Git
- GitHub CLI
- UV package manager
- Pre-configured VS Code/Cursor extensions and settings

## Customization

### Changing Python Version

To use a different Python version:

1. Edit the `Dockerfile` to use a different base image:
   ```dockerfile
   FROM mcr.microsoft.com/devcontainers/python:3.12
   ```

2. Update the `UV_PYTHON` environment variable:
   ```dockerfile
   ENV UV_PYTHON=3.12
   ```

3. Rebuild the container using the "Remote-Containers: Rebuild Container" command

### Adding Additional Packages

To add additional packages to the container:

1. Edit the `Dockerfile` and add the package to the `apt-get install` command:
   ```dockerfile
   RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
       && apt-get -y install --no-install-recommends \
       curl \
       git \
       your-package-here \
       && apt-get clean -y \
       && rm -rf /var/lib/apt/lists/*
   ```

2. Rebuild the container

### Adding VS Code/Cursor Extensions

To add additional VS Code/Cursor extensions:

1. Edit the `devcontainer.json` file and add the extension ID to the `extensions` array:
   ```json
   "extensions": [
     "ms-python.python",
     "your-extension-id"
   ]
   ```

2. Rebuild the container

## Troubleshooting

If you encounter issues with the development container:

1. Check the VS Code/Cursor output panel for error messages
2. Try rebuilding the container using the "Remote-Containers: Rebuild Container" command
3. Check the [VS Code Remote Development documentation](https://code.visualstudio.com/docs/remote/remote-containers) for more information 