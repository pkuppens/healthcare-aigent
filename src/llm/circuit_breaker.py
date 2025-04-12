"""Circuit breaker implementation for LLM connectivity checks.

This module provides a circuit breaker pattern for checking LLM connectivity.
It allows for quick failure when a service is known to be unavailable,
preventing unnecessary timeouts and retries.
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

# Constants for circuit breaker configuration
MAX_FAILURES = 5
RESET_TIMEOUT = 5.0  # seconds
CACHE_TIMEOUT = 5.0  # seconds
HTTP_OK = 200  # HTTP status code for successful response


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation, requests are allowed
    OPEN = "open"  # Circuit is open, requests are blocked
    HALF_OPEN = "half_open"  # Testing if service is back online


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 3  # Number of failures before opening circuit
    reset_timeout: float = 60.0  # Seconds to wait before attempting to reset
    half_open_timeout: float = 5.0  # Seconds to wait in half-open state
    success_threshold: int = 1  # Number of successes needed to close circuit


class CircuitBreaker:
    """Circuit breaker implementation for LLM connectivity checks."""

    def __init__(
        self,
        name: str,
        check_function: Callable[[], bool],
        config: CircuitBreakerConfig | None = None,
    ):
        """Initialize the circuit breaker.

        Args:
            name: Name of the circuit breaker (e.g., "ollama", "openai")
            check_function: Function that checks if the service is available
            config: Optional configuration for the circuit breaker
        """
        self.name = name
        self.check_function = check_function
        self.config = config or CircuitBreakerConfig()
        self._failures = 0
        self._last_failure_time: float | None = None
        self._state = "closed"
        self.success_count = 0
        self.last_success_time = 0.0
        self._cache: dict[str, tuple[bool, float]] = {}  # Cache for check results

    def is_available(self) -> bool:
        """Check if the service is available.

        Returns:
            True if the service is available, False otherwise
        """
        # Check cache first (cache expires after 5 seconds)
        current_time = time.time()
        if self.name in self._cache:
            result, timestamp = self._cache[self.name]
            if current_time - timestamp < CACHE_TIMEOUT:  # 5 second cache
                return result

        # If circuit is open, check if reset timeout has passed
        if self._state == "open":
            if self._last_failure_time is not None and current_time - self._last_failure_time < self.config.reset_timeout:
                logger.debug(f"Circuit {self.name} is OPEN, blocking request")
                return False
            else:
                logger.info(f"Circuit {self.name} reset timeout passed, moving to HALF-OPEN")
                self._state = "half_open"
                self._last_failure_time = current_time

        # If circuit is half-open, check if half-open timeout has passed
        if self._state == "half_open":
            if self._last_failure_time is not None and current_time - self._last_failure_time < self.config.half_open_timeout:
                logger.debug(f"Circuit {self.name} is HALF-OPEN, blocking request")
                return False

        # Perform the actual check
        try:
            result = self.check_function()
            self._cache[self.name] = (result, current_time)

            if result:
                self.record_success()
            else:
                self.record_failure()

            return result
        except Exception as e:
            logger.warning(f"Error checking {self.name} availability: {e}")
            self.record_failure()
            return False

    def record_failure(self) -> None:
        """Handle failed check."""
        self._failures += 1
        self._last_failure_time = time.time()
        self.success_count = 0

        if self._state == "closed" and self._failures >= self.config.failure_threshold:
            logger.warning(f"Circuit {self.name} is now OPEN")
            self._state = "open"
        elif self._state == "half_open":
            logger.warning(f"Circuit {self.name} is back to OPEN")
            self._state = "open"

    def record_success(self) -> None:
        """Handle successful check."""
        self.last_success_time = time.time()
        self.success_count += 1
        self._failures = 0

        if self._state == "half_open":
            if self.success_count >= self.config.success_threshold:
                logger.info(f"Circuit {self.name} is now CLOSED")
                self._state = "closed"
                self.success_count = 0

    def reset(self) -> None:
        """Reset the circuit breaker to closed state."""
        self._state = "closed"
        self._failures = 0
        self.success_count = 0
        self._cache.clear()
        logger.info(f"Circuit {self.name} has been manually reset")

    def is_open(self) -> bool:
        """Check if the circuit is open."""
        if self._state == "open":
            if self._last_failure_time is not None:
                current_time = time.time()
                time_diff = current_time - self._last_failure_time
                if time_diff >= RESET_TIMEOUT:
                    self._state = "half_open"
                    return False
            return True
        return False


# Replace with class-based singleton pattern
class CircuitBreakerFactory:
    """Factory for creating and managing circuit breaker instances."""

    _ollama_breaker: CircuitBreaker | None = None
    _openai_breaker: CircuitBreaker | None = None

    @classmethod
    def get_ollama_breaker(cls) -> CircuitBreaker:
        """Get the Ollama circuit breaker instance.

        Returns:
            The Ollama circuit breaker instance
        """
        if cls._ollama_breaker is None:
            from src.llm.ollama_llm import check_ollama_availability

            cls._ollama_breaker = CircuitBreaker("ollama", check_ollama_availability)
        return cls._ollama_breaker

    @classmethod
    def get_openai_breaker(cls) -> CircuitBreaker:
        """Get the OpenAI circuit breaker instance.

        Returns:
            The OpenAI circuit breaker instance
        """
        if cls._openai_breaker is None:
            from src.llm.openai_llm import check_openai_availability

            cls._openai_breaker = CircuitBreaker("openai", check_openai_availability)
        return cls._openai_breaker


def is_ollama_available() -> bool:
    """Check if Ollama is available.

    Returns:
        True if Ollama is available, False otherwise
    """
    return CircuitBreakerFactory.get_ollama_breaker().is_available()


def is_openai_available() -> bool:
    """Check if OpenAI is available.

    Returns:
        True if OpenAI is available, False otherwise
    """
    return CircuitBreakerFactory.get_openai_breaker().is_available()
