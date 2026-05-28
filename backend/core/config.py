from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

POOL_SIZE=int(os.getenv("POOL_SIZE"))
MAX_OVERFLOW=int(os.getenv("MAX_OVERFLOW"))
POOL_TIMEOUT=int(os.getenv("POOL_TIMEOUT"))
POOL_RECYCLE=int(os.getenv("POOL_RECYCLE"))


OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")