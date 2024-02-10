from pydantic import BaseModel, ConfigDict, EmailStr


class JWTTokenPayload(BaseModel):
    """JWT token payload"""

    sub: str | int
    refresh: bool
    issued_at: int
    expires_at: int


class AccessToken(BaseModel):
    """Access token response"""

    token_type: str
    access_token: str
    expires_at: int
    issued_at: int
    refresh_token: str
    refresh_token_expires_at: int
    refresh_token_issued_at: int

    model_config = ConfigDict(from_attributes=True)


class RefreshToken(BaseModel):
    """Refresh token response"""

    refresh_token: str
