"""Abstract LLM provider interface."""

from __future__ import annotations
from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """All LLM providers (local and external) implement this contract."""

    @abstractmethod
    def summarize(self, prompt: str) -> str:
        """Send a prompt and return the LLM's text response."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether the provider is reachable."""
