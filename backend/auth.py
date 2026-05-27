from jose import jwt
from fastapi import Header, HTTPException

SECRET_KEY = "ai_interview"

def verify_token(authorization: str = Header(None)):
    
    print(authorization)
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录")

    try:

        token = authorization.split(" ")[1]

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )

        return payload

    except:
        raise HTTPException(status_code=401, detail="token无效")