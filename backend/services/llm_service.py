import logging
from functools import lru_cache
from typing import Any

from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableLambda
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI

from core.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    LLM_PROVIDER,
    LLM_TIMEOUT,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)

logger = logging.getLogger(__name__)


class LLMProviderError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _get_llm_client():
    if LLM_PROVIDER == "ollama":
        logger.info("llm_provider=ollama model=%s base_url=%s", OLLAMA_MODEL, OLLAMA_BASE_URL)
        return OllamaLLM(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            timeout=LLM_TIMEOUT,
        )

    if LLM_PROVIDER == "deepseek":
        if not DEEPSEEK_API_KEY:
            raise LLMProviderError("DEEPSEEK_API_KEY is required when LLM_PROVIDER=deepseek")

        logger.info("llm_provider=deepseek model=%s base_url=%s", DEEPSEEK_MODEL, DEEPSEEK_BASE_URL)
        return ChatOpenAI(
            model=DEEPSEEK_MODEL,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            timeout=LLM_TIMEOUT,
            temperature=0.2,
        )

    raise LLMProviderError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")


def invoke_llm_text(prompt: Any) -> str:
    try:
        result = _get_llm_client().invoke(prompt)
    except LLMProviderError:
        raise
    except Exception as exc:
        raise LLMProviderError(f"LLM request failed: {exc}") from exc

    return extract_text(result)


def get_llm():
    return RunnableLambda(invoke_llm_text)


def extract_text(result: Any) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, BaseMessage):
        content = result.content
        if isinstance(content, str):
            return content
        return "".join(str(part) for part in content)
    if hasattr(result, "content"):
        content = result.content
        if isinstance(content, str):
            return content
    return str(result)
