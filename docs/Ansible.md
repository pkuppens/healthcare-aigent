# 🛠️ Infrastructure Automation with Ansible

## 1. 🧩 What Is Ansible?

Ansible is an open-source automation tool used to:
- Provision infrastructure
- Configure systems and services
- Deploy applications
- Automate updates and security

It uses YAML-based "playbooks" and works agentless — connecting over SSH or WinRM to execute tasks.

Ansible is a good fit for the Healthcare AI Agent system, which involves many independently running services (diarization, transcription, local/remote LLMs, memory DB, etc.).

## 2. 🚀 Installation & Startup

### ⚠️ Windows Users: Important Note
Ansible has known compatibility issues with Windows, particularly with the `os.get_blocking()` function which is not available on Windows. This results in errors like:
```python
AttributeError: module 'os' has no attribute 'get_blocking'
```

To work around this limitation, Windows users have three options:

#### Option 1: Use WSL2 (Recommended)
1. Install WSL2:
   ```bash
   # Open PowerShell as Administrator and run:
   wsl --install
   wsl --set-default-version 2
   ```
2. Install Ubuntu from Microsoft Store
3. Open Ubuntu terminal and run:
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip3 install ansible
   ```
4. Access your project files in WSL:
   ```bash
   # Navigate to your project (adjust path as needed)
   cd /mnt/c/Users/piete/Repos/pkuppens/healthcare-aigent
   ```

#### Option 2: Use Docker
1. Install Docker Desktop for Windows
2. Use a Linux-based container with Ansible pre-installed
3. Mount your project directory as a volume

#### Option 3: Use a Linux VM
1. Install VirtualBox or VMware
2. Create a Linux VM (Ubuntu recommended)
3. Install Ansible in the VM
4. Share your project directory with the VM

### Installation with UV (Linux/WSL)

```bash
# Install Ansible using UV
uv pip install ansible

# Verify installation
uv run ansible --version
```

⚠️ **Important Notes:**
1. When using UV, run Ansible commands with the `uv run` prefix:
   ```bash
   uv run ansible --version
   uv run ansible-playbook playbook.yml
   ```

### Verify Installation

On Linux/WSL:
```bash
uv run ansible --version
```

### Ubuntu / Unix / Cloud VM

```bash
sudo apt update
sudo apt install ansible -y
```

Check installation:

```bash
ansible --version
```

## 3. 📦 Modular Services with Ansible Playbooks

Below is an example of how to manage various services using Ansible.

### 📁 Directory Structure

```
ansible/
├── inventories/
│   └── local_hosts
├── playbooks/
│   ├── setup_ollama.yml
│   ├── setup_elasticsearch.yml
│   ├── setup_speech.yml
│   └── setup_langflow.yml
├── roles/
│   └── <modular service roles here>
```

### Example Inventory (inventories/local_hosts)

```ini
[healthcare_node]
127.0.0.1 ansible_connection=local
```

### 🧠 Deploy Ollama (Local LLM Hosting)

```yaml
# playbooks/setup_ollama.yml
- hosts: healthcare_node
  tasks:
    - name: Pull Ollama image
      docker_image:
        name: ollama/ollama
        source: pull

    - name: Run Ollama container
      docker_container:
        name: ollama
        image: ollama/ollama
        ports:
          - "11434:11434"
        volumes:
          - "/opt/ollama:/root/.ollama"
```

### 🔈 Speaker Diarization & Transcription (e.g. Whisper + PyAnnote)

```yaml
# playbooks/setup_speech.yml
- hosts: healthcare_node
  tasks:
    - name: Deploy Whisper + PyAnnote container
      docker_container:
        name: speech_services
        image: custom/speech-stack:latest
        build:
          path: ../services/speech/
        ports:
          - "5000:5000"
        volumes:
          - "./data/audio:/app/audio"
```

🧪 Tip: Split Whisper and diarization into microservices using FastAPI containers.

### 🧠 LangFlow + Agent Hosting

```yaml
# playbooks/setup_langflow.yml
- hosts: healthcare_node
  tasks:
    - name: Pull LangFlow
      docker_image:
        name: langflow/langflow
        source: pull

    - name: Start LangFlow with mounted volume
      docker_container:
        name: langflow
        image: langflow/langflow
        ports:
          - "7860:7860"
        volumes:
          - "./apps/langflow:/app/langflow"
```

## 4. 🔍 Elasticsearch Stack (Open Source)

Use the ELK stack (Elasticsearch + Logstash + Kibana) or lightweight alternative:

### 🧰 Suggested Stack
- Elasticsearch: Search engine backend
- Kibana: Web UI for search and dashboards
- Fluent Bit (lighter than Logstash): Log shipping

### Elasticsearch Ansible Snippet

```yaml
# playbooks/setup_elasticsearch.yml
- hosts: healthcare_node
  tasks:
    - name: Deploy Elasticsearch
      docker_container:
        name: elasticsearch
        image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
        env:
          discovery.type: single-node
          xpack.security.enabled: false
        ports:
          - "9200:9200"

    - name: Deploy Kibana
      docker_container:
        name: kibana
        image: docker.elastic.co/kibana/kibana:8.12.0
        ports:
          - "5601:5601"
        env:
          ELASTICSEARCH_HOSTS: http://elasticsearch:9200
        links:
          - elasticsearch
```

## 5. 🪢 Git Sync & Dev Inside LangFlow Container

### Option 1: Mount Project Volume
Mount your project code into the LangFlow container:

```yaml
volumes:
  - "../my_agent_repo:/app/langflow"
```

You can edit in VS Code on the host, and LangFlow will use the live version.

### Option 2: Git Pull via Ansible Task

```yaml
- name: Pull latest code
  git:
    repo: https://github.com/pkuppens/healthcare-aigent.git
    dest: /opt/agents/healthcare
    force: yes
```

### Option 3: Use Dev Containers
The project already has a `.devcontainer` directory with configuration for VS Code. You can extend this to include Ansible tooling.

## ✅ Next Steps

1. Modularize your services into separate playbooks or roles
2. Use tags like `--tags llm` or `--tags transcription` to deploy selectively
3. Version-control your `ansible/` folder with your main GitHub repo
4. For full automation, consider a Makefile or CI pipeline to run Ansible on every update
5. Integrate with the existing `.github` workflows for CI/CD

## 🔗 Related Documentation

- [Project Setup Guide](SETUP.md)
- [README](README.md)
- [GitHub Workflows](../.github/workflows/) 