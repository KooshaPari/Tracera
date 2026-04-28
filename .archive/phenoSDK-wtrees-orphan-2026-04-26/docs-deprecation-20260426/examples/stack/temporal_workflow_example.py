"""Temporal (durable) workflow example using workflow-kit exports.

This example demonstrates both local and durable execution modes,
illustrating the migration path from local to Temporal workflows.

Updated (Task 2.4): Enhanced with comprehensive Temporal example including:
- Activity definitions with retry policies
- Human approval gates
- Error handling and compensation
- Local vs durable comparison

See: workflow-kit/docs/LOCAL_VS_DURABLE.md

Note: Requires Temporal SDK/server for durable mode. Install with:
    pip install temporalio
"""

from __future__ import annotations

import asyncio
from datetime import timedelta

from workflow_kit import (
    DeclarativeWorkflow,
    DeclarativeWorkflowEngine,
    workflow_definition,
    workflow_step,
)

# Temporal imports (optional)
try:
    from temporalio import workflow
    from workflow_kit.orchestrators.temporal import (
        BaseWorkflow,
        TemporalWorkflowClient,
        workflow_activity,
    )

    TEMPORAL_AVAILABLE = True
except ImportError:
    TEMPORAL_AVAILABLE = False
    print("⚠ Temporal SDK not installed. Durable mode unavailable.")
    print("  Install with: pip install temporalio")


# ============================================================================
# Local Workflow Example (Fast, In-Memory, Development)
# ============================================================================


@workflow_definition
class DataProcessingWorkflow(DeclarativeWorkflow):
    """Local workflow for data processing pipeline.

    Characteristics:
    - Runs in-process, no external dependencies
    - Fast iteration for development
    - State lost on restart
    - Best for: dev/test, short-lived tasks (<5min)
    """

    @workflow_step()
    async def extract_data(self, ctx):
        """
        Simulate data extraction.
        """
        print("  → Step 1: Extracting data...")
        await asyncio.sleep(1)  # Simulate work
        return {"records": 100, "source": "database"}

    @workflow_step()
    async def transform_data(self, ctx):
        """
        Simulate data transformation.
        """
        print("  → Step 2: Transforming data...")
        extract_result = ctx.get_result("extract_data")
        await asyncio.sleep(1)
        return {"transformed_records": extract_result["records"], "format": "json"}

    @workflow_step()
    async def load_data(self, ctx):
        """
        Simulate data loading.
        """
        print("  → Step 3: Loading data...")
        transform_result = ctx.get_result("transform_data")
        await asyncio.sleep(1)
        return {
            "status": "completed",
            "records_loaded": transform_result["transformed_records"],
            "destination": "data_warehouse",
        }


async def run_local():
    """
    Run workflow locally (in-process, fast iteration).
    """
    print("\n" + "=" * 60)
    print("LOCAL WORKFLOW EXECUTION (In-Process)")
    print("=" * 60)

    engine = DeclarativeWorkflowEngine()
    result = await engine.execute(DataProcessingWorkflow, {"source": "database"})

    print(f"\n✓ Local workflow completed: {result}")
    return result


# ============================================================================
# Durable Workflow Example (Temporal, Fault-Tolerant, Production)
# ============================================================================

if TEMPORAL_AVAILABLE:

    @workflow.defn
    class OrderFulfillmentWorkflow(BaseWorkflow):
        """Durable workflow for order processing with approval gates.

        Characteristics:
        - Survives restarts and failures
        - State persisted in Temporal server
        - Supports human approval gates
        - Best for: long-running (>5min), critical business processes
        """

        async def orchestrate(self, workflow_args: dict) -> dict:
            """
            Main workflow orchestration with approval gate.
            """
            order_id = workflow_args.get("order_id", "ORD_123")
            amount = workflow_args.get("amount", 15000)

            print(f"\n  → Workflow started for order {order_id} (${amount})")

            # Step 1: Validate order (with retry policy)
            validation_result = await workflow.execute_activity(
                validate_order,
                args=[order_id, amount],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=workflow.common.RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_attempts=3,
                    backoff_coefficient=2.0,
                ),
            )

            if not validation_result["valid"]:
                print(f"  ✗ Order validation failed: {validation_result['reason']}")
                return {
                    "status": "rejected",
                    "reason": validation_result["reason"],
                }

            print("  ✓ Order validated")

            # Step 2: Request approval for high-value orders
            if amount > 10000:
                print(f"  ⏸ Requesting approval (high-value order: ${amount})")

                try:
                    approved = await self.wait_for_approval(
                        stage="high_value_review",
                        description=f"Order {order_id} requires approval (${amount})",
                        context={"order_id": order_id, "amount": amount},
                        timeout_seconds=24 * 60 * 60,  # 24 hours
                    )

                    if not approved:
                        print("  ✗ Order approval denied")
                        return {"status": "rejected", "reason": "approval_denied"}

                    print("  ✓ Order approved")
                except Exception as e:
                    print(f"  ✗ Approval process failed: {e}")
                    return {"status": "error", "reason": str(e)}

            # Step 3: Process payment
            payment_result = await workflow.execute_activity(
                process_payment,
                args=[order_id, amount],
                start_to_close_timeout=timedelta(minutes=10),
            )

            print(f"  ✓ Payment processed: {payment_result['transaction_id']}")

            # Step 4: Ship order (long-running activity)
            shipping_result = await workflow.execute_activity(
                ship_order,
                args=[order_id],
                start_to_close_timeout=timedelta(hours=48),
            )

            print(f"  ✓ Order shipped: {shipping_result['tracking_number']}")

            return {
                "status": "completed",
                "order_id": order_id,
                "transaction_id": payment_result["transaction_id"],
                "tracking_number": shipping_result["tracking_number"],
            }

    # Activities (stateless, idempotent functions)
    @workflow_activity
    async def validate_order(order_id: str, amount: float) -> dict:
        """
        Validate order details.
        """
        print(f"    [Activity] Validating order {order_id}...")
        await asyncio.sleep(1)  # Simulate validation
        return {"valid": True, "amount": amount}

    @workflow_activity
    async def process_payment(order_id: str, amount: float) -> dict:
        """
        Process payment for order.
        """
        print(f"    [Activity] Processing payment of ${amount}...")
        await asyncio.sleep(2)  # Simulate payment processing
        return {"transaction_id": f"TXN_{order_id}", "amount_charged": amount}

    @workflow_activity
    async def ship_order(order_id: str) -> dict:
        """
        Ship order to customer.
        """
        print(f"    [Activity] Shipping order {order_id}...")
        await asyncio.sleep(1)  # Simulate shipping
        return {"tracking_number": f"TRACK_{order_id}", "carrier": "FedEx"}


async def run_temporal(
    namespace: str = "default", order_id: str = "ORD_789", amount: float = 15000,
):
    """Run workflow durably with Temporal.

    Requires:
    - Temporal server running (docker-compose up -d temporal)
    - Worker process registered with workflows and activities
    """
    if not TEMPORAL_AVAILABLE:
        print("\n✗ Temporal SDK not installed. Cannot run durable workflow.")
        print("  Install with: pip install temporalio")
        return {"error": "temporal_unavailable"}

    print("\n" + "=" * 60)
    print("DURABLE WORKFLOW EXECUTION (Temporal)")
    print("=" * 60)
    print(f"Order ID: {order_id}, Amount: ${amount}")

    try:
        client = TemporalWorkflowClient(
            temporal_address="localhost:7233",
            namespace=namespace,
            task_queue="order-workflows",
        )

        connected = await client.connect()
        if not connected:
            print("\n✗ Failed to connect to Temporal server at localhost:7233")
            print("  Start Temporal with: docker-compose up -d temporal")
            print("  Or use Temporal Cloud")
            return {"error": "connection_failed"}

        print("✓ Connected to Temporal server")

        result = await client.start_workflow(
            OrderFulfillmentWorkflow,
            workflow_args={"order_id": order_id, "amount": amount},
            workflow_id=f"order-{order_id}",
            timeout_seconds=72 * 60 * 60,  # 72 hours
        )

        print("\n✓ Durable workflow completed")
        print(f"  Workflow ID: {result.workflow_id}")
        print(f"  Status: {result.status}")
        print(f"  Result: {result.result}")

        await client.disconnect()
        return result

    except Exception as e:
        print(f"\n✗ Workflow execution failed: {e}")
        return {"error": str(e)}


# ============================================================================
# Demo Runner
# ============================================================================


async def main():
    """
    Run both local and durable workflows for comparison.
    """
    print("\n" + "🔧" * 30)
    print("Workflow-Kit: Local vs Durable Execution Demo")
    print("Task 2.4 - Temporal Integration Example")
    print("🔧" * 30)

    # Run local workflow (always available)
    local_result = await run_local()

    # Run durable workflow (if Temporal available)
    if TEMPORAL_AVAILABLE:
        print("\n" + "─" * 60)
        temporal_result = await run_temporal()
    else:
        print("\n" + "─" * 60)
        print("\nSkipping durable workflow (Temporal SDK not installed)")
        print("\nTo enable durable workflows:")
        print("  1. Install Temporal SDK: pip install temporalio")
        print("  2. Start Temporal server: docker-compose up -d temporal")
        print("  3. Re-run this example")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\nLocal Workflow:")
    print("  ✓ Fast iteration, no infrastructure")
    print("  ✓ Good for: dev/test, short tasks (<5min)")
    print("  ✗ No fault tolerance or durability")

    if TEMPORAL_AVAILABLE:
        print("\nDurable Workflow (Temporal):")
        print("  ✓ Fault-tolerant, survives restarts")
        print("  ✓ Good for: long-running, critical processes")
        print("  ✓ Supports approval gates and saga patterns")
        print("  ✗ Requires infrastructure (Temporal server)")

    print("\nSee: workflow-kit/docs/LOCAL_VS_DURABLE.md for decision guide")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
