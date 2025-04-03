"""LLM factory for creating different types of language models."""

from enum import Enum

from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI


class LLMType(Enum):
    """Types of LLMs available."""

    LOCAL_FAST = "local_fast"  # Fast local model for non-sensitive tasks
    LOCAL_ACCURATE = "local_accurate"  # Accurate local model for sensitive tasks
    CLOUD_FAST = "cloud_fast"  # Fast cloud model for non-sensitive tasks
    CLOUD_ACCURATE = "cloud_accurate"  # Accurate cloud model for non-sensitive tasks


class LLMProvider(Enum):
    """Enum for supported LLM providers."""

    OPENAI = "openai"
    OLLAMA = "ollama"


class LLMFactory:
    """Factory for creating LLM instances."""

    @staticmethod
    def create_llm(llm_type: LLMType, temperature: float = 0.7) -> ChatOpenAI | ChatOllama:
        """Create an LLM instance based on type.

        Args:
            llm_type: Type of LLM to create
            temperature: Temperature setting for the model

        Returns:
            Configured LLM instance
        """
        if llm_type == LLMType.LOCAL_FAST:
            return ChatOllama(model="llama3", base_url="http://localhost:11434", temperature=temperature)

        elif llm_type == LLMType.LOCAL_ACCURATE:
            return ChatOllama(model="llama3:70b", base_url="http://localhost:11434", temperature=temperature)

        elif llm_type == LLMType.CLOUD_FAST:
            return ChatOpenAI(model_name="gpt-3.5-turbo", temperature=temperature)

        elif llm_type == LLMType.CLOUD_ACCURATE:
            return ChatOpenAI(model_name="gpt-4", temperature=temperature)

        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")

    @staticmethod
    def get_llm_for_task(task_type: str, temperature: float = 0.7) -> ChatOpenAI | ChatOllama:
        """Get appropriate LLM for a specific task type.

        Args:
            task_type: Type of task to perform
            temperature: Temperature setting for the model

        Returns:
            Configured LLM instance
        """
        if task_type in ["sensitive_data", "diagnosis"]:
            return LLMFactory.create_llm(LLMType.CLOUD_ACCURATE, temperature)
        elif task_type in ["summarization", "extraction"]:
            return LLMFactory.create_llm(LLMType.CLOUD_FAST, temperature)
        else:
            return LLMFactory.create_llm(LLMType.LOCAL_FAST, temperature)


def create_llm(provider: LLMProvider, model_name: str | None = None):
    """Create an LLM instance based on the provider.

    Args:
        provider: The LLM provider to use
        model_name: Optional model name to use

    Returns:
        Configured LLM instance
    """
    if provider == LLMProvider.OPENAI:
        return ChatOpenAI(model=model_name or "gpt-3.5-turbo", temperature=0.7)
    elif provider == LLMProvider.OLLAMA:
        return ChatOllama(model=model_name or "llama2", temperature=0.7)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
