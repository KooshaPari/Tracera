"""
Example workflows demonstrating pheno-SDK workflow orchestration capabilities.

This file showcases various workflow patterns including:
- Sequential execution
- Parallel execution
- Conditional branching
- Error handling and retries
- Complex DAG workflows
- Event-driven workflows
"""

import asyncio
import random
import sys
from datetime import datetime
from pathlib import Path

# Add src to path to use local version
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pheno.workflow.orchestrator import (
    WorkflowDefinition,
    WorkflowOrchestrator,
    WorkflowStep,
    build_parallel_workflow,
    build_simple_workflow,
)


# Example 1: Data Processing Pipeline
# Sequential workflow for processing data
def example_data_pipeline():
    """
    Demonstrates a simple sequential data processing pipeline.
    """
    print("\n=== Example 1: Data Processing Pipeline ===\n")

    def fetch_data(context: dict) -> dict:
        """Simulate fetching data from a source."""
        print("📥 Fetching data from source...")
        return {"records": [{"id": i, "value": random.randint(1, 100)} for i in range(10)]}

    def validate_data(context: dict) -> dict:
        """Validate the fetched data."""
        print("✅ Validating data...")
        records = context.get("step_fetch_data_output", {}).get("records", [])
        valid_records = [r for r in records if r["value"] > 0]
        return {"valid_records": valid_records, "count": len(valid_records)}

    def transform_data(context: dict) -> dict:
        """Transform the validated data."""
        print("🔄 Transforming data...")
        records = context.get("step_validate_data_output", {}).get("valid_records", [])
        transformed = [{"id": r["id"], "value": r["value"] * 2} for r in records]
        return {"transformed": transformed}

    def save_data(context: dict) -> str:
        """Save the transformed data."""
        print("💾 Saving data...")
        records = context.get("step_transform_data_output", {}).get("transformed", [])
        return f"Saved {len(records)} records"

    # Build the workflow
    workflow = build_simple_workflow(
        "data_pipeline",
        [
            ("fetch_data", fetch_data),
            ("validate_data", validate_data),
            ("transform_data", transform_data),
            ("save_data", save_data),
        ],
    )

    return workflow


# Example 2: Parallel Processing
# Process multiple tasks concurrently
def example_parallel_processing():
    """
    Demonstrates parallel processing of independent tasks.
    """
    print("\n=== Example 2: Parallel Processing ===\n")

    async def process_batch_a(context: dict) -> dict:
        """Process batch A."""
        print("🔵 Processing batch A...")
        await asyncio.sleep(0.1)
        return {"batch": "A", "processed": 100}

    async def process_batch_b(context: dict) -> dict:
        """Process batch B."""
        print("🟢 Processing batch B...")
        await asyncio.sleep(0.1)
        return {"batch": "B", "processed": 150}

    async def process_batch_c(context: dict) -> dict:
        """Process batch C."""
        print("🟡 Processing batch C...")
        await asyncio.sleep(0.1)
        return {"batch": "C", "processed": 200}

    workflow = build_parallel_workflow(
        "parallel_processing",
        [
            ("batch_a", process_batch_a),
            ("batch_b", process_batch_b),
            ("batch_c", process_batch_c),
        ],
    )

    return workflow


# Example 3: Conditional Workflow
# Execute steps based on conditions
def example_conditional_workflow():
    """
    Demonstrates conditional step execution based on runtime data.
    """
    print("\n=== Example 3: Conditional Workflow ===\n")

    def check_inventory(context: dict) -> dict:
        """Check current inventory levels."""
        print("📦 Checking inventory...")
        stock_level = random.randint(0, 100)
        print(f"   Current stock level: {stock_level}")
        return {"stock_level": stock_level, "threshold": 50}

    def should_reorder(context: dict) -> bool:
        """Determine if reorder is needed."""
        stock_level = context.get("step_check_inventory_output", {}).get("stock_level", 100)
        threshold = context.get("step_check_inventory_output", {}).get("threshold", 50)
        return stock_level < threshold

    def reorder_stock(context: dict) -> str:
        """Reorder stock."""
        print("🛒 Reordering stock...")
        stock_level = context.get("step_check_inventory_output", {}).get("stock_level", 0)
        quantity = 100 - stock_level
        return f"Ordered {quantity} units"

    def send_low_stock_alert(context: dict) -> str:
        """Send alert about low stock."""
        print("🚨 Sending low stock alert...")
        return "Alert sent"

    workflow = WorkflowDefinition(workflow_id="conditional_inventory", name="Inventory Management")

    workflow.add_step(WorkflowStep(step_id="check_inventory", handler=check_inventory))

    workflow.add_step(
        WorkflowStep(
            step_id="reorder_stock",
            handler=reorder_stock,
            condition=should_reorder,
            dependencies=["check_inventory"],
        ),
    )

    workflow.add_step(
        WorkflowStep(
            step_id="send_alert",
            handler=send_low_stock_alert,
            condition=should_reorder,
            dependencies=["check_inventory"],
        ),
    )

    return workflow


# Example 4: Error Handling and Retry
# Handle failures gracefully with retries
def example_error_handling():
    """
    Demonstrates error handling and retry mechanisms.
    """
    print("\n=== Example 4: Error Handling and Retry ===\n")

    attempt_count = {"api_call": 0}

    async def unreliable_api_call(context: dict) -> dict:
        """Simulate an unreliable API call."""
        attempt_count["api_call"] += 1
        print(f"🌐 API call attempt {attempt_count['api_call']}...")

        # Fail the first 2 attempts
        if attempt_count["api_call"] < 3:
            raise ConnectionError("API temporarily unavailable")

        print("   ✅ API call succeeded!")
        return {"data": "API response", "timestamp": datetime.utcnow().isoformat()}

    def process_response(context: dict) -> str:
        """Process the API response."""
        print("⚙️  Processing API response...")
        data = context.get("step_api_call_output", {})
        return f"Processed: {data}"

    workflow = WorkflowDefinition(workflow_id="error_handling", name="Error Handling Example")

    workflow.add_step(
        WorkflowStep(
            step_id="api_call",
            handler=unreliable_api_call,
            retry_policy={"max_retries": 3, "backoff_factor": 2},
        ),
    )

    workflow.add_step(
        WorkflowStep(step_id="process", handler=process_response, dependencies=["api_call"]),
    )

    return workflow


# Example 5: Complex DAG Workflow
# Demonstrate complex dependency graph
def example_complex_dag():
    """
    Demonstrates a complex workflow with multiple dependencies and branches.
    """
    print("\n=== Example 5: Complex DAG Workflow ===\n")

    async def init_workflow(context: dict) -> dict:
        """Initialize the workflow."""
        print("🚀 Initializing workflow...")
        return {"start_time": datetime.utcnow().isoformat(), "workflow_id": "dag_001"}

    async def fetch_user_data(context: dict) -> dict:
        """Fetch user data."""
        print("👤 Fetching user data...")
        await asyncio.sleep(0.05)
        return {"user_id": 123, "name": "John Doe"}

    async def fetch_order_data(context: dict) -> dict:
        """Fetch order data."""
        print("🛍️  Fetching order data...")
        await asyncio.sleep(0.05)
        return {"order_id": 456, "items": ["item1", "item2"]}

    async def compute_recommendations(context: dict) -> dict:
        """Compute recommendations based on user and order data."""
        print("🎯 Computing recommendations...")
        await asyncio.sleep(0.05)
        return {"recommendations": ["rec1", "rec2", "rec3"]}

    async def send_email(context: dict) -> str:
        """Send email to user."""
        print("📧 Sending email...")
        await asyncio.sleep(0.05)
        return "Email sent"

    async def update_database(context: dict) -> str:
        """Update database with results."""
        print("💾 Updating database...")
        await asyncio.sleep(0.05)
        return "Database updated"

    workflow = WorkflowDefinition(workflow_id="complex_dag", name="Complex DAG Workflow")

    # Layer 1: Initialization
    workflow.add_step(WorkflowStep(step_id="init", handler=init_workflow))

    # Layer 2: Parallel data fetching (depends on init)
    workflow.add_step(
        WorkflowStep(step_id="fetch_user", handler=fetch_user_data, dependencies=["init"]),
    )
    workflow.add_step(
        WorkflowStep(step_id="fetch_orders", handler=fetch_order_data, dependencies=["init"]),
    )

    # Layer 3: Compute (depends on both data fetches)
    workflow.add_step(
        WorkflowStep(
            step_id="compute_recs",
            handler=compute_recommendations,
            dependencies=["fetch_user", "fetch_orders"],
        ),
    )

    # Layer 4: Parallel final actions (depends on compute)
    workflow.add_step(
        WorkflowStep(step_id="send_email", handler=send_email, dependencies=["compute_recs"]),
    )
    workflow.add_step(
        WorkflowStep(step_id="update_db", handler=update_database, dependencies=["compute_recs"]),
    )

    return workflow


# Main execution
async def run_examples():
    """Run all workflow examples."""
    orchestrator = WorkflowOrchestrator()

    # Track events
    event_log = []

    def log_event(execution):
        event = f"{execution.workflow_id}: {execution.status.value}"
        event_log.append(event)
        print(f"\n📊 Event: {event}")

    orchestrator.on_event("workflow.started", log_event)
    orchestrator.on_event("workflow.completed", log_event)
    orchestrator.on_event("workflow.failed", log_event)

    # Example 1: Data Pipeline
    workflow1 = example_data_pipeline()
    orchestrator.register_workflow(workflow1)
    execution1 = await orchestrator.execute_workflow(workflow1.workflow_id)
    print(f"✅ Data Pipeline completed in {(execution1.completed_at - execution1.started_at).total_seconds():.2f}s")

    # Example 2: Parallel Processing
    workflow2 = example_parallel_processing()
    orchestrator.register_workflow(workflow2)
    start_time = datetime.utcnow()
    execution2 = await orchestrator.execute_workflow(workflow2.workflow_id)
    duration = (datetime.utcnow() - start_time).total_seconds()
    print(
        f"✅ Parallel Processing completed in {duration:.2f}s (would be ~0.3s if sequential)",
    )

    # Example 3: Conditional Workflow
    workflow3 = example_conditional_workflow()
    orchestrator.register_workflow(workflow3)
    execution3 = await orchestrator.execute_workflow(workflow3.workflow_id)
    print("✅ Conditional Workflow completed")

    # Example 4: Error Handling
    workflow4 = example_error_handling()
    orchestrator.register_workflow(workflow4)
    execution4 = await orchestrator.execute_workflow(workflow4.workflow_id)
    print("✅ Error Handling workflow completed (with retries)")

    # Example 5: Complex DAG
    workflow5 = example_complex_dag()
    orchestrator.register_workflow(workflow5)
    execution5 = await orchestrator.execute_workflow(workflow5.workflow_id)
    print(f"✅ Complex DAG completed with {len(execution5.step_results)} steps")

    # Show execution summary
    print("\n" + "=" * 60)
    print("EXECUTION SUMMARY")
    print("=" * 60)

    for execution in [execution1, execution2, execution3, execution4, execution5]:
        successful = sum(
            1 for r in execution.step_results.values() if r.status.value == "completed"
        )
        failed = sum(1 for r in execution.step_results.values() if r.status.value == "failed")
        skipped = sum(
            1 for r in execution.step_results.values() if r.status.value == "skipped"
        )

        print(f"\n{execution.workflow_id}:")
        print(f"  Status: {execution.status.value}")
        print(f"  Steps: {len(execution.step_results)} total")
        print(f"    - Completed: {successful}")
        print(f"    - Failed: {failed}")
        print(f"    - Skipped: {skipped}")
        print(f"  Events: {len(execution.events)}")

    print("\n✨ All examples completed successfully!")


if __name__ == "__main__":
    print("=" * 60)
    print("PHENO-SDK WORKFLOW ORCHESTRATION EXAMPLES")
    print("=" * 60)

    asyncio.run(run_examples())
