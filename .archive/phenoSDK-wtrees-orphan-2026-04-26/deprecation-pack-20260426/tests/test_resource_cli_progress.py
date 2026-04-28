from __future__ import annotations

from contextlib import contextmanager

import pytest

from pheno.infra.cli.resource_cli import ResourceCLI


class DummyProgress:
    def __init__(self):
        self.updates: list[str] = []
        self.success_messages: list[str | None] = []
        self.failure_messages: list[str | None] = []

    def update(self, message: str) -> None:
        self.updates.append(message)

    def succeed(self, message: str | None = None) -> None:
        self.success_messages.append(message)

    def fail(self, message: str | None = None) -> None:
        self.failure_messages.append(message)


class DummyCoordinator:
    def __init__(self, *_, **__):
        self.policies: list[object] = []
        self.request_calls: list[tuple] = []
        self.release_calls: list[tuple] = []

    async def initialize(self) -> None:  # pragma: no cover - unused in tests
        return None

    async def shutdown(self) -> None:  # pragma: no cover - unused in tests
        return None

    def set_resource_policy(self, policy) -> None:
        self.policies.append(policy)

    async def request_resource(self, **kwargs):
        self.request_calls.append(kwargs)
        return True, {"is_reused": False, "dependencies": []}

    async def release_resource(self, resource_name: str, force: bool):
        self.release_calls.append((resource_name, force))
        return True


@pytest.fixture
def cli_with_progress(monkeypatch):
    progress_calls: list[str] = []

    @contextmanager
    def fake_progress(message: str, **_: object):
        progress_calls.append(message)
        yield DummyProgress()

    monkeypatch.setattr("pheno.infra.cli.resource_cli.progress_step", fake_progress)
    monkeypatch.setattr("pheno.infra.cli.resource_cli.ResourceCoordinator", DummyCoordinator)

    cli = ResourceCLI(project_name="demo-project")
    return cli, progress_calls


@pytest.mark.asyncio
async def test_set_policy_uses_progress(cli_with_progress):
    cli, progress_calls = cli_with_progress

    success = await cli.set_policy(
        resource_type="redis",
        lifecycle_rule="project_scoped",
        reuse_strategy="always",
        dependencies=[],
        compatibility_requirements=None,
    )

    assert success is True
    assert progress_calls == ["Applying policy for 'redis'"]
    assert cli.coordinator.policies, "Coordinator should receive policy object"


@pytest.mark.asyncio
async def test_request_resource_uses_progress(cli_with_progress):
    cli, progress_calls = cli_with_progress

    success = await cli.request_resource(
        resource_name="postgres",
        config={"size": "small"},
        mode=None,
        dependencies=["redis"],
        metadata={"env": "dev"},
    )

    assert success is True
    assert progress_calls == ["Requesting resource 'postgres'"]
    assert cli.coordinator.request_calls, "Request should be forwarded to coordinator"


@pytest.mark.asyncio
async def test_release_resource_uses_progress(cli_with_progress):
    cli, progress_calls = cli_with_progress

    success = await cli.release_resource(resource_name="postgres", force=False)

    assert success is True
    assert progress_calls == ["Releasing resource 'postgres'"]
    assert cli.coordinator.release_calls == [("postgres", False)]
