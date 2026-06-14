from datetime import datetime, timedelta

from fastapi import HTTPException

from core.security import create_access_token, hash_password, verify_password
from db.crud import create_user, get_user_by_username, update_user_password
from schemas import LoginRequest, RegisterRequest, ResetPasswordRequest


def register_user(req: RegisterRequest):
    if get_user_by_username(req.username):
        raise HTTPException(status_code=409, detail="User already exists")

    create_user(username=req.username, password=hash_password(req.password))
    return {"message": "Register success"}


def login_user(req: LoginRequest):
    user = get_user_by_username(req.username)
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not user.password.startswith("pbkdf2_"):
        update_user_password(user.id, hash_password(req.password))

    expire = datetime.utcnow() + timedelta(hours=24)
    token = create_access_token(
        {
            "user_id": user.id,
            "username": user.username,
            "exp": expire,
        }
    )
    return {"token": token, "username": user.username, "user_id": user.id}


def reset_password(req: ResetPasswordRequest):
    user = get_user_by_username(req.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_user_password(user.id, hash_password(req.new_password))
    return {"message": "Password reset success"}
