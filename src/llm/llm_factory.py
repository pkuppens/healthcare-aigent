"""LLM factory for healthcare applications."""

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
    """Factory for creating LLMs based on healthcare use cases."""

    @staticmethod
    def create_llm(llm_type: LLMType, temperature: float = 0.7) -> ChatOpenAI | ChatOllama:
        """Create an LLM based on the specified type.

        Args:
            llm_type: Type of LLM to create
            temperature: Temperature parameter for the LLM

        Returns:
            Configured LLM instance
        """
        if llm_type in [LLMType.LOCAL_FAST, LLMType.LOCAL_ACCURATE]:
            model = "llama3" if llm_type == LLMType.LOCAL_FAST else "llama3:70b"
            return ChatOllama(model=model, base_url="http://localhost:11434", temperature=temperature)

        if llm_type in [LLMType.CLOUD_FAST, LLMType.CLOUD_ACCURATE]:
            model = "gpt-3.5-turbo" if llm_type == LLMType.CLOUD_FAST else "gpt-4"
            return ChatOpenAI(model_name=model, temperature=temperature)

        raise ValueError(f"Unsupported LLM type: {llm_type}")

    @staticmethod
    def get_llm_for_task(task_type: str, sensitive_data: bool = False) -> ChatOpenAI | ChatOllama:
        """Get appropriate LLM for a healthcare task.

        Args:
            task_type: Type of task (e.g., 'summarization', 'extraction')
            sensitive_data: Whether the task involves sensitive patient data

        Returns:
            Configured LLM instance
        """
        if sensitive_data:
            return LLMFactory.create_llm(LLMType.LOCAL_ACCURATE)

        if task_type in ["summarization", "extraction"]:
            return LLMFactory.create_llm(LLMType.CLOUD_ACCURATE)

        return LLMFactory.create_llm(LLMType.CLOUD_FAST)


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
