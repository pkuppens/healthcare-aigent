# Development Environment

This document describes the development environment setup for the Healthcare AI Agent project, including test matrix for different Python versions and development container configuration.

## Package Management with UV

This project uses `uv` for package management, which is significantly faster than traditional `pip`. UV is configured in the following ways:

1. **Project Configuration**: The `pyproject.toml` file includes UV configuration:
   ```toml
   [tool.uv]
   python = "3.11"
   ```

2. **Environment Variables**: The `.env` file includes:
   ```
   UV_PYTHON=3.11
   ```

3. **Global Configuration**: A `.uvrc` file in the project root:
   ```
   [uv]
   python = "3.11"
   ```

## Test Matrix

The project includes a test matrix script that tests compatibility with different Python versions. This ensures that the project works correctly across Python 3.10, 3.11, 3.12, and 3.13.

### Running the Test Matrix

To run the test matrix:

```bash
python test_matrix.py
```

This script will:
1. Create separate virtual environments for each Python version
2. Install the project dependencies using `uv`
3. Run the tests in each environment
4. Provide a summary of the results

### Test Matrix Results

The test matrix will show which Python versions are compatible with the project. This information is valuable for:
- Determining the minimum supported Python version
- Identifying compatibility issues with newer Python versions
- Ensuring the project works correctly across different environments

## Development Container

The project includes a development container configuration for VS Code and Cursor, which provides a consistent development environment across different machines and operating systems.

### Using the Development Container with VS Code

1. Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension in VS Code
2. Open the project in VS Code
3. Click the "Reopen in Container" button when prompted, or use the command palette (F1) and select "Remote-Containers: Reopen in Container"

### Using the Development Container with Cursor

Cursor is built on VS Code and supports the same development container features:

1. Open the project in Cursor
2. Click the "Reopen in Container" button when prompted, or use the command palette (F1) and select "Remote-Containers: Reopen in Container"
3. The container will be built and configured automatically

The development container configuration includes a mount for the Cursor settings directory, ensuring that your Cursor preferences are preserved within the container.

### Development Container Features

The development container includes:
- Python 3.11
- Git
- GitHub CLI
- UV package manager
- VS Code/Cursor extensions for Python development
- Pre-configured linting and formatting settings

### Customizing the Development Container

The development container configuration is in the `.devcontainer` directory:
- `devcontainer.json`: VS Code/Cursor configuration
- `Dockerfile`: Container image definition

To customize the development container:
1. Modify the `Dockerfile` to install additional packages or tools
2. Update the `devcontainer.json` file to add VS Code/Cursor extensions or settings
3. Rebuild the container using the "Remote-Containers: Rebuild Container" command

### Switching Python Versions in the Development Container

To use a different Python version in the development container:

1. **Option 1: Modify the existing container**
   - Edit the `.devcontainer/Dockerfile` file to use a different base image:
     ```dockerfile
     # Change this line
     FROM mcr.microsoft.com/devcontainers/python:3.12
     ```
   - Update the `UV_PYTHON` environment variable:
     ```dockerfile
     ENV UV_PYTHON=3.12
     ```
   - Rebuild the container using the "Remote-Containers: Rebuild Container" command

2. **Option 2: Create a new container configuration**
   - Create a new directory, e.g., `.devcontainer-py312`
   - Copy the existing `.devcontainer` files to the new directory
   - Modify the files as described in Option 1
   - Create a new VS Code/Cursor workspace file that uses the new container configuration

3. **Option 3: Use the Python version selector**
   - The development container includes multiple Python versions
   - Use the Python version selector in VS Code/Cursor to switch between versions
   - Update the `UV_PYTHON` environment variable in your `.env` file

## Best Practices

1. **Always use UV for package management**:
   ```bash
   uv pip install -e ".[dev]"
   ```

2. **Keep dependencies up to date**:
   ```bash
   uv pip install -e ".[dev]" --upgrade
   ```

3. **Run the test matrix before releasing**:
   ```bash
   python test_matrix.py
   ```

4. **Use the development container for consistent development**:
   - Ensures all developers have the same environment
   - Reduces "it works on my machine" issues
   - Simplifies onboarding for new developers 
