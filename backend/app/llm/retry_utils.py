"""Shared helpers to decide whether an LLM provider exception is worth retrying.

Quota/auth/bad-request errors (4xx) should fail fast rather than be retried,
since retrying them only burns quota further without any chance of success.
Transient network/server errors (5xx, timeouts, connection issues) are
retried with exponential backoff.
"""


def is_retryable_gemini_error(exc: BaseException) -> bool:
    from google.genai import errors as genai_errors

    if isinstance(exc, genai_errors.ClientError):
        return False
    return True


def is_retryable_openai_error(exc: BaseException) -> bool:
    import openai

    non_retryable = (
        openai.AuthenticationError,
        openai.PermissionDeniedError,
        openai.RateLimitError,
        openai.BadRequestError,
        openai.NotFoundError,
    )
    if isinstance(exc, non_retryable):
        return False
    return True


def is_retryable_groq_error(exc: BaseException) -> bool:
    import groq

    non_retryable = (
        groq.AuthenticationError,
        groq.PermissionDeniedError,
        groq.RateLimitError,
        groq.BadRequestError,
        groq.NotFoundError,
    )
    if isinstance(exc, non_retryable):
        return False
    return True
