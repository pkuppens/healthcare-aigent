"""Configuration management for LLM settings."""

import json
import logging
import os
from dataclasses import dataclass, field

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class OpenAIConfig:
    """OpenAI configuration settings."""

    api_key: str | None = None
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int | None = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


@dataclass
class OllamaConfig:
    """Ollama configuration settings."""

    base_url: str = "http://localhost:11434"
    model_name: str = "llama3"
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    num_ctx: int = 4096


@dataclass
class LLMConfig:
    """LLM configuration settings."""

    provider: str = "openai"
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    fallback_provider: str = "ollama"
    sensitive_data_handling: bool = True
    cache_responses: bool = True
    cache_dir: str = ".cache/llm"
    timeout_seconds: int = 30


class ConfigManager:
    """Manager for LLM configuration settings."""

    _instance = None
    _config: LLMConfig | None = None

    def __new__(cls):
        """Create a singleton instance of the ConfigManager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the ConfigManager."""
        if self._config is None:
            self._config = self._load_config()

    def _load_config(self) -> LLMConfig:
        """Load configuration from environment variables and config file.

        Returns:
            LLMConfig object with loaded settings
        """
        config = LLMConfig()

        # Load from environment variables
        config.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        config.fallback_provider = os.getenv("LLM_FALLBACK_PROVIDER", "ollama").lower()
        config.sensitive_data_handling = os.getenv("LLM_SENSITIVE_DATA_HANDLING", "true").lower() == "true"
        config.cache_responses = os.getenv("LLM_CACHE_RESPONSES", "true").lower() == "true"
        config.cache_dir = os.getenv("LLM_CACHE_DIR", ".cache/llm")
        config.timeout_seconds = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))

        # OpenAI settings
        config.openai.api_key = os.getenv("OPENAI_API_KEY")
        config.openai.model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
        config.openai.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        config.openai.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "0")) or None
        config.openai.top_p = float(os.getenv("OPENAI_TOP_P", "1.0"))
        config.openai.frequency_penalty = float(os.getenv("OPENAI_FREQUENCY_PENALTY", "0.0"))
        config.openai.presence_penalty = float(os.getenv("OPENAI_PRESENCE_PENALTY", "0.0"))

        # Ollama settings
        config.ollama.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        config.ollama.model_name = os.getenv("OLLAMA_MODEL_NAME", "llama3")
        config.ollama.temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
        config.ollama.top_p = float(os.getenv("OLLAMA_TOP_P", "0.9"))
        config.ollama.top_k = int(os.getenv("OLLAMA_TOP_K", "40"))
        config.ollama.num_ctx = int(os.getenv("OLLAMA_NUM_CTX", "4096"))

        # Load from config file if it exists
        config_file = os.getenv("LLM_CONFIG_FILE", "config/llm_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file) as f:
                    file_config = json.load(f)
                self._update_config_from_dict(config, file_config)
                logger.info(f"Loaded LLM configuration from {config_file}")
            except Exception as e:
                logger.warning(f"Failed to load LLM configuration from {config_file}: {e}")

        return config

    def _update_config_from_dict(self, config: LLMConfig, config_dict: dict) -> None:
        """Update configuration from a dictionary.

        Args:
            config: The LLMConfig object to update
            config_dict: Dictionary with configuration values
        """
        # Update top-level config attributes
        top_level_attrs = [
            "provider",
            "fallback_provider",
            "sensitive_data_handling",
            "cache_responses",
            "cache_dir",
            "timeout_seconds",
        ]
        for attr in top_level_attrs:
            if attr in config_dict:
                setattr(config, attr, config_dict[attr])

        # Update OpenAI config
        if "openai" in config_dict:
            openai_config = config_dict["openai"]
            openai_attrs = ["api_key", "model_name", "temperature", "max_tokens", "top_p", "frequency_penalty", "presence_penalty"]
            for attr in openai_attrs:
                if attr in openai_config:
                    setattr(config.openai, attr, openai_config[attr])

        # Update Ollama config
        if "ollama" in config_dict:
            ollama_config = config_dict["ollama"]
            ollama_attrs = ["base_url", "model_name", "temperature", "top_p", "top_k", "num_ctx"]
            for attr in ollama_attrs:
                if attr in ollama_config:
                    setattr(config.ollama, attr, ollama_config[attr])

    def get_config(self) -> LLMConfig:
        """Get the current configuration.

        Returns:
            The current LLMConfig object
        """
        return self._config

    def update_config(self, config_dict: dict) -> None:
        """Update the configuration with new values.

        Args:
            config_dict: Dictionary with new configuration values
        """
        self._update_config_from_dict(self._config, config_dict)
        logger.info("Updated LLM configuration")

    def save_config(self, config_file: str | None = None) -> None:
        """Save the current configuration to a file.

        Args:
            config_file: Optional path to the config file
        """
        if config_file is None:
            config_file = os.getenv("LLM_CONFIG_FILE", "config/llm_config.json")

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_file), exist_ok=True)

        # Convert config to dictionary
        config_dict = {
            "provider": self._config.provider,
            "fallback_provider": self._config.fallback_provider,
            "sensitive_data_handling": self._config.sensitive_data_handling,
            "cache_responses": self._config.cache_responses,
            "cache_dir": self._config.cache_dir,
            "timeout_seconds": self._config.timeout_seconds,
            "openai": {
                "api_key": self._config.openai.api_key,
                "model_name": self._config.openai.model_name,
                "temperature": self._config.openai.temperature,
                "max_tokens": self._config.openai.max_tokens,
                "top_p": self._config.openai.top_p,
                "frequency_penalty": self._config.openai.frequency_penalty,
                "presence_penalty": self._config.openai.presence_penalty,
            },
            "ollama": {
                "base_url": self._config.ollama.base_url,
                "model_name": self._config.ollama.model_name,
                "temperature": self._config.ollama.temperature,
                "top_p": self._config.ollama.top_p,
                "top_k": self._config.ollama.top_k,
                "num_ctx": self._config.ollama.num_ctx,
            },
        }

        # Save to file
        try:
            with open(config_file, "w") as f:
                json.dump(config_dict, f, indent=2)
            logger.info(f"Saved LLM configuration to {config_file}")
        except Exception as e:
            logger.error(f"Failed to save LLM configuration to {config_file}: {e}")
            raise


# Global instance
config_manager = ConfigManager()
