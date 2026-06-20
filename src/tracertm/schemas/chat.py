"""Chat schemas for AI assistant API."""

from enum import StrEnum

from pydantic import BaseModel, Field


class ChatRole(StrEnum):
    """Message role in chat."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AIProvider(StrEnum):
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

    project_id: str | None = None
    project_name: str | None = None
    current_view: str | None = None
    selected_items: list[dict] | None = None


class ChatRequest(BaseModel):
    """Request body for chat streaming endpoint."""

    messages: list[ChatMessage] = Field(..., min_length=1)
    model: str = Field(default="claude-sonnet-4-20250514")
    provider: AIProvider = Field(default=AIProvider.CLAUDE)
    system_prompt: str | None = None
    context: ChatContext | None = None
    max_tokens: int = Field(default=4096, ge=1, le=100000)
    session_id: str | None = Field(
        default=None,
        description="Optional session/chat ID for per-session sandbox; tools run under this sandbox path.",
    )


class ChatStreamChunk(BaseModel):
    """A single chunk in the SSE stream."""

    content: str | None = None
    done: bool = False
    error: str | None = None


class ChatResponse(BaseModel):
    """Non-streaming chat response (for testing)."""

    content: str
    model: str
    provider: AIProvider
    usage: dict | None = None
