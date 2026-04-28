"""Pydantic schemas for Authentication API."""

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Schema for user signup."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str | None = None
    account_name: str = Field(..., min_length=1, max_length=255)
    account_slug: str | None = None


class LoginRequest(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Schema for auth response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None
    user: dict[str, object]
    account: dict[str, object] | None = None


class UserResponse(BaseModel):
    """Schema for user response."""

    id: str
    email: str
    name: str | None = None
    accounts: list[dict[str, object]] = []


class AccountSwitchRequest(BaseModel):
    """Schema for switching active account."""

    account_id: str


class DeviceCodeRequest(BaseModel):
    """Schema for device code request."""

    client_id: str


class DeviceCodeResponse(BaseModel):
    """Schema for device code response (RFC 8628)."""

    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


class DeviceTokenRequest(BaseModel):
    """Schema for device token request."""

    device_code: str
    client_id: str


class DeviceTokenResponse(BaseModel):
    """Schema for device token response (RFC 8628)."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None
    refresh_token: str | None = None
    user: dict[str, object] | None = None
