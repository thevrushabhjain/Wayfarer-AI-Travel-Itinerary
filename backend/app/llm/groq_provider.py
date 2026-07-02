"""Groq provider implementation using the public `groq` SDK.

Enabled by setting LLM_PROVIDER=groq and GROQ_API_KEY in the environment.
Groq's chat completions API is OpenAI-compatible; JSON-object mode is used
for structured generation and validated with Pydantic on our side, since
strict JSON-schema enforcement support varies by hosted model.
"""

import json

from groq import AsyncGroq
from pydantic import ValidationError
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.core.logging_config import get_logger
from app.llm.base import LLMProvider, LLMProviderError, SchemaT
from app.llm.retry_utils import is_retryable_groq_error

logger = get_logger(__name__)


class GroqProvider(LLMProvider):
    def __init__(self, api_key: str | None, model: str) -> None:
        if not api_key:
            raise LLMProviderError(
                "GROQ_API_KEY is not set. Set LLM_PROVIDER=groq and GROQ_API_KEY in backend/.env"
            )
        self.client = AsyncGroq(api_key=api_key)
        self.model = model

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception(is_retryable_groq_error),
    )
    async def generate_structured(
        self,
        prompt: str,
        schema: type[SchemaT],
        system_instruction: str | None = None,
    ) -> SchemaT:
        schema_hint = json.dumps(schema.model_json_schema())
        base_instruction = system_instruction or "You are a precise JSON-generating assistant."
        full_instruction = (
            f"{base_instruction}\n\nRespond with ONLY a single JSON object that strictly matches this "
            f"JSON Schema (no prose, no markdown fences):\n{schema_hint}"
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": full_instruction},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                response_format={"type": "json_object"},
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Groq structured generation failed: %s", exc)
            raise LLMProviderError(f"Groq API error: {exc}") from exc

        content = response.choices[0].message.content
        if not content:
            raise LLMProviderError("Groq returned an empty structured response")

        try:
            data = json.loads(content)
            return schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.error("Groq structured output failed validation: %s", exc)
            raise LLMProviderError(f"Groq returned invalid structured output: {exc}") from exc

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception(is_retryable_groq_error),
    )
    async def generate_text(self, prompt: str, system_instruction: str | None = None) -> str:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Groq text generation failed: %s", exc)
            raise LLMProviderError(f"Groq API error: {exc}") from exc

        return (response.choices[0].message.content or "").strip()
