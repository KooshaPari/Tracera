"""Agent service: per-session sandbox + AI execution.

Orchestrates session sandbox resolution and delegates chat to AIService
with working_directory set to the session sandbox path. Publishes comprehensive
lifecycle events via NATS for real-time monitoring and integration.
"""

import logging
import traceback
from collections.abc import AsyncIterator
from dataclasses import dataclass

from tracertm.agent.events import AgentEventPublisher, ChatMessagePayload, SessionStatus
from tracertm.agent.session_store import SessionSandboxStore
from tracertm.agent.types import SandboxConfig

logger = logging.getLogger(__name__)

AGENT_SERVICE_NON_FATAL_ERRORS = (
    AttributeError,
    LookupError,
    TypeError,
    ValueError,
    RuntimeError,
    OSError,
    ConnectionError,
    TimeoutError,
)


@dataclass(frozen=True)
class StreamChatOptions:
    """Options for stream/simple chat (provider, model, limits)."""

    provider: str = "claude"
    model: str | None = None
    system_prompt: str | None = None
    max_tokens: int = 4096
    enable_tools: bool = True


class AgentService:
    """Resolves session sandbox and runs chat via AIService with that working directory."""

    def __init__(
        self,
        session_store: SessionSandboxStore | None = None,
        event_bus: object = None,
        nats_client: object = None,
    ) -> None:
        """Initialize AgentService.

        Args:
            session_store: Optional session sandbox store.
            event_bus: Optional legacy event bus for backward compatibility.
            nats_client: Optional NATS client for publishing agent lifecycle events.
        """
        self._store = session_store or SessionSandboxStore()
        self._event_bus = event_bus  # Legacy EventBus for backward compatibility

        # New dedicated agent event publisher
        self._event_publisher = AgentEventPublisher(nats_client) if nats_client else None

    async def get_or_create_session_sandbox(
        self,
        session_id: str,
        config: SandboxConfig | None = None,
        db_session: object = None,
    ) -> tuple[str | None, bool]:
        """Return (working_directory path or None, created). Publish session.created event when created."""
        if not (session_id and session_id.strip()):
            return None, False

        path, created = await self._store.get_or_create(session_id, config, db_session)

        if created:
            project_id = getattr(config, "project_id", None) if config else None
            provider = getattr(config, "provider", "claude") if config else "claude"
            model = getattr(config, "model", None) if config else None

            # Publish to new event publisher
            if self._event_publisher:
                try:
                    await self._event_publisher.publish_session_created(
                        session_id=session_id,
                        project_id=project_id,
                        sandbox_root=path or "",
                        provider=provider,
                        model=model,
                    )
                except AGENT_SERVICE_NON_FATAL_ERRORS as e:
                    logger.warning("Failed to publish session.created event: %s", e)

            # Legacy EventBus support
            if self._event_bus is not None:
                try:
                    await self._event_bus.publish(  # type: ignore[attr-defined]
                        "agent.session.created",
                        project_id or "",
                        session_id,
                        "agent_session",
                        {"session_id": session_id, "sandbox_root": path, "project_id": project_id},
                    )
                except AGENT_SERVICE_NON_FATAL_ERRORS as e:
                    logger.warning("Failed to publish agent.session.created: %s", e)

        return path, created

    async def _publish_user_message_if_any(
        self, session_id: str, project_id: object, messages: list[dict[str, object]]
    ) -> None:
        """Publish chat message event for the last user message."""
        if not (session_id and self._event_publisher and messages):
            return
        last_message = messages[-1]
        if last_message.get("role") != "user":
            return
        payload = ChatMessagePayload(
            role="user",
            content=str(last_message.get("content", "")),
            turn_number=len(messages) // 2,
            metadata=None,
        )
        try:
            await self._event_publisher.publish_chat_message(
                session_id=session_id,
                project_id=project_id,  # type: ignore[arg-type]
                payload=payload,
            )
        except AGENT_SERVICE_NON_FATAL_ERRORS as e:
            logger.debug("Failed to publish chat message event: %s", e)

    async def _publish_chat_error(self, session_id: str, project_id: object, exc: BaseException) -> None:
        """Publish chat error event; log and swallow publish errors."""
        if not (session_id and self._event_publisher):
            return
        try:
            await self._event_publisher.publish_chat_error(
                session_id=session_id,
                project_id=project_id,  # type: ignore[arg-type]
                error_type=type(exc).__name__,
                error_message=str(exc),
                stack_trace=traceback.format_exc(),
            )
        except AGENT_SERVICE_NON_FATAL_ERRORS as publish_error:
            logger.debug("Failed to publish chat error event: %s", publish_error)

    async def stream_chat_with_sandbox(
        self,
        messages: list[dict[str, object]],
        session_id: str | None = None,
        options: StreamChatOptions | None = None,
        db_session: object = None,
        sandbox_config: SandboxConfig | None = None,
    ) -> AsyncIterator[str]:
        """Stream chat; if session_id is set, use its sandbox as working_directory."""
        opts = options or StreamChatOptions()
        project_id = getattr(sandbox_config, "project_id", None) if sandbox_config else None
        working_directory = None
        if session_id:
            working_directory, _ = await self.get_or_create_session_sandbox(
                session_id,
                config=sandbox_config,
                db_session=db_session,
            )

        from tracertm.services.ai_service import get_ai_service
        from tracertm.services.ai_tools import set_allowed_paths

        if working_directory:
            set_allowed_paths([working_directory])

        await self._publish_user_message_if_any(session_id or "", project_id, messages)
        ai = get_ai_service()

        try:
            async for chunk in ai.stream_chat(
                messages=messages,
                provider=opts.provider,
                model=opts.model,
                system_prompt=opts.system_prompt,
                max_tokens=opts.max_tokens,
                enable_tools=opts.enable_tools,
                working_directory=working_directory,
                db_session=db_session,
            ):
                yield chunk
        except AGENT_SERVICE_NON_FATAL_ERRORS as e:
            await self._publish_chat_error(session_id or "", project_id, e)
            raise

    async def simple_chat_with_sandbox(
        self,
        messages: list[dict[str, object]],
        session_id: str | None = None,
        options: StreamChatOptions | None = None,
        db_session: object = None,
        sandbox_config: SandboxConfig | None = None,
    ) -> str:
        """Non-streaming chat; if session_id is set, use its sandbox as working_directory."""
        opts = options or StreamChatOptions()
        if session_id:
            _working_directory, _ = await self.get_or_create_session_sandbox(
                session_id,
                config=sandbox_config,
                db_session=db_session,
            )

        from tracertm.services.ai_service import get_ai_service

        ai = get_ai_service()
        return await ai.simple_chat(
            messages=messages,
            provider=opts.provider,
            model=opts.model,
            system_prompt=opts.system_prompt,
            max_tokens=opts.max_tokens,
        )

    async def destroy_session(
        self,
        session_id: str,
        reason: str | None = None,
        _db_session: object = None,
    ) -> None:
        """Destroy session sandbox and publish event."""
        project_id = None  # Would need to be fetched from DB if needed

        # Delete from store
        self._store.delete(session_id)

        # Publish destruction event
        if self._event_publisher:
            try:
                await self._event_publisher.publish_session_destroyed(
                    session_id=session_id,
                    project_id=project_id,
                    reason=reason,
                )
            except AGENT_SERVICE_NON_FATAL_ERRORS as e:
                logger.warning("Failed to publish session.destroyed event: %s", e)

    async def update_session_status(
        self,
        session_id: str,
        old_status: SessionStatus,
        new_status: SessionStatus,
        project_id: str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        """Update session status and publish event."""
        if self._event_publisher:
            try:
                await self._event_publisher.publish_session_status_changed(
                    session_id=session_id,
                    project_id=project_id,
                    old_status=old_status,
                    new_status=new_status,
                    details=details,
                )
            except AGENT_SERVICE_NON_FATAL_ERRORS as e:
                logger.warning("Failed to publish session status change event: %s", e)


_agent_service: AgentService | None = None


def get_agent_service(nats_client: object = None) -> AgentService:
    """Get or create the global AgentService instance.

    Args:
        nats_client: Optional NATS client for event publishing

    Returns:
        AgentService instance
    """
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService(nats_client=nats_client)
    return _agent_service
