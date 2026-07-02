"""Factory that selects the active LLM provider purely from environment configuration."""

from functools import lru_cache

from app.core.config import settings
from app.llm.base import LLMProvider, LLMProviderError
from app.llm.gemini_provider import GeminiProvider
from app.llm.groq_provider import GroqProvider
from app.llm.openai_provider import OpenAIProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    provider_name = settings.llm_provider.strip().lower()

    if provider_name == "gemini":
        return GeminiProvider(api_key=settings.gemini_api_key, model=settings.gemini_model)
    if provider_name == "openai":
        return OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_model)
    if provider_name == "groq":
        return GroqProvider(api_key=settings.groq_api_key, model=settings.groq_model)

    raise LLMProviderError(
        f"Unsupported LLM_PROVIDER '{provider_name}'. Use one of: gemini, openai, groq."
    )
