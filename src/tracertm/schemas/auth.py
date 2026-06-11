"""Pydantic schemas for Authentication API."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SignupRequest(BaseModel):
    """Schema for user signup."""

    model_config = ConfigDict(strict=True, extra="forbid")

    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str | None = None
    account_name: str = Field(..., min_length=1, max_length=255)
    account_slug: str | None = None


class LoginRequest(BaseModel):
    """Schema for user login."""

    model_config = ConfigDict(strict=True, extra="forbid")

    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Schema for auth response."""

    model_config = ConfigDict(strict=True, extra="forbid")

    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None
    user: dict[str, object]
    account: dict[str, object] | None = None


class UserResponse(BaseModel):
    """Schema for user response."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str
    email: str
    name: str | None = None
    accounts: list[dict[str, object]] = []


class AccountSwitchRequest(BaseModel):
    """Schema for switching active account."""

    model_config = ConfigDict(strict=True, extra="forbid")

    account_id: str


class DeviceCodeRequest(BaseModel):
    """Schema for device code request."""

    model_config = ConfigDict(strict=True, extra="forbid")

    client_id: str


class DeviceCodeResponse(BaseModel):
    """Schema for device code response (RFC 8628)."""

    model_config = ConfigDict(strict=True, extra="forbid")

    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


class DeviceTokenRequest(BaseModel):
    """Schema for device token request."""

    model_config = ConfigDict(strict=True, extra="forbid")

    device_code: str
    client_id: str


class DeviceTokenResponse(BaseModel):
    """Schema for device token response (RFC 8628)."""

    model_config = ConfigDict(strict=True, extra="forbid")

    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None
    refresh_token: str | None = None
    user: dict[str, object] | None = None
