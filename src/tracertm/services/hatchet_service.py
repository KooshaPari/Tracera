"""Hatchet workflow orchestration service."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx

try:  # Optional SDK for cron management
    from hatchet_sdk import Hatchet  # type: ignore
except Exception:  # pragma: no cover
    Hatchet = None  # type: ignore[assignment]


@dataclass(frozen=True)
class HatchetSettings:
    token: str
    base_url: str
    timeout_seconds: float


class HatchetService:
    def __init__(self, settings: HatchetSettings | None = None):
        self.settings = settings or self._load_settings()

    @staticmethod
    def _load_settings() -> HatchetSettings | None:
        token = os.getenv("HATCHET_CLIENT_TOKEN") or os.getenv("HATCHET_API_KEY")
        if not token:
            return None
        base_url = os.getenv("HATCHET_API_URL", "https://cloud.onhatchet.run").rstrip("/")
        timeout_seconds = float(os.getenv("HATCHET_API_TIMEOUT", "20"))
        return HatchetSettings(token=token, base_url=base_url, timeout_seconds=timeout_seconds)

    def enabled(self) -> bool:
        return self.settings is not None

    async def health_check(self) -> dict[str, Any]:
        if not self.settings:
            return {"enabled": False, "status": "missing_token"}
        return {"enabled": True, "status": "ready"}

    async def trigger_workflow(self, workflow_name: str, input_data: dict[str, Any]) -> dict[str, Any]:
        if not self.settings:
            raise ValueError("Hatchet token not configured")
        payload = {"workflow_name": workflow_name, "input": input_data}
        url = f"{self.settings.base_url}/api/workflows/trigger"
        headers = {
            "Authorization": f"Bearer {self.settings.token}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=self.settings.timeout_seconds) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    def _get_sdk(self):
        if Hatchet is None:
            raise RuntimeError("hatchet-sdk is not available")
        return Hatchet()

    async def create_cron(
        self,
        workflow_name: str,
        cron_name: str,
        expression: str,
        input_data: dict[str, Any],
        additional_metadata: dict[str, Any] | None = None,
        priority: int | None = None,
    ) -> dict[str, Any]:
        """Create a cron schedule via Hatchet SDK."""
        if not self.settings:
            raise ValueError("Hatchet token not configured")
        sdk = self._get_sdk()
        cron = sdk.cron.create(
            workflow_name=workflow_name,
            cron_name=cron_name,
            expression=expression,
            input=input_data,
            additional_metadata=additional_metadata or {},
            priority=priority,
        )
        return cron.dict() if hasattr(cron, "dict") else cron.__dict__

    async def list_crons(
        self,
        workflow_name: str | None = None,
        cron_name: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        additional_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.settings:
            raise ValueError("Hatchet token not configured")
        sdk = self._get_sdk()
        result = sdk.cron.list(
            workflow_name=workflow_name,
            cron_name=cron_name,
            limit=limit,
            offset=offset,
            additional_metadata=additional_metadata,
        )
        return result.dict() if hasattr(result, "dict") else result.__dict__

    async def delete_cron(self, cron_id: str) -> dict[str, Any]:
        if not self.settings:
            raise ValueError("Hatchet token not configured")
        sdk = self._get_sdk()
        result = sdk.cron.delete(cron_id=cron_id)
        return {"deleted": True, "cron_id": cron_id, "result": getattr(result, "dict", lambda: {})()}
