"""Agent system: per-session sandboxing and AI execution.

Adapted from atomsAgent (clean/deploy) where applicable. Integrates with
Trace AIService; optional Codex/CLIProxy path later.

Phase 5 (NATS Event Streaming):
- Comprehensive event publishing for agent lifecycle
- Session, chat, tool, and snapshot events
- Real-time event streaming via NATS JetStream
"""

from tracertm.agent.types import (
    SandboxConfig,
    SandboxMetadata,
    SandboxStatus,
    ExecutionRequest,
    ExecutionResult,
)
from tracertm.agent.session_store import SessionSandboxStore, SessionSandboxStoreDB
from tracertm.agent.agent_service import AgentService, get_agent_service
from tracertm.agent.events import (
    AgentEventPublisher,
    EventType,
    EventSource,
    SessionStatus,
    BaseEvent,
)
from tracertm.agent.graph_session_store import GraphSessionStore

__all__ = [
    # Core types
    "SandboxConfig",
    "SandboxMetadata",
    "SandboxStatus",
    "ExecutionRequest",
    "ExecutionResult",
    # Session stores
    "SessionSandboxStore",
    "SessionSandboxStoreDB",
    "GraphSessionStore",
    # Agent service
    "AgentService",
    "get_agent_service",
    # Event streaming
    "AgentEventPublisher",
    "EventType",
    "EventSource",
    "SessionStatus",
    "BaseEvent",
]
