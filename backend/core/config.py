from dotenv import load_dotenv
import os

load_dotenv()

def get_env(name: str, default: str) -> str:
    return os.getenv(name, default)


def get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {value!r}") from exc


SECRET_KEY = get_env("SECRET_KEY", "change-me")

DB_HOST = os.getenv("MYSQL_HOST") or get_env("DB_HOST", "localhost")
DB_PORT = get_int_env("DB_PORT", 3306)
DB_USER = get_env("DB_USER", "root")
DB_PASSWORD = get_env("DB_PASSWORD", "")
DB_NAME = get_env("DB_NAME", "ai_interview")

POOL_SIZE = get_int_env("POOL_SIZE", 5)
MAX_OVERFLOW = get_int_env("MAX_OVERFLOW", 10)
POOL_TIMEOUT = get_int_env("POOL_TIMEOUT", 30)
POOL_RECYCLE = get_int_env("POOL_RECYCLE", 1800)
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() in {"1", "true", "yes", "on"}


LLM_PROVIDER = get_env("LLM_PROVIDER", "deepseek").lower()
LLM_TIMEOUT = get_int_env("LLM_TIMEOUT", 60)

OLLAMA_BASE_URL = get_env("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = get_env("OLLAMA_MODEL", "qwen2.5:7b")

DEEPSEEK_API_KEY = get_env("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = get_env("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = get_env("DEEPSEEK_MODEL", "deepseek-v4-flash")

CHROMA_DB_PATH = get_env("CHROMA_DB_PATH", "./chroma_db")
CHROMA_COLLECTION_NAME = get_env("CHROMA_COLLECTION_NAME", "interview_docs")
EMBEDDING_MODEL = get_env("EMBEDDING_MODEL", "nomic-embed-text")

TOP_K = get_int_env("TOP_K", 3)

MAX_FOLLOW_UP = min(get_int_env("MAX_FOLLOW_UP", 3), 3)
