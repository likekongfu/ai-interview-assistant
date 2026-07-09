import hashlib
import hmac
import os

from jose import jwt

from core.config import SECRET_KEY

ALGORITHM = "HS256"
HASH_NAME = "sha256"
ITERATIONS = 120_000


def hash_password(password: str) -> str:
    """使用 PBKDF2-SHA256 对明文密码加盐哈希。"""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        HASH_NAME,
        password.encode("utf-8"),
        salt,
        ITERATIONS,
    )
    return f"pbkdf2_{HASH_NAME}${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """校验明文密码和数据库中的密码哈希是否匹配。"""
    if not password_hash:
        return False

    if not password_hash.startswith("pbkdf2_"):
        return hmac.compare_digest(password, password_hash)

    _, iterations, salt_hex, digest_hex = password_hash.split("$", 3)
    digest = hashlib.pbkdf2_hmac(
        HASH_NAME,
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        int(iterations),
    )
    return hmac.compare_digest(digest.hex(), digest_hex)


def create_access_token(payload: dict) -> str:
    """根据 payload 生成 JWT 访问令牌。"""
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
