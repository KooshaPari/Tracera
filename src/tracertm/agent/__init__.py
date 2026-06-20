"""Agent system: per-session sandboxing and AI execution.

Adapted from atomsAgent (clean/deploy) where applicable. Integrates with
Trace AIService; optional Codex/CLIProxy path later.

Phase 5 (NATS Event Streaming):
- Comprehensive event publishing for agent lifecycle
- Session, chat, tool, and snapshot events
- Real-time event streaming via NATS JetStream
"""

from tracertm.agent.agent_service import AgentService, get_agent_service
from tracertm.agent.events import (
    AgentEventPublisher,
    BaseEvent,
    EventSource,
    EventType,
    SessionStatus,
)
from tracertm.agent.graph_session_store import GraphSessionStore
from tracertm.agent.session_store import SessionSandboxStore, SessionSandboxStoreDB
from tracertm.agent.types import (
    ExecutionRequest,
    ExecutionResult,
    SandboxConfig,
    SandboxMetadata,
    SandboxStatus,
)

__all__ = [
    "AgentEventPublisher",
    "AgentService",
    "BaseEvent",
    "EventSource",
    "EventType",
    "ExecutionRequest",
    "ExecutionResult",
    "GraphSessionStore",
    "SandboxConfig",
    "SandboxMetadata",
    "SandboxStatus",
    "SessionSandboxStore",
    "SessionSandboxStoreDB",
    "SessionStatus",
    "get_agent_service",
]
