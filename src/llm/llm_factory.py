"""LLM factory for creating different types of language models."""

import logging
import os
from enum import Enum
from typing import ClassVar

from src.llm.base import BaseLLM
from src.llm.ollama_llm import OllamaLLM
from src.llm.openai_llm import OpenAILLM

# Configure logging
logger = logging.getLogger(__name__)


class LLMType(Enum):
    """Types of LLMs available."""

    LOCAL_FAST = "local_fast"  # Fast local model for non-sensitive tasks
    LOCAL_ACCURATE = "local_accurate"  # Accurate local model for sensitive tasks
    CLOUD_FAST = "cloud_fast"  # Fast cloud model for non-sensitive tasks
    CLOUD_ACCURATE = "cloud_accurate"  # Accurate cloud model for sensitive tasks


class LLMProvider(Enum):
    """Enum for supported LLM providers."""

    OPENAI = "openai"
    OLLAMA = "ollama"


class LLMFactory:
    """Factory for creating LLM instances."""

    # Map of LLM types to their implementations
    _llm_type_map: ClassVar[dict[LLMType, dict[str, str | float]]] = {
        LLMType.LOCAL_FAST: {"provider": "ollama", "model": "llama3", "temperature": 0.7},
        LLMType.LOCAL_ACCURATE: {"provider": "ollama", "model": "llama3:70b", "temperature": 0.5},
        LLMType.CLOUD_FAST: {"provider": "openai", "model": "gpt-3.5-turbo", "temperature": 0.7},
        LLMType.CLOUD_ACCURATE: {"provider": "openai", "model": "gpt-4", "temperature": 0.5},
    }

    # Map of providers to their implementation classes
    _provider_map: ClassVar[dict[str, type[BaseLLM]]] = {
        "openai": OpenAILLM,
        "ollama": OllamaLLM,
    }

    @classmethod
    def create_llm(cls, llm_type: LLMType, temperature: float | None = None, **kwargs) -> BaseLLM:
        """Create an LLM instance based on type.

        Args:
            llm_type: Type of LLM to create
            temperature: Optional temperature override
            **kwargs: Additional arguments to pass to the LLM constructor

        Returns:
            Configured LLM instance
        """
        if llm_type not in cls._llm_type_map:
            raise ValueError(f"Unsupported LLM type: {llm_type}")

        config = cls._llm_type_map[llm_type]
        provider = config["provider"]
        model = config["model"]
        default_temp = config["temperature"]

        # Use provided temperature or default from config
        temp = temperature if temperature is not None else default_temp

        logger.info(f"Creating {llm_type.value} LLM with provider {provider}, model {model}")

        return cls.create_llm_by_provider(provider, model, temp, **kwargs)

    @classmethod
    def create_llm_by_provider(cls, provider: str, model: str, temperature: float = 0.7, **kwargs) -> BaseLLM:
        """Create an LLM instance based on provider.

        Args:
            provider: The LLM provider to use
            model: The model name to use
            temperature: The temperature setting for the model
            **kwargs: Additional arguments to pass to the LLM constructor

        Returns:
            Configured LLM instance
        """
        provider = provider.lower()

        if provider not in cls._provider_map:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        llm_class = cls._provider_map[provider]

        try:
            return llm_class(model_name=model, temperature=temperature, **kwargs)
        except Exception as e:
            logger.error(f"Error creating {provider} LLM: {e}")
            raise

    @classmethod
    def get_llm_for_task(cls, task_type: str, sensitive_data: bool = False, temperature: float | None = None) -> BaseLLM:
        """Get appropriate LLM for a specific task type.

        Args:
            task_type: Type of task to perform
            sensitive_data: Whether the task involves sensitive data
            temperature: Optional temperature override

        Returns:
            Configured LLM instance
        """
        # Default to cloud fast for most tasks
        llm_type = LLMType.CLOUD_FAST

        # Use more accurate models for specific tasks
        if sensitive_data or task_type in ["diagnosis", "treatment_planning"]:
            llm_type = LLMType.CLOUD_ACCURATE
        elif task_type in ["summarization", "extraction"]:
            llm_type = LLMType.CLOUD_FAST

        # Try to create the preferred LLM, fall back to alternatives if needed
        try:
            return cls.create_llm(llm_type, temperature)
        except Exception as e:
            logger.warning(f"Failed to create preferred LLM {llm_type}: {e}")

            # Fall back to local models if cloud models fail
            if llm_type in [LLMType.CLOUD_FAST, LLMType.CLOUD_ACCURATE]:
                fallback_type = LLMType.LOCAL_FAST if llm_type == LLMType.CLOUD_FAST else LLMType.LOCAL_ACCURATE
                logger.info(f"Falling back to {fallback_type.value}")
                return cls.create_llm(fallback_type, temperature)

            # If all else fails, try to create a basic OpenAI model
            try:
                logger.info("Falling back to basic OpenAI model")
                return cls.create_llm_by_provider("openai", "gpt-3.5-turbo", temperature or 0.7)
            except Exception as e:
                logger.error(f"All LLM creation attempts failed: {e}")
                raise


def get_llm(provider: str | None = None, temperature: float = 0.7) -> BaseLLM:
    """Get LLM instance based on configuration.

    This is a convenience function that maintains backward compatibility
    with the old get_llm function in llm_config.py.

    Args:
        provider: The LLM provider to use (OPENAI or OLLAMA)
        temperature: The temperature parameter for the LLM

    Returns:
        An instance of BaseLLM
    """
    provider = provider or os.getenv("LLM_PROVIDER", "OPENAI")
    provider = provider.lower()

    if provider == "openai":
        model = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
        return LLMFactory.create_llm_by_provider("openai", model, temperature)
    elif provider == "ollama":
        model = os.getenv("OLLAMA_MODEL_NAME", "llama3")
        return LLMFactory.create_llm_by_provider("ollama", model, temperature)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
