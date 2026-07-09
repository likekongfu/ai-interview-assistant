import os
from pathlib import Path


def get_upload_dir() -> Path:
    upload_dir = Path(os.getenv("UPLOAD_DIR", "/app/uploads")).expanduser()
    upload_dir = upload_dir if upload_dir.is_absolute() else upload_dir.resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir
