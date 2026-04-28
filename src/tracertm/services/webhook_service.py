"""Webhook Service for processing inbound webhooks."""

from __future__ import annotations

import hashlib
import hmac
import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy.exc import OperationalError

from tracertm.constants import (
    HTTP_BAD_REQUEST,
    HTTP_OK,
    HTTP_TOO_MANY_REQUESTS,
    HTTP_UNAUTHORIZED,
    PREVIEW_SIZE_DEFAULT,
)
from tracertm.models.webhook_integration import WebhookStatus
from tracertm.repositories.test_run_repository import TestRunRepository
from tracertm.repositories.webhook_repository import WebhookRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from tracertm.models.webhook_integration import WebhookIntegration


class WebhookService:
    """Service for processing webhook requests.

    Functional Requirements:
    - FR-DISC-005

    User Stories:
    - US-WEBHOOK-001

    Epics:
    - EPIC-001
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.webhook_repo: WebhookRepository = WebhookRepository(session)
        self.test_run_repo: TestRunRepository = TestRunRepository(session)

    def verify_signature(
        self,
        secret: str,
        payload: bytes,
        signature: str,
        algorithm: str = "sha256",
    ) -> bool:
        """Verify HMAC signature of webhook payload.

        Supports common signature formats:
        - sha256=<hex_signature>
        - <hex_signature>
        """
        # Extract the actual signature if prefixed
        if "=" in signature:
            parts = signature.split("=", 1)
            algorithm = parts[0].lower()
            signature = parts[1]

        # Compute expected signature
        if algorithm == "sha256":
            expected = hmac.new(
                secret.encode("utf-8"),
                payload,
                hashlib.sha256,
            ).hexdigest()
        elif algorithm == "sha1":
            expected = hmac.new(
                secret.encode("utf-8"),
                payload,
                hashlib.sha1,
            ).hexdigest()
        else:
            # Default to sha256
            expected = hmac.new(
                secret.encode("utf-8"),
                payload,
                hashlib.sha256,
            ).hexdigest()

        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected.lower(), signature.lower())

    async def process_inbound_webhook(
        self,
        webhook_id: str,
        payload: dict[str, Any],
        raw_payload: bytes,
        signature: str | None = None,
        headers: dict[str, str] | None = None,
        source_ip: str | None = None,
        user_agent: str | None = None,
    ) -> dict[str, Any]:
        """Process an inbound webhook request.

        Returns a response dict with:
        - success: bool
        - message: str
        - data: optional result data
        - error: optional error message
        """
        start_time = time.time()
        headers = headers or {}

        # Get webhook configuration
        webhook = await self.webhook_repo.get_by_id(webhook_id)
        if not webhook:
            return {
                "success": False,
                "message": "Webhook not found",
                "error": "Invalid webhook ID",
            }

        # Check if active
        if webhook.status != WebhookStatus.ACTIVE:
            return {
                "success": False,
                "message": f"Webhook is {webhook.status.value}",
                "error": "Webhook is not active",
            }

        # Check rate limit
        allowed, remaining = await self.webhook_repo.check_rate_limit(webhook_id)
        if not allowed:
            processing_time = int((time.time() - start_time) * 1000)
            await self.webhook_repo.create_log(
                webhook_id=webhook_id,
                event_type=payload.get("action"),
                source_ip=source_ip,
                user_agent=user_agent,
                request_headers=headers,
                request_body_preview=str(payload)[:PREVIEW_SIZE_DEFAULT],
                payload_size_bytes=len(raw_payload),
                success=False,
                status_code=HTTP_TOO_MANY_REQUESTS,
                error_message="Rate limit exceeded",
                processing_time_ms=processing_time,
            )
            await self.webhook_repo.record_request(webhook_id, success=False, error_message="Rate limit exceeded")
            return {
                "success": False,
                "message": "Rate limit exceeded",
                "error": "Too many requests",
                "rate_limit_remaining": remaining,
            }

        # Verify signature if required
        if webhook.verify_signatures:
            if not signature:
                # Try common header names
                signature = (
                    headers.get("X-Hub-Signature-256")
                    or headers.get("X-Hub-Signature")
                    or headers.get("X-Signature")
                    or headers.get("X-Webhook-Signature")
                )

            if not signature:
                processing_time = int((time.time() - start_time) * 1000)
                await self.webhook_repo.create_log(
                    webhook_id=webhook_id,
                    event_type=payload.get("action"),
                    source_ip=source_ip,
                    user_agent=user_agent,
                    request_headers=headers,
                    success=False,
                    status_code=HTTP_UNAUTHORIZED,
                    error_message="Missing signature",
                    processing_time_ms=processing_time,
                )
                await self.webhook_repo.record_request(webhook_id, success=False, error_message="Missing signature")
                return {
                    "success": False,
                    "message": "Missing signature",
                    "error": "Signature verification required",
                }

            if not self.verify_signature(webhook.webhook_secret, raw_payload, signature):
                processing_time = int((time.time() - start_time) * 1000)
                await self.webhook_repo.create_log(
                    webhook_id=webhook_id,
                    event_type=payload.get("action"),
                    source_ip=source_ip,
                    user_agent=user_agent,
                    request_headers=headers,
                    success=False,
                    status_code=HTTP_UNAUTHORIZED,
                    error_message="Invalid signature",
                    processing_time_ms=processing_time,
                )
                await self.webhook_repo.record_request(webhook_id, success=False, error_message="Invalid signature")
                return {
                    "success": False,
                    "message": "Invalid signature",
                    "error": "Signature verification failed",
                }

        # Process based on action type
        action = payload.get("action", "submit_result")
        event_payload = payload.get("payload", payload)

        try:
            result_data = {}
            test_run_id = None
            results_submitted = 0

            if action == "create_run":
                result_data = await self._handle_create_run(webhook, event_payload)
                test_run_id = result_data.get("run_id")

            elif action == "start_run":
                result_data = await self._handle_start_run(event_payload)
                test_run_id = event_payload.get("run_id")

            elif action == "submit_result":
                result_data = await self._handle_submit_result(webhook, event_payload)
                test_run_id = event_payload.get("run_id")
                results_submitted = 1

            elif action == "bulk_results":
                result_data = await self._handle_bulk_results(webhook, event_payload)
                test_run_id = event_payload.get("run_id")
                results_submitted = result_data.get("submitted", 0)

            elif action == "complete_run":
                result_data = await self._handle_complete_run(event_payload)
                test_run_id = event_payload.get("run_id")

            else:
                msg = f"Unknown action: {action}"
                raise ValueError(msg)

            # Log success
            processing_time = int((time.time() - start_time) * 1000)
            await self.webhook_repo.create_log(
                webhook_id=webhook_id,
                event_type=action,
                source_ip=source_ip,
                user_agent=user_agent,
                request_headers=headers,
                request_body_preview=str(payload)[:PREVIEW_SIZE_DEFAULT],
                payload_size_bytes=len(raw_payload),
                success=True,
                status_code=HTTP_OK,
                processing_time_ms=processing_time,
                test_run_id=test_run_id,
                results_submitted=results_submitted,
            )
            await self.webhook_repo.record_request(webhook_id, success=True)

            return {
                "success": True,
                "message": f"Action '{action}' processed successfully",
                "data": result_data,
                "rate_limit_remaining": remaining - 1,
            }

        except (ValueError, KeyError, OperationalError) as e:
            processing_time = int((time.time() - start_time) * 1000)
            error_message = str(e)
            await self.webhook_repo.create_log(
                webhook_id=webhook_id,
                event_type=action,
                source_ip=source_ip,
                user_agent=user_agent,
                request_headers=headers,
                request_body_preview=str(payload)[:PREVIEW_SIZE_DEFAULT],
                payload_size_bytes=len(raw_payload),
                success=False,
                status_code=HTTP_BAD_REQUEST,
                error_message=error_message,
                processing_time_ms=processing_time,
            )
            await self.webhook_repo.record_request(webhook_id, success=False, error_message=error_message)

            return {
                "success": False,
                "message": f"Failed to process action '{action}'",
                "error": error_message,
            }

    async def _handle_create_run(
        self,
        webhook: WebhookIntegration,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle create_run action."""
        name = payload.get("name", f"CI/CD Run - {datetime.now(UTC).isoformat()}")
        run = await self.test_run_repo.create(
            project_id=webhook.project_id,
            name=name,
            description=payload.get("description"),
            suite_id=payload.get("suite_id") or webhook.default_suite_id,
            run_type="ci_cd",
            environment=payload.get("environment"),
            build_number=payload.get("build_number"),
            build_url=payload.get("build_url"),
            branch=payload.get("branch"),
            commit_sha=payload.get("commit_sha"),
            initiated_by=payload.get("initiated_by"),
            external_run_id=payload.get("external_run_id"),
            webhook_id=webhook.id,
        )
        return {
            "run_id": run.id,
            "run_number": run.run_number,
        }

    async def _handle_start_run(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle start_run action."""
        run_id = payload.get("run_id")
        if not run_id:
            msg = "run_id is required"
            raise ValueError(msg)

        run = await self.test_run_repo.start(
            run_id,
            executed_by=payload.get("executed_by"),
        )
        if not run:
            msg = "Test run not found"
            raise ValueError(msg)

        return {
            "run_id": run.id,
            "status": run.status.value,
            "started_at": run.started_at.isoformat() if run.started_at else None,
        }

    async def _handle_submit_result(
        self,
        webhook: WebhookIntegration,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle submit_result action."""
        run_id = payload.get("run_id")

        # Auto-create run if enabled and no run_id provided
        if not run_id and webhook.auto_create_run:
            create_result = await self._handle_create_run(
                webhook,
                {
                    "name": f"Auto-created run - {datetime.now(UTC).isoformat()}",
                    "build_number": payload.get("build_number"),
                    "branch": payload.get("branch"),
                    "commit_sha": payload.get("commit_sha"),
                },
            )
            run_id = create_result["run_id"]
            # Auto-start the run
            await self.test_run_repo.start(run_id)

        if not run_id:
            msg = "run_id is required or auto_create_run must be enabled"
            raise ValueError(msg)

        test_case_id = payload.get("test_case_id")
        if not test_case_id:
            msg = "test_case_id is required"
            raise ValueError(msg)

        result = await self.test_run_repo.add_result(
            run_id=run_id,
            test_case_id=test_case_id,
            status=payload.get("status", "passed"),
            executed_by=payload.get("executed_by"),
            actual_result=payload.get("actual_result"),
            failure_reason=payload.get("failure_reason"),
            error_message=payload.get("error_message"),
            stack_trace=payload.get("stack_trace"),
            duration_seconds=payload.get("duration_seconds"),
            screenshots=payload.get("screenshots"),
            logs_url=payload.get("logs_url"),
            notes=payload.get("notes"),
            is_flaky=payload.get("is_flaky", False),
        )

        return {
            "result_id": result.id,
            "run_id": run_id,
            "status": result.status.value if hasattr(result.status, "value") else result.status,
        }

    async def _handle_bulk_results(
        self,
        webhook: WebhookIntegration,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle bulk_results action."""
        run_id = payload.get("run_id")

        # Auto-create run if enabled and no run_id provided
        if not run_id and webhook.auto_create_run:
            create_result = await self._handle_create_run(
                webhook,
                {
                    "name": f"Auto-created run - {datetime.now(UTC).isoformat()}",
                    "build_number": payload.get("build_number"),
                    "branch": payload.get("branch"),
                    "commit_sha": payload.get("commit_sha"),
                },
            )
            run_id = create_result["run_id"]
            await self.test_run_repo.start(run_id)

        if not run_id:
            msg = "run_id is required or auto_create_run must be enabled"
            raise ValueError(msg)

        results = payload.get("results", [])
        if not results:
            msg = "results array is required"
            raise ValueError(msg)

        # Submit each result
        submitted = 0
        for result_data in results:
            test_case_id = result_data.get("test_case_id")
            if not test_case_id:
                continue
            await self.test_run_repo.add_result(
                run_id=run_id,
                test_case_id=test_case_id,
                status=result_data.get("status", "passed"),
                executed_by=result_data.get("executed_by"),
                actual_result=result_data.get("actual_result"),
                failure_reason=result_data.get("failure_reason"),
                error_message=result_data.get("error_message"),
                duration_seconds=result_data.get("duration_seconds"),
                is_flaky=result_data.get("is_flaky", False),
            )
            submitted += 1

        # Auto-complete run if enabled
        run = await self.test_run_repo.get_by_id(run_id)
        if run and webhook.auto_complete_run and payload.get("complete"):
            await self.test_run_repo.complete(run_id)

        return {
            "run_id": run_id,
            "submitted": submitted,
            "run_status": run.status.value if run and hasattr(run.status, "value") else None,
            "pass_rate": run.pass_rate if run else None,
        }

    async def _handle_complete_run(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle complete_run action."""
        run_id = payload.get("run_id")
        if not run_id:
            msg = "run_id is required"
            raise ValueError(msg)

        run = await self.test_run_repo.complete(
            run_id,
            failure_summary=payload.get("failure_summary"),
            notes=payload.get("notes"),
        )
        if not run:
            msg = "Test run not found"
            raise ValueError(msg)

        return {
            "run_id": run.id,
            "status": run.status.value,
            "pass_rate": run.pass_rate,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        }
