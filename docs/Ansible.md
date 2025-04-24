# 🛠️ Infrastructure Automation with Ansible for Healthcare AI Agent

## 1. 🧩 Introduction to Ansible

Ansible is an open-source automation tool that helps:
- Provision infrastructure
- Configure systems and services
- Deploy applications
- Automate updates and security

It uses YAML-based \"playbooks\" and works agentless — connecting over SSH or WinRM to execute tasks.

Ansible is particularly well-suited for the Healthcare AI Agent system's distributed architecture, managing multiple independent services like diarization, transcription, LLMs, memory databases, and more.

## 2. 🚀 System Prerequisites & Environment Setup

### Installation Overview

| Tool | Installation Level | Purpose |
|------|-------------------|---------|
| Ansible | Global | Core automation platform |
| UV Package Manager | Global | Fast dependency management |
| Python (3.11, 3.12, 3.13) | Global | Runtime environments |
| Docker | Global | Container management |
| Project Dependencies | Virtual Environment | Project-specific packages |

### Platform-Specific Setup

#### ⚠️ Windows Users

Ansible has compatibility issues with Windows, particularly with the `os.get_blocking()` function. Choose one of these options:

##### Option 1: WSL2 (Recommended)
```bash
# In PowerShell as Administrator:
wsl --install
wsl --set-default-version 2

# Install Ubuntu from Microsoft Store, then in Ubuntu terminal:
sudo apt update
sudo apt install python3-pip
pip3 install ansible
```

Access project files with:
```bash
cd /mnt/c/Users/username/path/to/healthcare-aigent
```

##### Option 2: Docker
1. Install Docker Desktop for Windows
2. Use a Linux-based container with Ansible pre-installed
3. Mount your project directory as a volume

##### Option 3: Linux VM
1. Install VirtualBox or VMware
2. Create a Linux VM (Ubuntu recommended)
3. Install Ansible in the VM
4. Share your project directory with the VM

#### Linux/WSL Setup

1. Install required Python versions:
```bash
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.12 python3.13
```

2. Install UV Package Manager (Global):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

3. Install Ansible (Global):
```bash
uv pip install ansible
```

4. Verify installations:
```bash
uv run ansible --version
python3.11 --version
python3.12 --version
python3.13 --version
```

### Sudo Password Handling

The playbooks require sudo access for system-level operations. There are two secure ways to provide the sudo password:

#### Option 1: Interactive Prompt (Recommended)
```bash
# Run with interactive sudo password prompt
uv run ansible-playbook ansible/playbooks/setup_system.yml --ask-become-pass -v
```

#### Option 2: Ansible Vault (Advanced)

1. Create the vault directory and file:
```bash
# Create secure directory
mkdir -p ~/.ansible/vault
cd ~/.ansible/vault

# Create the vault file (you'll be prompted for a vault password)
ansible-vault create sudo_pass.yml
```

2. Add your sudo password to the vault file:
```yaml
# Content of ~/.ansible/vault/sudo_pass.yml
ansible_become_pass: "your-actual-sudo-password"
```

3. Verify the vault setup:
```bash
# Run the verification playbook with interactive prompt
uv run ansible-playbook ansible/playbooks/verify_vault.yml --ask-vault-pass -v
```

or if you placed the vault password in a secure file:
```bash
# Create a secure password file
echo 'your-vault-password' > ~/.ansible/vault/.vault_pass
chmod 600 ~/.ansible/vault/.vault_pass

# Run verification with password file
uv run ansible-playbook ansible/playbooks/verify_vault.yml --vault-password-file ~/.ansible/vault/.vault_pass -v
```

4. Run playbook with vault (choose one method):

   a. Interactive prompt (recommended for first-time setup):
   ```bash
   uv run ansible-playbook ansible/playbooks/setup_system.yml --ask-vault-pass -v
   ```

   b. Environment variable (more secure):
   ```bash
   # Set the vault password
   export ANSIBLE_VAULT_PASSWORD='your-vault-password'
   uv run ansible-playbook ansible/playbooks/setup_system.yml -v
   ```

   c. Password file (for automation):
   ```bash
   # Use the password file
   uv run ansible-playbook ansible/playbooks/setup_system.yml --vault-password-file ~/.ansible/vault/.vault_pass -v
   ```

Example Directory Structure:
```
~/.ansible/
└── vault/
    ├── sudo_pass.yml      # Encrypted vault file with sudo password
    └── .vault_pass        # Optional: Plaintext vault password (chmod 600)
```

⚠️ Security Best Practices:
- NEVER store vault files in the repository
- Keep vault files in a secure, private location (e.g., `~/.ansible/vault/`)
- Use a strong password for the vault file
- Consider using environment variables for sensitive data
- Rotate vault passwords regularly
- Use different vault files for different environments
- Document the vault file location in a secure place
- Back up vault files securely
- If using a password file, ensure it has proper permissions (chmod 600)
- Never commit password files to version control

Troubleshooting:
1. If you get "sudo: a password is required":
   - Verify the vault password is correct
   - Check the sudo password in the vault file
   - Run the verification playbook: `uv run ansible-playbook ansible/playbooks/verify_vault.yml --ask-vault-pass -v`

2. If you get "Vault format unhexlify error":
   - The vault password is incorrect
   - Try recreating the vault file

3. If you get "Permission denied":
   - Check file permissions: `chmod 600 ~/.ansible/vault/*`
   - Verify you own the files: `chown $USER:$USER ~/.ansible/vault/*`

#### Ubuntu/Unix/Cloud VM Setup

```bash
sudo apt update
sudo apt install ansible -y
ansible --version
```

## 3. 🐍 Python Environment Management

### Virtual Environment Setup

The project uses multiple Python versions and environments managed through Ansible:

```bash
# Run the environment setup playbook
uv run ansible-playbook ansible/playbooks/setup_python_envs.yml
```

This creates three virtual environments:
- `.venv-py3.11` - Python 3.11
- `.venv-py3.12` - Python 3.12
- `.venv-py3.13` - Python 3.13

Each environment contains:
- Project dependencies
- LangFlow and related packages
- Other service dependencies

### Using Virtual Environments

Activate a specific environment:
```bash
source .venv-py3.11/bin/activate  # For Python 3.11
source .venv-py3.12/bin/activate  # For Python 3.12
source .venv-py3.13/bin/activate  # For Python 3.13
```

Update all environments:
```bash
uv run ansible-playbook ansible/playbooks/setup_python_envs.yml
```

### Troubleshooting Virtual Environments

If you encounter issues:
1. Verify Python installations:
   ```bash
   python3.11 --version
   python3.12 --version
   python3.13 --version
   ```

2. Check UV installation:
   ```bash
   uv --version
   ```

3. Examine virtual environment directories:
   ```bash
   ls -la .venvs/
   ```

4. Manual LangFlow installation (if needed):
   ```bash
   source .venv-py3.11/bin/activate
   pip install langflow
   ```

## 4. 📦 Service Management with Ansible

### 📁 Project Structure

```
ansible/
├── inventories/
│   └── local_hosts          # Inventory file for local deployment
├── playbooks/
│   ├── setup_ollama.yml     # Local LLM hosting
│   ├── setup_elasticsearch.yml  # Search and storage
│   ├── setup_speech.yml     # Diarization and transcription
│   ├── setup_langflow.yml   # Agent hosting and workflow
│   └── setup_python_envs.yml  # Python environment management
├── roles/
│   └── <modular service roles here>
```

### Inventory Setup

Example inventory file (`inventories/local_hosts`):
```ini
[healthcare_node]
127.0.0.1 ansible_connection=local
```

### Service Deployment

#### 🧠 Local LLM Hosting with Ollama

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
          - \"11434:11434\"
        volumes:
          - \"/opt/ollama:/root/.ollama\"
```

#### 🔍 Elasticsearch Stack

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
          - \"9200:9200\"

    - name: Deploy Kibana
      docker_container:
        name: kibana
        image: docker.elastic.co/kibana/kibana:8.12.0
        ports:
          - \"5601:5601\"
        env:
          ELASTICSEARCH_HOSTS: http://elasticsearch:9200
        links:
          - elasticsearch
```

#### 🔈 Speech Services (Whisper + PyAnnote)

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
          - \"5000:5000\"
        volumes:
          - \"./data/audio:/app/audio\"
```

🧪 Tip: Consider splitting Whisper and diarization into separate microservices using FastAPI containers.

#### 🧠 LangFlow Agent Hosting

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
          - \"7860:7860\"
        volumes:
          - \"./apps/langflow:/app/langflow\"
```

## 5. 🪢 Development Workflow Options

### Option 1: Mount Project Volume

Mount your project code into the LangFlow container:

```yaml
volumes:
  - \"../my_agent_repo:/app/langflow\"
```

This allows editing in VS Code on the host while LangFlow uses the live version.

### Option 2: Git Sync via Ansible

```yaml
- name: Pull latest code
  git:
    repo: https://github.com/pkuppens/healthcare-aigent.git
    dest: /opt/agents/healthcare
    force: yes
```

### Option 3: Dev Containers

The project has a `.devcontainer` directory with VS Code configuration. This can be extended to include Ansible tooling.

## 6. ✅ Best Practices & Next Steps

1. **Modularize Services**: Split services into separate playbooks or roles
2. **Use Tags**: Deploy selectively with tags like `--tags llm` or `--tags transcription`
3. **Version Control**: Include `ansible/` folder in your GitHub repo
4. **CI/CD Integration**: Add a Makefile or CI pipeline to run Ansible automatically
5. **Idempotent Playbooks**: Ensure playbooks can be run multiple times without issues
6. **Documentation**: Keep this Ansible.md up to date with changes

### Running Ansible Commands

Important points for consistent operation:
- When using UV, prefix Ansible commands with `uv run`:
  ```bash
  uv run ansible --version
  uv run ansible-playbook playbooks/setup_ollama.yml
  ```
- Use tags for selective deployment:
  ```bash
  uv run ansible-playbook site.yml --tags \"llm,speech\"
  ```
- Validate playbooks before running:
  ```bash
  uv run ansible-playbook playbook.yml --check
  ```

## 🔗 Related Documentation

- [Project Setup Guide](SETUP.md)
- [README](README.md)
- [GitHub Workflows](../.github/workflows/)
