#!/usr/bin/env python3
"""Async Orchestration Example.

This example demonstrates how to use the pheno.async.orchestration module for task
management, workflows, and progress tracking.
"""

import asyncio
import time
from pathlib import Path

from pheno.async.execution import AsyncTaskExecutor
from pheno.async.monitoring import TaskMonitor
from pheno.async.orchestration import (
    OrchestrationConfig,
    TaskConfig,
    TaskOrchestrator,
    TaskPriority,
    TaskStatus,
)
from pheno.async.storage import InMemoryTaskStorage


async def sample_task(name: str, duration: float = 1.0) -> str:
    """
    Sample task for demonstration.
    """
    print(f"🔄 Starting task: {name}")
    await asyncio.sleep(duration)
    print(f"✅ Completed task: {name}")
    return f"Result from {name}"


async def failing_task(name: str) -> str:
    """
    Sample failing task for demonstration.
    """
    print(f"🔄 Starting failing task: {name}")
    await asyncio.sleep(0.5)
    raise Exception(f"Task {name} failed intentionally")


async def main():
    """
    Main example function.
    """
    print("⚡ Async Orchestration Example")
    print("=" * 50)

    # Setup orchestrator
    config = OrchestrationConfig(
        max_concurrent_tasks=3,
        task_timeout=30.0,
        enable_metrics=True,
        enable_progress_tracking=True
    )

    storage = InMemoryTaskStorage()
    executor = AsyncTaskExecutor()
    orchestrator = TaskOrchestrator(config, storage, executor)

    # Start orchestrator
    await orchestrator.start()
    print("🚀 Orchestrator started")

    try:
        # Submit individual tasks
        print(f"\n📝 Submitting individual tasks...")

        task1_id = await orchestrator.submit_task(
            sample_task, "Task 1", 2.0,
            task_config=TaskConfig(
                name="Sample Task 1",
                priority=TaskPriority.HIGH,
                max_retries=2
            )
        )

        task2_id = await orchestrator.submit_task(
            sample_task, "Task 2", 1.5,
            task_config=TaskConfig(
                name="Sample Task 2",
                priority=TaskPriority.NORMAL
            )
        )

        task3_id = await orchestrator.submit_task(
            failing_task, "Failing Task",
            task_config=TaskConfig(
                name="Failing Task",
                priority=TaskPriority.LOW,
                max_retries=1
            )
        )

        print(f"  • Task 1 ID: {task1_id}")
        print(f"  • Task 2 ID: {task2_id}")
        print(f"  • Task 3 ID: {task3_id}")

        # Wait for tasks
        print(f"\n⏳ Waiting for tasks...")

        try:
            result1 = await orchestrator.wait_for_task(task1_id)
            print(f"  ✅ Task 1 result: {result1.result}")
        except Exception as e:
            print(f"  ❌ Task 1 failed: {e}")

        try:
            result2 = await orchestrator.wait_for_task(task2_id)
            print(f"  ✅ Task 2 result: {result2.result}")
        except Exception as e:
            print(f"  ❌ Task 2 failed: {e}")

        try:
            result3 = await orchestrator.wait_for_task(task3_id)
            print(f"  ✅ Task 3 result: {result3.result}")
        except Exception as e:
            print(f"  ❌ Task 3 failed: {e}")

        # Create workflow
        print(f"\n🔄 Creating workflow...")

        workflow_tasks = [
            (sample_task, ("Workflow Task 1", 1.0), {}),
            (sample_task, ("Workflow Task 2", 1.5), {}),
            (sample_task, ("Workflow Task 3", 1.0), {}),
        ]

        workflow_id = await orchestrator.create_workflow("Sample Workflow", workflow_tasks)
        print(f"  • Workflow ID: {workflow_id}")

        # Wait for workflow
        print(f"⏳ Waiting for workflow...")
        workflow_results = await orchestrator.wait_for_workflow(workflow_id)

        print(f"  • Workflow completed with {len(workflow_results)} results")
        for i, result in enumerate(workflow_results, 1):
            if result.is_successful():
                print(f"    ✅ Workflow Task {i}: {result.result}")
            else:
                print(f"    ❌ Workflow Task {i}: {result.error}")

        # List all tasks
        print(f"\n📋 All tasks:")
        all_tasks = await orchestrator.list_tasks()
        for task in all_tasks:
            status_emoji = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.RUNNING: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.FAILED: "❌",
                TaskStatus.CANCELLED: "🚫"
            }.get(task.status, "❓")

            print(f"  {status_emoji} {task.config.name}: {task.status.value}")

        # Get metrics
        print(f"\n📊 Orchestrator Metrics:")
        # Note: In a real implementation, you'd get metrics from the orchestrator
        print(f"  • Total tasks: {len(all_tasks)}")
        print(f"  • Completed: {sum(1 for t in all_tasks if t.status == TaskStatus.COMPLETED)}")
        print(f"  • Failed: {sum(1 for t in all_tasks if t.status == TaskStatus.FAILED)}")

    finally:
        # Stop orchestrator
        await orchestrator.stop()
        print(f"\n🛑 Orchestrator stopped")


if __name__ == "__main__":
    asyncio.run(main())
