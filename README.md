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
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix/MacOS:
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. Configure the system:
   - Copy `config/crew.yaml.example` to `config/crew.yaml`
   - Update the configuration for each agent:
     ```yaml
     agents:
       preprocessor:
         llm_provider: "OPENAI"  # or "OLLAMA"
         model_name: "gpt-3.5-turbo"
         api_key: "your-api-key"
         temperature: 0.7
       
       language_assessor:
         llm_provider: "OPENAI"
         model_name: "gpt-3.5-turbo"
         api_key: "your-api-key"
         temperature: 0.5
       
       clinical_extractor:
         llm_provider: "OLLAMA"
         model_name: "llama2"
         temperature: 0.3
     
     tools:
       database:
         type: "mock"  # or "production" for real database
         connection_string: "your-connection-string"
     
     system:
       log_level: "INFO"
       max_retries: 3
       timeout: 30
     ```

4. Run the system:
   ```bash
   # Start the backend service
   python src/main.py

   # In a new terminal, start the frontend development server
   cd frontend
   npm install
   npm run dev
   ```

   The system will provide:
   - Patient selection interface
   - Patient file summary view
   - Consultation request form
   - Real-time communication assistance
   - Speech-to-text input for consultations
   - Automated documentation generation

## Documentation

- [System Architecture](docs/architecture.md): Detailed system design, component diagrams, and data flow
- [CrewAI Implementation](docs/crewai.md): CrewAI framework integration, agent configuration, and best practices
- [Testing Strategy](docs/testing.md): Comprehensive testing approach, examples, and guidelines
- [Development Guidelines](docs/development.md): Code quality standards, testing procedures, and development workflow

## Project Structure

```
/project_root
|-- src/                # Backend source code
|   |-- agents/         # Agent implementations
|   |-- tools/          # Tool implementations
|   |-- main.py         # Backend entry point
|-- frontend/           # Frontend application
|   |-- src/            # React/Vue source code
|   |-- public/         # Static assets
|   |-- package.json    # Frontend dependencies
|-- config/             # Configuration files
|   |-- crew.yaml       # Agent and system configuration
|   |-- crew.yaml.example
|-- tests/              # Test suite
|-- docs/               # Documentation
|-- data/               # Example data
|-- requirements.txt    # Python dependencies
|-- README.md           # This file
```

## License

MIT License, see [LICENSE](LICENSE)
