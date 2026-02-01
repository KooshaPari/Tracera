"""Agent service: per-session sandbox + AI execution.

Orchestrates session sandbox resolution and delegates chat to AIService
with working_directory set to the session sandbox path. Publishes comprehensive
lifecycle events via NATS for real-time monitoring and integration.
"""

import logging
import traceback
from collections.abc import AsyncIterator
from typing import Any, Optional

from tracertm.agent.events import AgentEventPublisher, SessionStatus
from tracertm.agent.session_store import SessionSandboxStore
from tracertm.agent.types import SandboxConfig

logger = logging.getLogger(__name__)


class AgentService:
    """Resolves session sandbox and runs chat via AIService with that working directory."""

    def __init__(
        self,
        session_store: Optional[SessionSandboxStore] = None,
        event_bus: Any = None,
        nats_client: Any = None,
    ):
        self._store = session_store or SessionSandboxStore()
        self._event_bus = event_bus  # Legacy EventBus for backward compatibility

        # New dedicated agent event publisher
        self._event_publisher = AgentEventPublisher(nats_client) if nats_client else None

    async def get_or_create_session_sandbox(
        self,
        session_id: str,
        config: Optional[SandboxConfig] = None,
        db_session: Any = None,
    ) -> tuple[Optional[str], bool]:
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
                except Exception as e:
                    logger.warning("Failed to publish session.created event: %s", e)

            # Legacy EventBus support
            if self._event_bus is not None:
                try:
                    await self._event_bus.publish(
                        "agent.session.created",
                        project_id or "",
                        session_id,
                        "agent_session",
                        {"session_id": session_id, "sandbox_root": path, "project_id": project_id},
                    )
                except Exception as e:
                    logger.warning("Failed to publish agent.session.created: %s", e)

        return path, created

    async def stream_chat_with_sandbox(
        self,
        messages: list[dict],
        session_id: Optional[str] = None,
        provider: str = "claude",
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        enable_tools: bool = True,
        db_session: Any = None,
        sandbox_config: Optional[SandboxConfig] = None,
    ) -> AsyncIterator[str]:
        """Stream chat; if session_id is set, use its sandbox as working_directory."""
        working_directory = None
        project_id = getattr(sandbox_config, "project_id", None) if sandbox_config else None

        if session_id:
            working_directory, _ = await self.get_or_create_session_sandbox(
                session_id, config=sandbox_config, db_session=db_session
            )

        from tracertm.services.ai_service import get_ai_service
        from tracertm.services.ai_tools import set_allowed_paths

        if working_directory:
            set_allowed_paths([working_directory])

        # Publish chat message event for user message
        if session_id and self._event_publisher and messages:
            last_message = messages[-1]
            if last_message.get("role") == "user":
                try:
                    await self._event_publisher.publish_chat_message(
                        session_id=session_id,
                        project_id=project_id,
                        role="user",
                        content=str(last_message.get("content", "")),
                        turn_number=len(messages) // 2,  # Approximate turn number
                    )
                except Exception as e:
                    logger.debug(f"Failed to publish chat message event: {e}")

        ai = get_ai_service()

        try:
            async for chunk in ai.stream_chat(
                messages=messages,
                provider=provider,
                model=model,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                enable_tools=enable_tools,
                working_directory=working_directory,
                db_session=db_session,
            ):
                yield chunk

        except Exception as e:
            # Publish error event
            if session_id and self._event_publisher:
                try:
                    await self._event_publisher.publish_chat_error(
                        session_id=session_id,
                        project_id=project_id,
                        error_type=type(e).__name__,
                        error_message=str(e),
                        stack_trace=traceback.format_exc(),
                    )
                except Exception as publish_error:
                    logger.debug(f"Failed to publish chat error event: {publish_error}")
            raise

    async def simple_chat_with_sandbox(
        self,
        messages: list[dict],
        session_id: Optional[str] = None,
        provider: str = "claude",
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        db_session: Any = None,
        sandbox_config: Optional[SandboxConfig] = None,
    ) -> str:
        """Non-streaming chat; if session_id is set, use its sandbox as working_directory."""
        working_directory = None
        if session_id:
            working_directory, _ = await self.get_or_create_session_sandbox(
                session_id, config=sandbox_config, db_session=db_session
            )

        from tracertm.services.ai_service import get_ai_service

        ai = get_ai_service()
        return await ai.simple_chat(
            messages=messages,
            provider=provider,
            model=model,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
        )


    async def destroy_session(
        self,
        session_id: str,
        reason: Optional[str] = None,
        db_session: Any = None,
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
            except Exception as e:
                logger.warning(f"Failed to publish session.destroyed event: {e}")

    async def update_session_status(
        self,
        session_id: str,
        old_status: SessionStatus,
        new_status: SessionStatus,
        project_id: Optional[str] = None,
        details: Optional[dict] = None,
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
            except Exception as e:
                logger.warning(f"Failed to publish session status change event: {e}")


_agent_service: Optional[AgentService] = None


def get_agent_service(nats_client: Any = None) -> AgentService:
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
