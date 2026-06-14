import logging

from langchain_chroma import Chroma
from langchain_core.runnables import RunnableLambda
from langchain_ollama import OllamaEmbeddings

from core.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DB_PATH,
    EMBEDDING_MODEL,
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    TOP_K,
)

logger = logging.getLogger(__name__)

_db = None


def get_retriever(k: int = 3):
    if LLM_PROVIDER == "deepseek":
        logger.info("rag_disabled provider=deepseek reason=no_local_embedding_service")
        return RunnableLambda(lambda _: [])

    return _get_chroma_db().as_retriever(search_kwargs={"k": k or TOP_K})


def _get_chroma_db():
    global _db
    if _db is None:
        logger.info("rag_provider=ollama_embeddings model=%s", EMBEDDING_MODEL)
        _db = Chroma(
            persist_directory=CHROMA_DB_PATH,
            embedding_function=OllamaEmbeddings(
                model=EMBEDDING_MODEL,
                base_url=OLLAMA_BASE_URL,
            ),
            collection_name=CHROMA_COLLECTION_NAME,
        )
    return _db
