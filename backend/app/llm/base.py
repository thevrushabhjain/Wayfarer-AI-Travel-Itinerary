"""Abstract LLM provider interface.

Every concrete provider (Gemini, OpenAI, Groq) implements this exact
interface, so the rest of the application never depends on a specific
vendor SDK. Switching providers is a matter of changing the
``LLM_PROVIDER`` environment variable.
"""

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class LLMProviderError(Exception):
    """Raised when the underlying LLM call fails after retries."""


class LLMProvider(ABC):
    """Base class for all LLM provider implementations."""

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: type[SchemaT],
        system_instruction: str | None = None,
    ) -> SchemaT:
        """Generate a response constrained to the given Pydantic schema.

        Returns a validated instance of ``schema``.
        """
        raise NotImplementedError

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> str:
        """Generate a free-form text response (used for conversational replies)."""
        raise NotImplementedError
