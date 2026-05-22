#!/usr/bin/env python3
"""Base provider abstraction layer for LLM interactions.

Defines the interface that all provider adapters must implement,
plus shared data structures and retry logic.
"""

import time
import functools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class ProviderNotAvailableError(ProviderError):
    """Raised when a provider is not installed or reachable."""
    pass


class ProviderAuthError(ProviderError):
    """Raised when authentication fails (missing API key, expired token)."""
    pass


class ProviderTimeoutError(ProviderError):
    """Raised when a provider call times out."""
    pass


class ProviderRateLimitError(ProviderError):
    """Raised when rate-limited — signals retry logic to back off."""
    pass


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class CompletionResult:
    """Result from an LLM completion call."""
    text: str
    model: str
    tokens_used: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    duration_ms: float = 0.0
    cost_estimate: float = 0.0
    raw_response: dict | None = None


@dataclass
class TriggerResult:
    """Result from a skill-trigger check."""
    triggered: bool
    tool_name: str | None = None
    tool_input: dict | None = None
    confidence: float = 0.0
    reasoning: str = ""


@dataclass
class ProviderCapabilities:
    """What a provider supports."""
    streaming: bool = False
    function_calling: bool = False
    skill_trigger_detection: bool = False
    tool_use: bool = False
    vision: bool = False
    max_context_tokens: int = 128000


# ---------------------------------------------------------------------------
# Retry Decorator
# ---------------------------------------------------------------------------

def retry_with_backoff(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    jitter: float = 0.5,
    retryable_exceptions: tuple = (ProviderTimeoutError, ProviderRateLimitError),
):
    """Decorator that retries a function with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (including the first).
        backoff_factor: Multiplier for wait time between retries.
        jitter: Random jitter factor (0.0 to 1.0) to prevent thundering herd.
        retryable_exceptions: Exception types that trigger a retry.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        raise
                    wait = backoff_factor ** (attempt - 1)
                    # Add jitter
                    import random
                    wait += random.uniform(0, jitter * wait)
                    time.sleep(wait)
            raise last_exception  # Should never reach here
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Abstract Base Provider
# ---------------------------------------------------------------------------

class LLMProvider(ABC):
    """Abstract base class for LLM provider adapters.

    Every adapter must implement complete() and get_default_model().
    check_skill_trigger() has a default implementation using complete(),
    but providers with native tool-use can override it.
    """

    @abstractmethod
    def complete(
        self,
        prompt: str,
        model: str | None = None,
        timeout: int = 300,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> CompletionResult:
        """Send a prompt and get a text completion.

        Args:
            prompt: The user prompt to send.
            model: Model identifier (uses default if None).
            timeout: Max seconds to wait.
            temperature: Sampling temperature (provider default if None).
            max_tokens: Maximum output tokens (provider default if None).

        Returns:
            CompletionResult with the response text and metadata.

        Raises:
            ProviderError: On any provider-specific failure.
        """

    def check_skill_trigger(
        self,
        query: str,
        skill_name: str,
        skill_description: str,
        model: str | None = None,
        timeout: int = 30,
    ) -> TriggerResult:
        """Test whether a query would trigger a skill.

        Default implementation uses complete() with a structured prompt.
        Adapters with native skill/tool infrastructure can override this
        method.

        Args:
            query: The user query to test.
            skill_name: Name of the skill.
            skill_description: The skill's description text.
            model: Model to use (provider default if None).
            timeout: Max seconds to wait.

        Returns:
            TriggerResult indicating whether the skill was triggered.
        """
        prompt = (
            f"You are an AI coding assistant with access to skills. "
            f"You have a skill called \"{skill_name}\" with this description:\n"
            f"---\n{skill_description}\n---\n\n"
            f"A user sends this query:\n"
            f"---\n{query}\n---\n\n"
            f"Would you use the \"{skill_name}\" skill for this query? "
            f"Respond with ONLY a JSON object:\n"
            f'{{"triggered": true/false, "reasoning": "brief explanation"}}'
        )
        try:
            result = self.complete(prompt, model=model, timeout=timeout, temperature=0)
            import json
            import re
            # Try to extract JSON from the response
            json_match = re.search(r'\{[^{}]*"triggered"\s*:\s*(true|false)[^{}]*\}', result.text, re.IGNORECASE)
            if json_match:
                parsed = json.loads(json_match.group())
                return TriggerResult(
                    triggered=parsed.get("triggered", False),
                    reasoning=parsed.get("reasoning", ""),
                    confidence=0.8 if parsed.get("triggered") else 0.2,
                )
            # Fallback: look for yes/no patterns
            lower = result.text.lower()
            triggered = "true" in lower or "yes" in lower.split()[:5]
            return TriggerResult(triggered=triggered, reasoning=result.text[:200])
        except ProviderError as exc:
            return TriggerResult(
                triggered=False,
                reasoning=f"{type(exc).__name__}: {exc}",
            )

    @abstractmethod
    def get_default_model(self) -> str:
        """Return the default model identifier for this provider."""

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the adapter's canonical name."""

    def get_capabilities(self) -> ProviderCapabilities:
        """Return this provider's capability flags."""
        return ProviderCapabilities()

    def is_available(self) -> bool:
        """Check whether this provider is configured and reachable.

        Default implementation returns True. Adapters should override
        to check for API keys, CLI binaries, or network connectivity.
        """
        return True
