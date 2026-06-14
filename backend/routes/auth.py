from fastapi import APIRouter

from schemas import (
    AuthMessageResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    ResetPasswordRequest,
)
from services.auth_service import login_user, register_user, reset_password

router = APIRouter()


@router.post("/register", response_model=AuthMessageResponse)
def register(req: RegisterRequest):
    return register_user(req)


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    return login_user(req)


@router.post("/reset_password", response_model=AuthMessageResponse)
def reset_user_password(req: ResetPasswordRequest):
    return reset_password(req)
