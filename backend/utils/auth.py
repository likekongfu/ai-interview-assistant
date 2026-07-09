from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from core.config import SECRET_KEY
from core.security import ALGORITHM

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """解析并校验请求头中的 Bearer Token，返回 JWT payload。"""
    try:
        return jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
