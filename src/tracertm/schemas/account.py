"""Pydantic schemas for Account API."""

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    """Schema for creating an account."""

    model_config = ConfigDict(strict=True, extra="forbid")

    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=255)
    account_type: str = Field(default="personal", pattern="^(personal|organization)$")


class AccountUpdate(BaseModel):
    """Schema for updating an account."""

    model_config = ConfigDict(strict=True, extra="forbid")

    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=255)
    metadata: dict[str, object] | None = None


class AccountResponse(BaseModel):
    """Schema for account response."""

    id: str
    name: str
    slug: str
    account_type: str
    metadata: dict
    created_at: str
    updated_at: str

    model_config = ConfigDict(strict=True, extra="forbid", from_attributes=True)


class AccountUserResponse(BaseModel):
    """Schema for account user response."""

    id: str
    account_id: str
    user_id: str
    role: str
    joined_at: str

    model_config = ConfigDict(strict=True, extra="forbid", from_attributes=True)


class AccountListResponse(BaseModel):
    """Schema for account list response."""

    model_config = ConfigDict(strict=True, extra="forbid")

    accounts: list[AccountResponse]
    total: int
