# LangFlow Healthcare Communication Proof-of-Concept

This project is a learning experience in building a complex multi-agent AI system with LangFlow. 
We use tools, websearch, RAG, and other techniques to create a healthcare communication system.

## Table of Contents

- [What is LangFlow?](#what-is-langflow)
  - [LangFlow vs CrewAI vs LangChain](#langflow-vs-crewai-vs-langchain)
  - [This proof-of-concept](#this-proof-of-concept)
- [Installation](#installation)
- [My First Agent](#my-first-agent)
  - [The Prompt](#the-prompt)
  - [The LLM](#the-llm)
  - [The Response](#the-response)
- [Project Structure](#project-structure)
- [Task List](#task-list)
- [Progress](#progress)
- [Reflection and Feedback](#reflection-and-feedback)

## What is LangFlow?

LangFlow is a visual tool for building AI workflows. It allows you to create complex 
AI systems without writing much code. You can connect different components (such as LLMs, 
tools, and databases) to create a working system.

### LangFlow vs CrewAI vs LangChain

| Tool | Description | Advantages | Disadvantages |
|------|-------------|------------|--------------|
| **LangFlow** | Visual tool for building AI workflows | Visual, easy to understand, quick to prototype | Less flexible than pure code, less suitable for very complex logic |
| **CrewAI** | Framework for building multi-agent systems | Good for complex agent interactions, strongly typed | More code needed, steep learning curve |
| **LangChain** | Framework for building LLM applications | Very flexible, many components | Complex, requires lots of code |

### This proof-of-concept

In this proof-of-concept, we use LangFlow to create a healthcare communication system. 
The system adapts communication based on patient preferences. We learn how to:

- Build multi-agent systems
- Integrate tools
- Use websearch
- Implement RAG (Retrieval Augmented Generation)
- Use feedback and reflection to improve agents

## Installation

This project uses `uv` for package management, virtual environments, and running the application. 
`uv` is a fast Python package installer and resolver that can replace pip, venv, and other tools.

> **Note**: This project requires LangFlow version 1.3.4 or higher. We recommend keeping LangFlow updated to the latest version using `uv pip install -U langflow` to access new features and improvements.

1. Install `uv` if you don't have it already:
   ```bash
   # On Windows
   pip install uv

   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   # Create a virtual environment
   uv venv

   # Activate the virtual environment
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate

   # Install dependencies
   uv sync --dev
   ```

3. Ensure Ollama is running locally:
   ```bash
   # Test Ollama connection
   python src/langflow_poc/test_ollama.py
   ```

4. Start LangFlow:
   ```bash
   # Run LangFlow using uv
   # Set DO_NOT_TRACK=true to opt-out of anonymous data collection
   # This is especially important for healthcare applications
   # Set LANGFLOW_CONFIG_DIR to store workflows in the repository
   set DO_NOT_TRACK=true && set LANGFLOW_CONFIG_DIR=src/langflow_poc/workflows && uv run langflow run
   ```

   Note: The application may take 10 seconds or more to start up. This is normal, especially on first run.

5. Open the LangFlow UI in your browser: http://localhost:7860

## Keeping LangFlow Updated

LangFlow is under active development with frequent updates (weekly or more often). To keep your installation up to date:

```bash
# Update LangFlow to the latest version
uv add langflow --upgrade

# After updating, restart LangFlow
set DO_NOT_TRACK=true && set LANGFLOW_CONFIG_DIR=src/langflow_poc/workflows && uv run langflow run
```

## My First Agent

### The Prompt

A prompt is the instruction you give to an LLM. In LangFlow, you can create prompts with:

- Textual prompts
- Prompt templates
- Prompt variables

Example of a simple prompt:
```
You are a friendly healthcare assistant. 
Answer the following question in a way that matches the patient preferences:
Question: {question}
Patient preferences: {preferences}
```

### The LLM

An LLM (Large Language Model) is the AI model that processes the prompts. In LangFlow, you can use different LLMs:

- OpenAI models (GPT-3.5, GPT-4)
- Ollama models (local)
- Other LLM providers

For this proof-of-concept, we mainly use Ollama models that run locally.

### The Response

The response is the answer from the LLM. In LangFlow, you can:

- Format responses
- Process responses
- Forward responses to other components

## Project Structure

```
src/langflow_poc/
├── README.md                 # This documentation
├── test_ollama.py            # Test Ollama connection
├── patient_data.py           # Mock patient database with preferences
├── workflows/                # LangFlow workflow definitions
│   ├── basic_agent.json      # First agent workflow
│   └── healthcare_agent.json # Healthcare agent workflow
└── custom_components/        # Custom LangFlow components
    ├── patient_loader.py     # Loads patient data
    └── preference_adapter.py # Adapts text based on preferences
```

## Workflow Storage

LangFlow workflows can be managed in several ways:

### Default Storage
By default, LangFlow stores workflows in:
- Windows: `%LOCALAPPDATA%\langflow\langflow\Cache`
- macOS: `/Users/<username>/Library/Caches/langflow`
- Linux/WSL: `~/.cache/langflow`

### Export/Import Workflows
Instead of storing workflows directly in version control, we recommend:
1. Create and test workflows in the LangFlow UI
2. Export workflows when they are stable
3. Store exported workflows in a secure location (not in version control)
4. Import workflows when needed

> **Important**: Exported workflows may contain:
> - API keys and secrets
> - Large JSON structures
> - Sensitive configuration
> 
> Therefore, they should not be stored in version control.

### Recommended Workflow Management
1. **Development**:
   - Use the LangFlow UI for development and testing
   - Keep workflows in the default storage during development

2. **Version Control**:
   - Document workflow designs in the repository
   - Store workflow templates (without secrets)
   - Keep configuration separate from workflows

3. **Deployment**:
   - Export stable workflows
   - Store them in a secure location
   - Use environment variables for configuration/secrets.

### Example Workflow Documentation
```json
{
  "name": "Healthcare Agent",
  "description": "Basic healthcare communication agent",
  "components": [
    {
      "type": "LLM",
      "model": "ollama/mistral"
    },
    {
      "type": "Prompt",
      "template": "You are a healthcare assistant..."
    }
  ]
}
```

## Task List

### Level 1: Basic LangFlow Understanding
- [ ] What is LangFlow?
  - [ ] Read the official documentation
  - [ ] Understand the basic concepts
  - [ ] Compare with other frameworks
- [ ] Installation
  - [ ] Install LangFlow
  - [ ] Configure Ollama
  - [ ] Test the installation
- [ ] First Workflow
  - [ ] Create a simple prompt
  - [ ] Connect to an LLM
  - [ ] Process the response

### Level 2: Advanced Techniques
- [ ] Multi-Agent Systems
  - [ ] Design agent architecture
  - [ ] Implement agent communication
  - [ ] Test agent interactions
- [ ] Tools Integration
  - [ ] Research available tools
  - [ ] Implement custom tools
  - [ ] Test tool functionality
- [ ] Websearch
  - [ ] Configure websearch component
  - [ ] Integrate search results
  - [ ] Evaluate search results
- [ ] RAG Implementation
  - [ ] Design document storage
  - [ ] Implement retrieval
  - [ ] Test RAG workflow
- [ ] Feedback and Reflection
  - [ ] Design feedback mechanism
  - [ ] Implement reflection logic
  - [ ] Test agent improvement

## Progress

### Completed Tasks
- [x] Project initialization
- [x] Basic project structure
- [x] Ollama integration

### Tasks in Progress
- [ ] First agent implementation
- [ ] Patient preferences integration

### Planned Tasks
- [ ] Multi-agent system design
- [ ] Tool integration
- [ ] Websearch implementation
- [ ] RAG system
- [ ] Feedback and reflection mechanism

## Reflection and Feedback

An important part of this project is improving agents based on feedback and reflection. 
We implement a feedback flow where:

1. Agents evaluate their own output
2. Users provide feedback on the output
3. Agents learn from this feedback
4. System messages are improved

This process is documented in the `reflection_flow.md` file.

## Custom Components

This project includes custom components for:
- Patient data loading
- Preference-based text adaptation
- Medical terminology simplification
- Multi-language support

## Testing

1. Run the Ollama connection test:
   ```bash
   python src/langflow_poc/test_ollama.py
   ```

2. Load the workflow in the LangFlow UI (http://localhost:7860)
3. Test with different patient IDs (P001, P002) to see preference-based adaptations

## Notes

- This is a proof-of-concept implementation
- Uses local Ollama models for text generation
- Includes error handling for Ollama service availability
- Demonstrates preference-based output adaptation 