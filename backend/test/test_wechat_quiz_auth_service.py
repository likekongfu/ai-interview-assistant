import os
import sys
import types
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

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


def test_web_username_password_login_still_success(monkeypatch):
    payloads = capture_tokens(monkeypatch)
    web_user = user(id=10, username="alice")
    monkeypatch.setattr(auth_service, "get_user_by_username", lambda username: web_user)
    monkeypatch.setattr(auth_service, "verify_password", lambda password, hashed: True)

    result = auth_service.login_user(LoginRequest(username="alice", password="secret123"))
    payload = payloads[0]

    assert result["username"] == "alice"
    assert result["user_id"] == 10
    assert payload["user_id"] == 10
    assert payload["sub"] == "10"
    assert payload["client"] == "quiz"


def test_wechat_first_login_creates_user(monkeypatch):
    payloads = capture_tokens(monkeypatch)
    created = []
    wx_user = user(
        id=20,
        username=None,
        password=None,
        wechat_appid="quiz_appid",
        wechat_openid="openid_a",
        nickname="微信用户",
    )

    monkeypatch.setattr(auth_service, "WECHAT_APPID", "quiz_appid")
    monkeypatch.setattr(auth_service, "_wechat_code_to_openid", lambda code: "openid_a")
    monkeypatch.setattr(auth_service, "get_user_by_wechat_identity", lambda appid, openid: None)
    monkeypatch.setattr(
        auth_service,
        "create_wechat_user",
        lambda openid, appid: created.append((appid, openid)) or wx_user,
    )
    monkeypatch.setattr(auth_service, "update_user_last_login", lambda user_id, login_at: wx_user)

    result = auth_service.login_wechat_user(WechatLoginRequest(code="code_a"))

    assert created == [("quiz_appid", "openid_a")]
    assert result["user"]["nickname"] == "微信用户"
    assert payloads[0]["client"] == "quiz"


def test_same_wechat_user_second_login_reuses_user(monkeypatch):
    payloads = capture_tokens(monkeypatch)
    users = {}
    create_count = {"value": 0}

    def get_user(appid, openid):
        return users.get((appid, openid))

    def create_user(openid, appid):
        create_count["value"] += 1
        users[(appid, openid)] = user(
            id=create_count["value"],
            username=None,
            password=None,
            wechat_appid=appid,
            wechat_openid=openid,
            nickname="微信用户",
        )
        return users[(appid, openid)]

    monkeypatch.setattr(auth_service, "WECHAT_APPID", "quiz_appid")
    monkeypatch.setattr(auth_service, "_wechat_code_to_openid", lambda code: "same_openid")
    monkeypatch.setattr(auth_service, "get_user_by_wechat_identity", get_user)
    monkeypatch.setattr(auth_service, "create_wechat_user", create_user)
    monkeypatch.setattr(auth_service, "update_user_last_login", lambda user_id, login_at: users[("quiz_appid", "same_openid")])

    auth_service.login_wechat_user(WechatLoginRequest(code="first"))
    auth_service.login_wechat_user(WechatLoginRequest(code="second"))

    assert create_count["value"] == 1
    assert payloads[0]["user_id"] == payloads[1]["user_id"]


def test_different_openid_creates_different_users(monkeypatch):
    capture_tokens(monkeypatch)
    users = {}

    def create_user(openid, appid):
        created = user(
            id=len(users) + 1,
            username=None,
            password=None,
            wechat_appid=appid,
            wechat_openid=openid,
            nickname="微信用户",
        )
        users[(appid, openid)] = created
        return created

    monkeypatch.setattr(auth_service, "WECHAT_APPID", "quiz_appid")
    monkeypatch.setattr(auth_service, "_wechat_code_to_openid", lambda code: f"openid_{code}")
    monkeypatch.setattr(auth_service, "get_user_by_wechat_identity", lambda appid, openid: users.get((appid, openid)))
    monkeypatch.setattr(auth_service, "create_wechat_user", create_user)
    monkeypatch.setattr(auth_service, "update_user_last_login", lambda user_id, login_at: next(item for item in users.values() if item.id == user_id))

    auth_service.login_wechat_user(WechatLoginRequest(code="a"))
    auth_service.login_wechat_user(WechatLoginRequest(code="b"))

    assert len(users) == 2


def test_wechat_identity_unique_constraint_exists():
    constraints = [
        constraint
        for constraint in User.__table__.constraints
        if getattr(constraint, "name", "") == "uq_users_wechat_identity"
    ]

    assert constraints
    assert [column.name for column in constraints[0].columns] == ["wechat_appid", "wechat_openid"]


def test_wechat_user_password_login_returns_clear_error(monkeypatch):
    wx_user = user(username="wx_user", password=None)
    monkeypatch.setattr(auth_service, "get_user_by_username", lambda username: wx_user)

    with pytest.raises(HTTPException) as exc:
        auth_service.login_user(LoginRequest(username="wx_user", password="secret123"))

    assert exc.value.status_code == 400
    assert exc.value.detail == "该账号未设置密码"


def test_token_contains_user_id_and_quiz_client():
    payloads = []
    original = auth_service.create_access_token
    auth_service.create_access_token = lambda payload: payloads.append(payload) or "token"
    try:
        token = auth_service._build_token(user(id=88, username=None, password=None))
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
