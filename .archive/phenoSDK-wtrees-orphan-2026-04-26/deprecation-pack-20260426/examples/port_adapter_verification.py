"""Port Adapter Verification Script.

This script verifies that the OrchestratorPortAdapter correctly implements
the AgentOrchestratorPort protocol and is compatible with the pheno.mcp.ports
interface.

Run:
    python examples/port_adapter_verification.py
"""

import asyncio
import logging
from typing import Any

from pheno.mcp.agents import OrchestratorPortAdapter
from pheno.mcp.ports import AgentConfig, AgentOrchestratorPort, ExecutionResult, TaskConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def verify_protocol_compliance(adapter: Any) -> bool:
    """Verify that adapter implements AgentOrchestratorPort.

    Args:
        adapter: Instance to verify

    Returns:
        True if compliant
    """
    logger.info("Verifying AgentOrchestratorPort protocol compliance...")

    # Check if instance of protocol
    if not isinstance(adapter, AgentOrchestratorPort):
        logger.error("❌ Adapter does not implement AgentOrchestratorPort protocol")
        return False

    logger.info("✅ Adapter implements AgentOrchestratorPort protocol")

    # Check required methods
    required_methods = [
        "create_agent",
        "execute_task",
        "execute_workflow",
        "get_agent_status",
    ]

    for method_name in required_methods:
        if not hasattr(adapter, method_name):
            logger.error(f"❌ Missing required method: {method_name}")
            return False

        method = getattr(adapter, method_name)
        if not callable(method):
            logger.error(f"❌ {method_name} is not callable")
            return False

        logger.info(f"✅ Method '{method_name}' exists and is callable")

    return True


async def test_create_agent(adapter: AgentOrchestratorPort) -> str | None:
    """Test agent creation.

    Args:
        adapter: Port adapter instance

    Returns:
        Agent ID if successful, None otherwise
    """
    logger.info("\n=== Testing create_agent ===")

    try:
        config = AgentConfig(
            name="test_agent",
            role="Test Agent",
            goal="Verify port compliance",
            backstory="Created for testing purposes",
        )

        agent_id = await adapter.create_agent(config)

        logger.info(f"✅ Agent created successfully: {agent_id}")
        logger.info(f"   Type: {type(agent_id)}")
        logger.info(f"   Value: {agent_id}")

        return agent_id

    except Exception as e:
        logger.error(f"❌ Agent creation failed: {e}", exc_info=True)
        return None


async def test_execute_task(adapter: AgentOrchestratorPort) -> ExecutionResult | None:
    """Test task execution.

    Args:
        adapter: Port adapter instance

    Returns:
        ExecutionResult if successful, None otherwise
    """
    logger.info("\n=== Testing execute_task ===")

    try:
        task = TaskConfig(
            description="Test task for port verification",
            agent="test_agent",
            expected_output="Test result",
        )

        result = await adapter.execute_task(task)

        logger.info(f"✅ Task executed successfully")
        logger.info(f"   Type: {type(result)}")
        logger.info(f"   Success: {result.success}")
        logger.info(f"   Task ID: {result.task_id}")
        logger.info(f"   Output: {result.output}")
        logger.info(f"   Error: {result.error}")

        # Verify result is ExecutionResult
        if not isinstance(result, ExecutionResult):
            logger.error(f"❌ Result is not ExecutionResult: {type(result)}")
            return None

        return result

    except Exception as e:
        logger.error(f"❌ Task execution failed: {e}", exc_info=True)
        return None


async def test_execute_workflow(adapter: AgentOrchestratorPort) -> list[ExecutionResult] | None:
    """Test workflow execution.

    Args:
        adapter: Port adapter instance

    Returns:
        List of ExecutionResults if successful, None otherwise
    """
    logger.info("\n=== Testing execute_workflow ===")

    try:
        tasks = [
            TaskConfig(
                description="First task in workflow",
                agent="test_agent",
                expected_output="First result",
            ),
            TaskConfig(
                description="Second task in workflow",
                agent="test_agent",
                expected_output="Second result",
            ),
        ]

        results = await adapter.execute_workflow(tasks)

        logger.info(f"✅ Workflow executed successfully")
        logger.info(f"   Type: {type(results)}")
        logger.info(f"   Count: {len(results)}")

        # Verify results
        if not isinstance(results, list):
            logger.error(f"❌ Results is not a list: {type(results)}")
            return None

        for i, result in enumerate(results):
            if not isinstance(result, ExecutionResult):
                logger.error(f"❌ Result {i} is not ExecutionResult: {type(result)}")
                return None

            logger.info(f"   Task {i}:")
            logger.info(f"     Success: {result.success}")
            logger.info(f"     Task ID: {result.task_id}")

        return results

    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {e}", exc_info=True)
        return None


async def test_get_agent_status(
    adapter: AgentOrchestratorPort, agent_id: str
) -> dict[str, Any] | None:
    """Test getting agent status.

    Args:
        adapter: Port adapter instance
        agent_id: Agent identifier

    Returns:
        Status dictionary if successful, None otherwise
    """
    logger.info("\n=== Testing get_agent_status ===")

    try:
        status = await adapter.get_agent_status(agent_id)

        logger.info(f"✅ Agent status retrieved successfully")
        logger.info(f"   Type: {type(status)}")

        # Verify status is dict
        if not isinstance(status, dict):
            logger.error(f"❌ Status is not a dict: {type(status)}")
            return None

        # Log status details
        for key, value in status.items():
            logger.info(f"   {key}: {value}")

        return status

    except Exception as e:
        logger.error(f"❌ Get agent status failed: {e}", exc_info=True)
        return None


async def main():
    """
    Run all verification tests.
    """
    logger.info("=" * 60)
    logger.info("PORT ADAPTER VERIFICATION")
    logger.info("=" * 60)

    # Create adapter - using custom framework for testing
    # (CrewAI would require actual API keys)
    adapter = OrchestratorPortAdapter(framework="custom")

    # Verify protocol compliance
    if not verify_protocol_compliance(adapter):
        logger.error("\n❌ VERIFICATION FAILED: Protocol compliance check failed")
        return False

    # Test create_agent
    agent_id = await test_create_agent(adapter)
    if not agent_id:
        logger.error("\n❌ VERIFICATION FAILED: Agent creation failed")
        return False

    # Test execute_task
    task_result = await test_execute_task(adapter)
    if not task_result:
        logger.error("\n❌ VERIFICATION FAILED: Task execution failed")
        return False

    # Test execute_workflow
    workflow_results = await test_execute_workflow(adapter)
    if not workflow_results:
        logger.error("\n❌ VERIFICATION FAILED: Workflow execution failed")
        return False

    # Test get_agent_status
    status = await test_get_agent_status(adapter, agent_id)
    if not status:
        logger.error("\n❌ VERIFICATION FAILED: Get agent status failed")
        return False

    # Cleanup
    await adapter.shutdown()

    logger.info("\n" + "=" * 60)
    logger.info("✅ ALL VERIFICATION TESTS PASSED")
    logger.info("=" * 60)
    logger.info("\nThe OrchestratorPortAdapter correctly implements:")
    logger.info("  ✓ AgentOrchestratorPort protocol")
    logger.info("  ✓ create_agent method")
    logger.info("  ✓ execute_task method")
    logger.info("  ✓ execute_workflow method")
    logger.info("  ✓ get_agent_status method")
    logger.info("\nPort compliance: VERIFIED ✅")

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
