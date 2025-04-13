# Development Environment

## Python Version

This project requires Python 3.11 or higher. We specifically recommend Python 3.11.8 for optimal compatibility and performance.

### Why Python 3.11?

- **Performance Improvements**: Python 3.11 offers significant performance improvements over previous versions, with up to 10-60% faster execution times.
- **Better Error Messages**: Enhanced error messages and tracebacks make debugging easier.
- **Type System Enhancements**: Improved type hints and typing system support.
- **Modern Features**: Access to modern Python features and syntax improvements.

### Version Compatibility

- **Python 3.10**: Use at your own risk. Not actively developed.
- **Python 3.11**: Fully supported
- **Python 3.12**: Fully supported
- **Python 3.13**: Not yet fully supported due to compatibility issues with dependencies. We include it in our test matrix to detect when these issues are resolved.

### Version Management

We recommend using a version manager like `pyenv` or `conda` to manage Python versions. This ensures consistency across development environments and makes it easy to switch between different Python versions.

### Checking Your Python Version

You can check your Python version by running:

```bash
python --version
```

### Virtual Environment

Always use a virtual environment for development. You can create one using:

```bash
# Using venv (built into Python 3.3+)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

## Package Management with UV

This project uses `uv` for package management, which is significantly faster than traditional `pip`. UV is configured in the following ways:

1. **Project Configuration**: The `pyproject.toml` file includes UV configuration:
   ```toml
   [tool.uv]
   required-version = ">=0.1.0"
   resolution = "highest"
   compile-bytecode = true
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

4. **VS Code Configuration**: The `.vscode/settings.json` file includes:
   ```json
   "python.packageManager": "uv",
   "python.terminal.activateEnvironment": true
   ```

### Using UV with VS Code

To configure VS Code to use UV instead of pip:

1. Install the UV package manager if you haven't already:
   ```bash
   pip install uv
   ```

2. Configure VS Code to use UV as the package manager:
   - Open VS Code settings (File > Preferences > Settings)
   - Search for "python.packageManager"
   - Set it to "uv"

3. When creating a new virtual environment, VS Code will now use UV instead of pip.

4. For existing projects, you can manually install dependencies with UV:
   ```bash
   uv pip install -e ".[dev]"
   ```

### Troubleshooting UV with VS Code

If you encounter issues with VS Code using UV:

1. **VS Code doesn't recognize UV**: Make sure UV is installed and in your PATH. You can verify this by running `uv --version` in a terminal.

2. **Package installation fails**: Try running the installation command manually in a terminal to see the error message.

3. **VS Code still uses pip**: Check your VS Code settings to ensure `python.packageManager` is set to `uv`. You may need to restart VS Code after changing this setting.

4. **Virtual environment issues**: If VS Code creates a virtual environment with pip instead of UV, you can manually create a virtual environment and then point VS Code to it:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # or source .venv/bin/activate on Unix/MacOS
   uv pip install -e ".[dev]"
   ```
   Then in VS Code, select the Python interpreter from the `.venv` directory.

## Test Matrix

The project includes a test matrix script that tests compatibility with different Python versions. This ensures that the project works correctly across Python 3.10, 3.11, and 3.12.

### Running the Test Matrix

To run the test matrix:

```bash
python tests/test_matrix.py
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
   python tests/test_matrix.py
   ```

4. **Use the development container for consistent development**:
   - Ensures all developers have the same environment
   - Reduces "it works on my machine" issues
   - Simplifies onboarding for new developers 
