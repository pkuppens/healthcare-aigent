# Ollama Installation and Usage Guide

## Introduction

This project uses Ollama to run Large Language Models (LLMs) locally on your machine. Running models locally offers several advantages:
- No internet connection required after initial download
- No API costs or usage limits
- Complete control over model versions and parameters
- Enhanced privacy as data never leaves your machine

Ollama provides a simple way to download, run, and manage various open-source LLMs. It handles all the complexity of model management, allowing you to focus on using the models for your applications.

## Installation Options

### Docker Installation

The recommended way to run Ollama is using Docker. Here's how to get started:

```bash
docker run --gpus=all -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

This command:
- Runs Ollama in detached mode (`-d`)
- Maps port 11434 to your host machine (`-p 11434:11434`)
- Uses a named volume for persistent storage of models (`-v ollama:/root/.ollama`)
- Names the container "ollama" (`--name ollama`)

#### Understanding Docker Components

- **Image**: The `ollama/ollama` image contains the Ollama application and its dependencies
- **Container**: A running instance of the image, named "ollama" in this case
- **Volume**: `ollama:/data` creates a named volume for persistent storage of models
- **Port**: `11434:11434` maps the container's port to your host machine (format: `host:container`)

#### Additional Docker Options

You can customize the Docker installation with these options:

```bash
# Use a different port
docker run -d -p 8080:11434 -v ollama:/data --name ollama ollama/ollama

# Add restart policy
docker run -d --restart unless-stopped -p 11434:11434 -v ollama:/data --name ollama ollama/ollama

# Specify GPU support (requires nvidia-docker)
docker run -d --gpus all -p 11434:11434 -v ollama:/data --name ollama ollama/ollama
```

##### GPU Support with NVIDIA Docker

To use GPU acceleration, you need:
1. NVIDIA GPU drivers installed
2. NVIDIA Container Toolkit (nvidia-docker) installed
3. Docker configured to use NVIDIA runtime

While this is recommended, the exact description of how to install this is out-of-scope for this document.


##### Modifying Container Settings

After creating a container, you can modify its settings:

```bash
# Change restart policy
docker update --restart unless-stopped ollama

# Stop and remove container (preserves volume data)
docker stop ollama
docker rm ollama

# Recreate with new settings
docker run -d --restart unless-stopped -p 11434:11434 -v ollama:/data --name ollama ollama/ollama
```

Note: Some settings like ports and volumes cannot be changed while the container is running. You'll need to recreate the container with new settings.

### Local Installation

#### Windows
1. Download the latest Windows installer from [Ollama's official website](https://ollama.ai/download)
2. Run the installer and follow the prompts
3. Ollama will be installed as a Windows service

#### macOS/Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## Volume Management

### Creating and Managing Volumes

```bash
# Create a named volume
docker volume create ollama

# List volumes
docker volume ls

# Inspect volume details
docker volume inspect ollama
```

### Sharing Models Between Docker and Local Installation

You can share models between Docker and local Windows installation by mounting the Windows Ollama directory, instead of the Docker volume:

```bash
# Windows path format
docker run -d -p 11434:11434 -v %LOCALAPPDATA%\ollama:/data --name ollama ollama/ollama
```

Note: 
- This approach shares the model storage between both installations
- Both installations will use the same models
- Be careful with concurrent access as it might cause issues
- Make sure the Windows path exists before starting the container

## Basic Usage

### Listing Available Models
```bash
ollama list
```
Output example:
```
NAME            SIZE    MODIFIED
llama2:latest   3.8 GB  2 hours ago
mistral:latest  4.1 GB  1 day ago
```

### Installing Models
```bash
ollama pull llama2
```
This will download and install the Llama 2 model. You can see the progress in real-time.

### Running Models
```bash
ollama run llama2
```
This starts an interactive chat session with the model.

## Finding and Selecting Models

### Official Models
Visit [Ollama's model library](https://ollama.ai/library) to browse available models. Popular choices include:
- llama2
- mistral
- codellama
- neural-chat
- vicuna

### Model Modifiers
You can use model modifiers to customize behavior:
```bash
# Run with specific parameters
ollama run llama2 "Explain quantum computing" --temperature 0.7

# Use a specific model variant
ollama run llama2:13b
```

## Data Storage

Models and their data are stored in:
- Docker: Inside the named volume `ollama:/data`
- Windows: `%LOCALAPPDATA%\ollama`
- Linux/macOS: `~/.ollama`

---

Regarding your specific question about having both Ollama.exe and a Docker container:

When you have both Ollama.exe installed locally and a Docker container running, they are indeed separate installations. The Ollama.exe is not just a wrapper for the Docker container - it's a standalone installation that runs natively on Windows.

This configuration could lead to:
1. Duplicate model downloads (each installation maintains its own model storage)
2. Potential port conflicts if both try to use port 11434
3. Confusion about which installation is being used

Recommendation:
- Choose one installation method based on your needs
- If you need GPU support or want to isolate the environment, use Docker
- If you prefer native Windows integration, use the .exe installation
- If you decide to keep both, make sure to use different ports for each installation 