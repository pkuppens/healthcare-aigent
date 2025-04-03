# Healthcare Multi-Agent System

A proof-of-concept multi-agent LLM system to support healthcare professionals and patients. The system processes text-based medical conversations to extract information, create summaries, and assist with documentation.

## Features

- Multi-agent system using `crewai`
- Support for both OpenAI and Ollama LLMs
- Specialized agents for:
  - Pre-processing & context determination
  - Patient language & medical literacy assessment
  - Clinical information extraction
  - Structured summarization (SOAP notes)
  - Quality control & database updates
- Mocked tools for:
  - Database operations
  - Web search
  - Audit logging

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix/MacOS:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the following variables:
     ```
     OPENAI_API_KEY="your-api-key"
     OPENAI_MODEL_NAME="gpt-3.5-turbo"  # or your preferred model
     LLM_PROVIDER="OPENAI"  # or "OLLAMA" if using local models
     ```

4. (Optional) For Ollama support:
   - Install Ollama from [ollama.ai](https://ollama.ai)
   - Pull your preferred model: `ollama pull llama3`
   - Update `.env` with Ollama settings

## Usage

1. Run the system:
   ```bash
   python src/main.py
   ```

2. The system will process the example transcript and:
   - Identify speakers and context
   - Assess patient language proficiency
   - Extract clinical information
   - Create SOAP notes
   - Generate patient-friendly summaries
   - Propose database updates

## Project Structure

```
/project_root
|-- src/
|   |-- __init__.py
|   |-- agents.py        # Agent definitions
|   |-- tasks.py         # Task definitions
|   |-- tools/
|   |   |-- __init__.py
|   |   |-- database_tools.py
|   |   |-- web_tools.py
|   |   |-- logging_tools.py
|   |-- llm_config.py    # LLM configuration
|   |-- main.py          # Main execution script
|   |-- utils.py         # Utility functions
|-- data/                # Example data
|-- config/              # Configuration files
|-- .env                 # Environment variables
|-- requirements.txt
|-- README.md
```

## Development

- Code formatting and linting:
  ```bash
  ruff check .
  ruff format .
  ```

- Type checking:
  ```bash
  mypy src/
  ```

## License

MIT License
