# Use the official Python 3.11 dev container image as the base
# This image includes Python, pip, and other development tools
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install additional OS packages
# These packages are commonly used in development environments
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    curl \
    git \
    # Add any other packages you need for development
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
# UV is a fast Python package installer and resolver
RUN pip install uv

# Set environment variables
# PYTHONUNBUFFERED: Ensures Python output is sent straight to terminal
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files
# UV_PYTHON: Specifies the Python version for UV
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PYTHON=3.11

# Create a non-root user for security
# This prevents running the container as root
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user and add to sudo group
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Set the default user
# This ensures commands run as the non-root user
USER $USERNAME

# Set the working directory
# This is where the project will be mounted
WORKDIR /workspace 