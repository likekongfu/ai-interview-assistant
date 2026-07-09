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
    """LLM Provider 初始化或调用失败时抛出的统一异常。"""
    pass


@lru_cache(maxsize=1)
def _get_llm_client():
    """根据环境变量创建并缓存 LLM 客户端。

    本地开发可使用 Ollama，服务器部署可使用 DeepSeek API。
    """
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
    """统一调用当前 LLM Provider，并把返回结果转换成纯文本。"""
    try:
        result = _get_llm_client().invoke(prompt)
    except LLMProviderError:
        raise
    except Exception as exc:
        raise LLMProviderError(f"LLM request failed: {exc}") from exc

    return extract_text(result)


def invoke_llm_json_text(prompt: Any) -> str:
    """调用 LLM 并返回文本，由上层 parse_json_response 解析 JSON。"""
    try:
        client = _get_llm_client()
        if LLM_PROVIDER == "deepseek" and hasattr(client, "bind"):
            client = client.bind(response_format={"type": "json_object"})
        result = client.invoke(prompt)
    except LLMProviderError:
        raise
    except Exception as exc:
        raise LLMProviderError(f"LLM request failed: {exc}") from exc

    return extract_text(result)


def get_llm():
    """返回 LangChain Runnable，供各个 chain 复用统一 LLM Provider。"""
    return RunnableLambda(invoke_llm_text)


def extract_text(result: Any) -> str:
    """兼容字符串、LangChain Message 和其他对象形式的 LLM 返回值。"""
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
