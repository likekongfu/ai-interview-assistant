from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class ResetPasswordRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    new_password: str = Field(min_length=6, max_length=128)


class AuthMessageResponse(BaseModel):
    message: str


class LoginResponse(BaseModel):
    token: str
    username: str
    user_id: int


class WechatLoginRequest(BaseModel):
    code: str


class UserProfileResponse(BaseModel):
    avatar_url: str = ""
    nickname: str = ""
    level: int = 1
    answered_count: int = 0
    correct_count: int = 0
    accuracy: int = 0
    streak_days: int = 0
    total_score: int = 0


class WechatLoginResponse(BaseModel):
    token: str
    user: UserProfileResponse


class UpdateProfileRequest(BaseModel):
    nickname: str = ""
    avatar_url: str = ""


class AvatarUploadResponse(BaseModel):
    avatar_url: str
