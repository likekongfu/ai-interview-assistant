import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

from fastapi import HTTPException

from core.config import WECHAT_APPID, WECHAT_LOGIN_URL, WECHAT_MOCK_LOGIN, WECHAT_SECRET
from core.security import create_access_token, hash_password, verify_password
from db.crud import (
    create_user,
    create_wechat_user,
    get_user_by_wechat_identity,
    get_user_by_username,
    update_user_last_login,
    update_user_password,
)
from schemas import LoginRequest, RegisterRequest, ResetPasswordRequest, WechatLoginRequest


def _build_token(user):
    expire = datetime.utcnow() + timedelta(hours=24)
    return create_access_token(
        {
            "sub": str(user.id),
            "user_id": user.id,
            "username": user.username or "",
            "client": "quiz",
            "exp": expire,
        }
    )


def _profile(user):
    answered_count = user.answered_count or 0
    correct_count = user.correct_count or 0
    accuracy = int(round(correct_count / answered_count * 100)) if answered_count else 0
    return {
        "avatar_url": user.avatar_url or "",
        "nickname": user.nickname or "微信用户",
        "level": user.level or 1,
        "answered_count": answered_count,
        "correct_count": correct_count,
        "accuracy": accuracy,
        "streak_days": user.streak_days or 0,
        "total_score": user.total_score or 0,
    }


def register_user(req: RegisterRequest):
    """注册新用户，用户名重复时返回 409。"""
    if get_user_by_username(req.username):
        raise HTTPException(status_code=409, detail="User already exists")

    create_user(username=req.username, password=hash_password(req.password))
    return {"message": "Register success"}


def login_user(req: LoginRequest):
    """校验用户名密码并签发 24 小时有效的 JWT。"""
    user = get_user_by_username(req.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if user.password is None:
        raise HTTPException(status_code=400, detail="该账号未设置密码")
    if not verify_password(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not user.password.startswith("pbkdf2_"):
        update_user_password(user.id, hash_password(req.password))

    token = _build_token(user)
    return {"token": token, "username": user.username, "user_id": user.id}


def reset_password(req: ResetPasswordRequest):
    """根据用户名重置密码。当前项目用于忘记密码功能。"""
    user = get_user_by_username(req.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_user_password(user.id, hash_password(req.new_password))
    return {"message": "Password reset success"}


def _wechat_code_to_openid(code: str) -> str:
    if WECHAT_MOCK_LOGIN:
        return f"mock_{code}"
    if not WECHAT_APPID or not WECHAT_SECRET:
        raise HTTPException(status_code=500, detail="Wechat appid/secret not configured")

    query = urllib.parse.urlencode(
        {
            "appid": WECHAT_APPID,
            "secret": WECHAT_SECRET,
            "js_code": code,
            "grant_type": "authorization_code",
        }
    )
    try:
        with urllib.request.urlopen(f"{WECHAT_LOGIN_URL}?{query}", timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Wechat login request failed") from exc

    if data.get("errcode"):
        raise HTTPException(status_code=401, detail=data.get("errmsg", "Wechat login failed"))
    openid = data.get("openid")
    if not openid:
        raise HTTPException(status_code=401, detail="Wechat login did not return openid")
    return openid


def login_wechat_user(req: WechatLoginRequest):
    """微信小程序登录：code 换 openid，创建或读取用户，并签发 JWT。"""
    openid = _wechat_code_to_openid(req.code)
    user = get_user_by_wechat_identity(WECHAT_APPID, openid)
    if not user:
        user = create_wechat_user(openid=openid, appid=WECHAT_APPID)
    user = update_user_last_login(user.id, datetime.utcnow()) or user
    return {"token": _build_token(user), "user": _profile(user)}
