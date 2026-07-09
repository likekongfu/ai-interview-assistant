import os
import sys
import types
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BACKEND_ROOT = os.path.dirname(os.path.dirname(__file__))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

if "jose" not in sys.modules:
    jose_module = types.ModuleType("jose")
    jwt_module = types.ModuleType("jwt")
    jwt_module.encode = lambda payload, secret, algorithm=None: "stub-token"
    jwt_module.decode = lambda token, secret, algorithms=None: {}
    jose_module.jwt = jwt_module
    sys.modules["jose"] = jose_module
    sys.modules["jose.jwt"] = jwt_module

from models import User
from schemas import LoginRequest, WechatLoginRequest
from services import auth_service


def user(**kwargs):
    defaults = {
        "id": 1,
        "username": "web_user",
        "password": "pbkdf2_sha256$120000$00$00",
        "wechat_appid": None,
        "wechat_openid": None,
        "nickname": "",
        "avatar_url": "",
        "level": 1,
        "answered_count": 0,
        "correct_count": 0,
        "streak_days": 0,
        "total_score": 0,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def capture_tokens(monkeypatch):
    payloads = []

    def fake_create_access_token(payload):
        payloads.append(payload)
        return f"token-{payload['user_id']}"

    monkeypatch.setattr(auth_service, "create_access_token", fake_create_access_token)
    return payloads


@pytest.fixture
def sqlite_session_local():
    engine = create_engine("sqlite:///:memory:")
    User.__table__.create(bind=engine)
    return sessionmaker(bind=engine)


def test_web_username_password_login_still_success(monkeypatch, sqlite_session_local):
    payloads = capture_tokens(monkeypatch)
    with sqlite_session_local() as db:
        db.add(User(username="alice", password="pbkdf2_sha256$120000$00$00"))
        db.commit()

    monkeypatch.setattr(auth_service, "SessionLocal", sqlite_session_local)
    monkeypatch.setattr(auth_service, "verify_password", lambda password, hashed: True)

    result = auth_service.login_user(LoginRequest(username="alice", password="secret123"))
    payload = payloads[0]

    assert result["username"] == "alice"
    assert result["user_id"] == 1
    assert payload["user_id"] == 1
    assert payload["sub"] == "1"
    assert payload["client"] == "quiz"


def test_wechat_first_login_creates_user(monkeypatch, sqlite_session_local):
    payloads = capture_tokens(monkeypatch)

    monkeypatch.setattr(auth_service, "WECHAT_APPID", "quiz_appid")
    monkeypatch.setattr(auth_service, "_wechat_code_to_openid", lambda code: "openid_a")
    monkeypatch.setattr(auth_service, "SessionLocal", sqlite_session_local)

    result = auth_service.login_wechat_user(WechatLoginRequest(code="code_a"))
    with sqlite_session_local() as db:
        users = db.query(User).all()

    assert len(users) == 1
    assert users[0].username is None
    assert users[0].password is None
    assert users[0].wechat_appid == "quiz_appid"
    assert users[0].wechat_openid == "openid_a"
    assert result["token"] == f"token-{users[0].id}"
    assert result["user"]["nickname"] == "微信用户"
    assert payloads[0]["client"] == "quiz"
    assert payloads[0]["user_id"] == users[0].id


def test_same_wechat_user_second_login_reuses_user(monkeypatch, sqlite_session_local):
    payloads = capture_tokens(monkeypatch)

    monkeypatch.setattr(auth_service, "WECHAT_APPID", "quiz_appid")
    monkeypatch.setattr(auth_service, "_wechat_code_to_openid", lambda code: "same_openid")
    monkeypatch.setattr(auth_service, "SessionLocal", sqlite_session_local)

    first = auth_service.login_wechat_user(WechatLoginRequest(code="first"))
    second = auth_service.login_wechat_user(WechatLoginRequest(code="second"))
    with sqlite_session_local() as db:
        users = db.query(User).all()

    assert len(users) == 1
    assert first["token"]
    assert second["token"]
    assert first["user"]["nickname"] == "微信用户"
    assert second["user"]["nickname"] == "微信用户"
    assert payloads[0]["user_id"] == payloads[1]["user_id"]


def test_different_openid_creates_different_users(monkeypatch, sqlite_session_local):
    capture_tokens(monkeypatch)

    monkeypatch.setattr(auth_service, "WECHAT_APPID", "quiz_appid")
    monkeypatch.setattr(auth_service, "_wechat_code_to_openid", lambda code: f"openid_{code}")
    monkeypatch.setattr(auth_service, "SessionLocal", sqlite_session_local)

    auth_service.login_wechat_user(WechatLoginRequest(code="a"))
    auth_service.login_wechat_user(WechatLoginRequest(code="b"))
    with sqlite_session_local() as db:
        users = db.query(User).all()

    assert len(users) == 2


def test_wechat_identity_unique_constraint_exists():
    constraints = [
        constraint
        for constraint in User.__table__.constraints
        if getattr(constraint, "name", "") == "uq_users_wechat_identity"
    ]

    assert constraints
    assert [column.name for column in constraints[0].columns] == ["wechat_appid", "wechat_openid"]


def test_wechat_user_password_login_returns_clear_error(monkeypatch, sqlite_session_local):
    with sqlite_session_local() as db:
        db.add(User(username="wx_user", password=None))
        db.commit()

    monkeypatch.setattr(auth_service, "SessionLocal", sqlite_session_local)

    with pytest.raises(HTTPException) as exc:
        auth_service.login_user(LoginRequest(username="wx_user", password="secret123"))

    assert exc.value.status_code == 400
    assert exc.value.detail == "该账号未设置密码"


def test_token_contains_user_id_and_quiz_client():
    payloads = []
    original = auth_service.create_access_token
    auth_service.create_access_token = lambda payload: payloads.append(payload) or "token"
    try:
        token = auth_service._build_token_by_user_id(88)
    finally:
        auth_service.create_access_token = original
    payload = payloads[0]

    assert token == "token"
    assert payload["user_id"] == 88
    assert payload["sub"] == "88"
    assert payload["client"] == "quiz"


def test_profile_accuracy_zero_when_answered_count_zero():
    profile = auth_service._profile(user(answered_count=0, correct_count=0))

    assert profile["accuracy"] == 0
