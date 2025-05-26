# Healthcare AI Agent System

A proof-of-concept AI system designed to support healthcare professionals in patient communication and clinical documentation. The system provides intelligent assistance to adapt communication styles based on patient characteristics and automate routine documentation tasks.

## Overview

This system demonstrates how AI agents can enhance healthcare delivery by:

- **Improving Patient Communication**: Adapting language and explanations based on patient literacy, cultural background, and communication preferences
- **Streamlining Documentation**: Automating clinical note generation and ensuring completeness
- **Supporting Decision Making**: Providing real-time insights during patient consultations
- **Enhancing Quality**: Continuous feedback on communication effectiveness and documentation accuracy

### Key Benefits

- **Patient-Centric Care**: Personalized communication that improves patient understanding and engagement
- **Efficiency Gains**: Reduced administrative burden through automated documentation
- **Quality Assurance**: Consistent, comprehensive clinical records with built-in quality checks
- **Scalability**: Modular architecture that can adapt to different healthcare settings

### Important Note

This is a proof-of-concept system using simulated data and mocked components. For production use in healthcare environments, additional security, compliance, and integration considerations would be required.

## Quick Start

For detailed installation instructions, see [INSTALL.md](INSTALL.md).

**Quick setup:**
```bash
git clone https://github.com/pkuppens/healthcare-aigent.git
cd healthcare-aigent
uv venv && source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync --dev
cp .env.example .env  # Edit with your API keys
python src/main.py
```

**Next steps:**
- Configure your `.env` file with API keys and preferences
- Run test scenarios: `python notebooks/run_crewai_llm.py`
- Read the [Technical Implementation](docs/technical_implementation.md) guide

## Architecture

The system uses a modular, multi-agent architecture that supports various AI frameworks and LLM providers:

### Framework Options
- **Multi-Agent Systems**: CrewAI, LangFlow, or custom implementations
- **LLM Providers**: OpenAI, Ollama (local), or other compatible providers
- **Deployment**: Local development, containerized, or cloud-based

### Core Components
- **Agent Orchestration**: Coordinates multiple specialized AI agents
- **Communication Adaptation**: Analyzes and adjusts language for different patients
- **Clinical Documentation**: Automated SOAP note generation and medical terminology management
- **Quality Control**: Ensures accuracy and completeness of all outputs

For detailed technical information, see [Technical Implementation](docs/technical_implementation.md).

## Documentation

- **[Technical Implementation](docs/technical_implementation.md)**: Detailed architecture and implementation details
- **[Development Environment](docs/development_environment.md)**: Setup and development guidelines
- **[CrewAI Configuration](docs/crewai.md)**: Multi-agent system configuration
- **[Testing Guidelines](docs/testing.md)**: Testing framework and best practices

## Development

### Prerequisites
- Python 3.11 or higher
- UV package manager (recommended) or pip
- OpenAI API key (optional) or Ollama installation

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Submit a pull request

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src
```

## License

This project is licensed under the MIT License with Commercial Use Restriction. See the [LICENSE](LICENSE) file for details.

**Commercial Use**: Commercial use requires explicit written permission. For licensing inquiries, contact: pieter.kuppens@gmail.com

## Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Review the documentation in the `docs/` folder
- Check existing discussions and solutions
