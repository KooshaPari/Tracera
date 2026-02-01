"""Chat schemas for AI assistant API."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ChatRole(str, Enum):
    """Message role in chat."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AIProvider(str, Enum):
    """Supported AI providers."""

    CLAUDE = "claude"
    CODEX = "codex"
    GEMINI = "gemini"


class ChatMessage(BaseModel):
    """A single chat message."""

    role: ChatRole
    content: str


class ChatContext(BaseModel):
    """Optional context for the chat session."""

    project_id: Optional[str] = None
    project_name: Optional[str] = None
    current_view: Optional[str] = None
    selected_items: Optional[list[dict]] = None


class ChatRequest(BaseModel):
    """Request body for chat streaming endpoint."""

    messages: list[ChatMessage] = Field(..., min_length=1)
    model: str = Field(default="claude-sonnet-4-20250514")
    provider: AIProvider = Field(default=AIProvider.CLAUDE)
    system_prompt: Optional[str] = None
    context: Optional[ChatContext] = None
    max_tokens: int = Field(default=4096, ge=1, le=100000)
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session/chat ID for per-session sandbox; tools run under this sandbox path.",
    )


class ChatStreamChunk(BaseModel):
    """A single chunk in the SSE stream."""

    content: Optional[str] = None
    done: bool = False
    error: Optional[str] = None


class ChatResponse(BaseModel):
    """Non-streaming chat response (for testing)."""

    content: str
    model: str
    provider: AIProvider
    usage: Optional[dict] = None
