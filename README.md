# Healthcare Multi-Agent System

A proof-of-concept multi-agent LLM system to support healthcare professionals in communication with patients and colleagues. The system helps healthcare professionals adapt their communication style based on patient characteristics and provides real-time assistance during consultations.

## Features

### Business Value
- **Patient-Centric Communication**: Get real-time suggestions for adapting language based on:
  - Patient's language proficiency
  - Medical literacy level
  - Cultural background
  - Communication preferences
- **Clinical Documentation Support**: Automated assistance with:
  - SOAP note generation
  - Medical terminology simplification
  - Multilingual documentation
- **Quality Improvement**: Real-time feedback on:
  - Communication effectiveness
  - Documentation completeness
  - Clinical information accuracy

### Technical Components
- Multi-agent system using `crewai`
- Support for both OpenAI and Ollama LLMs
- Specialized agents for:
  - Pre-processing & context determination
  - Patient language & medical literacy assessment
  - Clinical information extraction
  - Structured summarization (SOAP notes)
  - Quality control & database updates

### Extensibility
- Modular architecture for easy addition of:
  - New specialized agents
  - Custom tools and utilities
  - Additional LLM providers
  - Integration with external systems

### Note on Data
This proof-of-concept uses simulated data and mocked components to demonstrate the system's capabilities. In a production environment, this would be replaced with real healthcare data and secure integrations.

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/pkuppens/healthcare-aigent.git
   cd healthcare-aigent
   ```

2. Set up the environment:
   ```bash
   # Create and activate virtual environment
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Unix/MacOS:
   source .venv/bin/activate

   # Install dependencies using uv
   uv sync --dev
   ```

3. Configure the system:
   - Copy `.env.example` to `.env` and update the configuration:
     ```
     # OpenAI Configuration
     OPENAI_API_KEY="your-api-key-here"
     OPENAI_MODEL_NAME="gpt-3.5-turbo"

     # Ollama Configuration (optional)
     OLLAMA_BASE_URL="http://localhost:11434"
     OLLAMA_MODEL_NAME="llama3"

     # LLM Provider Selection
     LLM_PROVIDER="OPENAI"  # or "OLLAMA" 

     # Logging Configuration
     LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
     LOG_FILE="logs/crewai_llm.log"  # Path to log file, or empty for console only
     
     # UV Configuration
     UV_PYTHON=3.11  # Recommended Python version for development
     ```

4. Run the system:
   ```bash
   # Start the backend service
   python src/main.py
   ```

5. Run the test script:
   ```bash
   # Run the CrewAI LLM test script
   python notebooks/run_crewai_llm.py
   ```

## Project Structure

The project is organized as follows:

```
healthcare-aigent/
├── config/                  # Configuration files
├── data/                    # Data files
├── docs/                    # Documentation
├── notebooks/               # Jupyter notebooks and test scripts
├── src/                     # Source code
│   ├── agents.py            # Agent definitions
│   ├── llm_config.py        # LLM configuration
│   ├── main.py              # Main entry point
│   ├── tasks.py             # Task definitions
│   ├── utils.py             # Utility functions
│   └── tools/               # Tool implementations
├── tests/                   # Test files
├── .env                     # Environment variables
├── .env.example             # Example environment variables
├── pyproject.toml           # Project metadata and dependencies
└── README.md                # Project documentation
```

## Logging Configuration

The system uses Python's built-in logging module with configurable settings:

- **Log Level**: Set the `LOG_LEVEL` environment variable to one of:
  - `DEBUG`: Detailed information for debugging
  - `INFO`: General information about program execution
  - `WARNING`: Indicate a potential problem
  - `ERROR`: A more serious problem
  - `CRITICAL`: A critical problem that may prevent the program from running

- **Log File**: Set the `LOG_FILE` environment variable to specify where logs should be written.
  - If not set or empty, logs will only be output to the console.
  - If set, logs will be written to both the console and the specified file.

## LLM Configuration

The system supports multiple LLM providers:

- **OpenAI**: Requires an API key set in the `OPENAI_API_KEY` environment variable.
- **Ollama**: Requires Ollama to be installed and running locally.
- **Mocked LLM**: Used as a fallback when no other LLM is available.

## Development

### Adding New Features

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git commit -m "Add your feature"
   ```

3. Push your branch and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src
```

### Package Management with UV

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

#### Using UV with VS Code

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
   uv sync --dev
   ```

#### Updating Dependencies

```bash
# Update all dependencies
uv sync --dev --upgrade

# Add a new dependency to the project
uv add package-name

# Add a development dependency
uv add --dev package-name

# Remove a dependency
uv remove package-name
```

### Python Version

For information about Python version requirements and recommendations, see [Development Environment](docs/development_environment.md#python-version).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
