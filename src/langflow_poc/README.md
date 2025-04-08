# LangFlow Healthcare Communication Proof-of-Concept

This proof-of-concept demonstrates how LangFlow can be used to create adaptable healthcare communication workflows based on patient preferences.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure Ollama is running locally:
   ```bash
   # Test Ollama connection
   python test_ollama.py
   ```

3. Start LangFlow:
   ```bash
   langflow run
   ```

## Project Structure

- `test_ollama.py`: Tests Ollama integration and connection
- `patient_data.py`: Mock patient database with preferences
- `workflows/`: Directory for storing LangFlow workflow definitions
- `custom_components/`: Directory for custom LangFlow components

## Workflow Storage

Local workflows are stored in:
- Windows: `%APPDATA%/langflow/workflows/`
- Linux/Mac: `~/.langflow/workflows/`

## Custom Components

The project includes custom components for:
- Patient data loading
- Preference-based text adaptation
- Medical terminology simplification
- Multi-language support

## Testing

1. Run Ollama connection test:
   ```bash
   python test_ollama.py
   ```

2. Load the workflow in LangFlow UI (http://localhost:7860)
3. Test with different patient IDs (P001, P002) to see preference-based adaptations

## Notes

- This is a proof-of-concept implementation
- Uses local Ollama models for text generation
- Includes error handling for Ollama service availability
- Demonstrates preference-based output adaptation 