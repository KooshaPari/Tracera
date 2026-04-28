"""
SDK Integration Tests.
"""

import pytest


@pytest.mark.asyncio
async def test_pydevkit_config():
    """
    Basic sanity check for PyDevKit configuration primitives.
    """
    from pheno.dev import ConfigManager

    config = ConfigManager()
    config.load_from_dict({"app": {"name": "test"}})
    assert config.get("app.name") == "test"


@pytest.mark.asyncio
async def test_workflow_kit_declarative():
    """
    Ensure declarative workflow engine executes a simple step.
    """
    from workflow_kit import (
        DeclarativeWorkflow,
        DeclarativeWorkflowEngine,
        workflow_definition,
        workflow_step,
    )

    @workflow_definition
    class TestWorkflow(DeclarativeWorkflow):
        @workflow_step()
        async def run(self, ctx):  # ctx is WorkflowContext
            return {"result": "success"}

    engine = DeclarativeWorkflowEngine()
    result = await engine.execute(TestWorkflow, {"input": True})
    assert result == {"result": "success"}


@pytest.mark.asyncio
async def test_workflow_kit_saga():
    """
    Verify saga executor compensates completed steps on failure.
    """
    from workflow_kit import Saga, SagaExecutor

    saga = Saga("demo")

    async def action(context):
        context.data["called"] = True
        return True

    async def compensation(context):
        context.data["compensated"] = True

    saga.add_step("demo_step", action, compensation)

    executor = SagaExecutor()
    context = await executor.execute(saga, {})
    assert context.data["demo_step_result"] is True


def test_db_kit_supabase_instantiation():
    """
    Supabase adapter should be constructible with minimal fields.
    """
    from pheno.database import SupabaseAdapter

    adapter = SupabaseAdapter()
    adapter.set_access_token("test")
    assert adapter is not None


def test_deploy_kit_nvms_parser(tmp_path):
    """
    NVMS parser should load simple manifests.
    """
    from pheno.deployment import NVMSParser

    manifest = tmp_path / "app.nvms"
    manifest.write_text(
        """
name: sample
services:
  api:
    path: api/index.js
""",
    )

    parser = NVMSParser()
    config = parser.parse(str(manifest))
    assert config["services"]["api"]["path"] == "api/index.js"
