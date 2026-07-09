from fastapi import APIRouter

from schemas import (
    AuthMessageResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    ResetPasswordRequest,
    WechatLoginRequest,
    WechatLoginResponse,
)
from services.auth_service import login_user, login_wechat_user, register_user, reset_password

router = APIRouter()


@router.post("/register", response_model=AuthMessageResponse)
def register(req: RegisterRequest):
    """注册接口：创建新用户。"""
    return register_user(req)


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """登录接口：校验账号密码并返回 JWT。"""
    return login_user(req)


@router.post("/reset_password", response_model=AuthMessageResponse)
def reset_user_password(req: ResetPasswordRequest):
    """忘记密码接口：根据用户名重置密码。"""
    return reset_password(req)


@router.post("/api/auth/wechat/login", response_model=WechatLoginResponse)
def wechat_login(req: WechatLoginRequest):
    """微信小程序登录接口：接收 wx.login code，返回 JWT 和用户资料。"""
    return login_wechat_user(req)
