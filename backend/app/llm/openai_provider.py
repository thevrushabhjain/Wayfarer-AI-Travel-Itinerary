"""OpenAI provider implementation using the public `openai` SDK.

Enabled by setting LLM_PROVIDER=openai and OPENAI_API_KEY in the environment.
"""

import json

from openai import AsyncOpenAI
from pydantic import ValidationError
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.core.logging_config import get_logger
from app.llm.base import LLMProvider, LLMProviderError, SchemaT
from app.llm.retry_utils import is_retryable_openai_error
from app.utils.schema_utils import to_openai_strict_schema

logger = get_logger(__name__)


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str | None, model: str) -> None:
        if not api_key:
            raise LLMProviderError(
                "OPENAI_API_KEY is not set. Set LLM_PROVIDER=openai and OPENAI_API_KEY in backend/.env"
            )
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception(is_retryable_openai_error),
    )
    async def generate_structured(
        self,
        prompt: str,
        schema: type[SchemaT],
        system_instruction: str | None = None,
    ) -> SchemaT:
        json_schema = to_openai_strict_schema(schema)
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": schema.__name__,
                        "schema": json_schema,
                        "strict": True,
                    },
                },
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("OpenAI structured generation failed: %s", exc)
            raise LLMProviderError(f"OpenAI API error: {exc}") from exc

        content = response.choices[0].message.content
        if not content:
            raise LLMProviderError("OpenAI returned an empty structured response")

        try:
            data = json.loads(content)
            return schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.error("OpenAI structured output failed validation: %s", exc)
            raise LLMProviderError(f"OpenAI returned invalid structured output: {exc}") from exc

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception(is_retryable_openai_error),
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
            logger.error("OpenAI text generation failed: %s", exc)
            raise LLMProviderError(f"OpenAI API error: {exc}") from exc

        return (response.choices[0].message.content or "").strip()
