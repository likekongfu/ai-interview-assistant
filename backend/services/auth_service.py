import json
import logging
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

from fastapi import HTTPException

from core.config import WECHAT_APPID, WECHAT_LOGIN_URL, WECHAT_MOCK_LOGIN, WECHAT_SECRET
from core.security import create_access_token, hash_password, verify_password
from db.crud import (
    create_user,
    get_user_by_username,
)
from db.database import SessionLocal
from models import User
from schemas import LoginRequest, RegisterRequest, ResetPasswordRequest, WechatLoginRequest

logger = logging.getLogger(__name__)


def _build_token_by_user_id(user_id: int):
    expire = datetime.utcnow() + timedelta(hours=24)
    return create_access_token(
        {
            "sub": str(user_id),
            "user_id": user_id,
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
    with SessionLocal() as db:
        user = db.query(User).filter(User.username == req.username).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        if user.password is None:
            raise HTTPException(status_code=400, detail="该账号未设置密码")
        if not verify_password(req.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        if not user.password.startswith("pbkdf2_"):
            user.password = hash_password(req.password)
            db.commit()
            db.refresh(user)

        user_id = user.id
        username = user.username

    token = _build_token_by_user_id(user_id)
    return {"token": token, "username": username, "user_id": user_id}


def reset_password(req: ResetPasswordRequest):
    """根据用户名重置密码。当前项目用于忘记密码功能。"""
    with SessionLocal() as db:
        user = db.query(User).filter(User.username == req.username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.password = hash_password(req.new_password)
        db.commit()
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
    try:
        with SessionLocal() as db:
            user = (
                db.query(User)
                .filter(User.wechat_appid == WECHAT_APPID, User.wechat_openid == openid)
                .first()
            )
            if not user:
                user = User(
                    username=None,
                    password=None,
                    wechat_appid=WECHAT_APPID,
                    wechat_openid=openid,
                    nickname="微信用户",
                    avatar_url="",
                    level=1,
                    answered_count=0,
                    correct_count=0,
                    streak_days=0,
                    total_score=0,
                )
                db.add(user)

            user.last_login_at = datetime.utcnow()
            db.commit()
            db.refresh(user)

            user_id = user.id
            profile = _profile(user)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Wechat login database operation failed")
        raise HTTPException(status_code=500, detail="登录服务暂时不可用") from exc

    return {"token": _build_token_by_user_id(user_id), "user": profile}
