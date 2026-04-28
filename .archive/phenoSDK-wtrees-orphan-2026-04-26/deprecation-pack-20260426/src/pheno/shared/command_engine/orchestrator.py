"""Process Orchestrator.

Provides advanced orchestration capabilities for complex command sequences, including
dependency management, parallel execution, and workflow coordination.
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .context import ProjectContext
from .core import CommandEngine, CommandResult, CommandStage

logger = logging.getLogger(__name__)


class OrchestrationStatus(Enum):
    """
    Status of orchestration execution.
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OrchestrationStep:
    """
    A step in an orchestration workflow.
    """

    name: str
    description: str
    command: str | list[str]
    dependencies: list[str] = field(default_factory=list)
    condition: Callable[[], bool] | None = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int | None = None
    parallel: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationResult:
    """
    Result of orchestration execution.
    """

    success: bool
    status: OrchestrationStatus
    steps: list[CommandResult]
    duration: float
    start_time: datetime
    end_time: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def failed_steps(self) -> list[CommandResult]:
        """
        Get steps that failed.
        """
        return [step for step in self.steps if not step.success]

    @property
    def successful_steps(self) -> list[CommandResult]:
        """
        Get steps that succeeded.
        """
        return [step for step in self.steps if step.success]


class ProcessOrchestrator:
    """Advanced process orchestrator for complex workflows.

    Provides dependency management, parallel execution, retry logic, and workflow
    coordination for complex command sequences.
    """

    def __init__(self, command_engine: CommandEngine | None = None):
        self.command_engine = command_engine or CommandEngine()
        self._running_workflows: dict[str, asyncio.Task] = {}

    async def execute_workflow(
        self,
        steps: list[OrchestrationStep],
        *,
        context: ProjectContext | None = None,
        max_parallel: int = 3,
        progress_callback: Callable[[CommandStage], None] | None = None,
        workflow_id: str | None = None,
    ) -> OrchestrationResult:
        """Execute a workflow with dependency management and parallel execution.

        Args:
            steps: List of orchestration steps
            context: Project context for command execution
            max_parallel: Maximum parallel steps
            progress_callback: Callback for progress updates
            workflow_id: Optional workflow identifier

        Returns:
            OrchestrationResult with execution details
        """
        workflow_id = workflow_id or f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()

        logger.info(f"Starting workflow {workflow_id} with {len(steps)} steps")

        # Validate dependencies
        self._validate_dependencies(steps)

        # Create execution plan
        execution_plan = self._create_execution_plan(steps, max_parallel)

        # Execute steps according to plan
        results = []
        status = OrchestrationStatus.RUNNING

        try:
            for batch in execution_plan:
                if status == OrchestrationStatus.CANCELLED:
                    break

                # Execute batch in parallel
                batch_results = await self._execute_batch(
                    batch, context=context, progress_callback=progress_callback,
                )

                results.extend(batch_results)

                # Check if any step failed
                if any(not result.success for result in batch_results):
                    status = OrchestrationStatus.FAILED
                    break

            if status == OrchestrationStatus.RUNNING:
                status = OrchestrationStatus.COMPLETED

        except Exception as e:
            logger.exception(f"Workflow {workflow_id} failed: {e}")
            status = OrchestrationStatus.FAILED

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        success = status == OrchestrationStatus.COMPLETED

        logger.info(f"Workflow {workflow_id} completed: {status.value} in {duration:.2f}s")

        return OrchestrationResult(
            success=success,
            status=status,
            steps=results,
            duration=duration,
            start_time=start_time,
            end_time=end_time,
            metadata={
                "workflow_id": workflow_id,
                "max_parallel": max_parallel,
                "total_steps": len(steps),
            },
        )

    def _validate_dependencies(self, steps: list[OrchestrationStep]) -> None:
        """
        Validate that all dependencies exist.
        """
        step_names = {step.name for step in steps}

        for step in steps:
            for dep in step.dependencies:
                if dep not in step_names:
                    raise ValueError(f"Step '{step.name}' depends on unknown step '{dep}'")

    def _create_execution_plan(
        self, steps: list[OrchestrationStep], max_parallel: int,
    ) -> list[list[OrchestrationStep]]:
        """
        Create execution plan with dependency resolution.
        """
        plan = []
        remaining_steps = {step.name: step for step in steps}
        completed_steps = set()

        while remaining_steps:
            # Find steps that can be executed (dependencies satisfied)
            ready_steps = []
            for step in remaining_steps.values():
                if all(dep in completed_steps for dep in step.dependencies):
                    ready_steps.append(step)

            if not ready_steps:
                # Circular dependency or missing dependency
                remaining_names = list(remaining_steps.keys())
                raise ValueError(f"Cannot resolve dependencies for steps: {remaining_names}")

            # Limit parallel execution
            batch = ready_steps[:max_parallel]
            plan.append(batch)

            # Mark steps as completed
            for step in batch:
                completed_steps.add(step.name)
                del remaining_steps[step.name]

        return plan

    async def _execute_batch(
        self,
        batch: list[OrchestrationStep],
        *,
        context: ProjectContext | None = None,
        progress_callback: Callable[[CommandStage], None] | None = None,
    ) -> list[CommandResult]:
        """
        Execute a batch of steps in parallel.
        """

        async def execute_step(step: OrchestrationStep) -> CommandResult:
            """
            Execute a single step with retry logic.
            """
            for attempt in range(step.max_retries + 1):
                try:
                    # Check condition if provided
                    if step.condition and not step.condition():
                        logger.info(f"Skipping step '{step.name}' due to condition")
                        return CommandResult(
                            success=True,
                            exit_code=0,
                            stdout="Skipped due to condition",
                            stderr="",
                            duration=0.0,
                            stages=[],
                            metadata={"skipped": True, "reason": "condition"},
                        )

                    # Execute command
                    result = await self.command_engine.run_command(
                        step.command,
                        working_directory=context.project_path if context else None,
                        environment=context.environment if context else None,
                        timeout=step.timeout,
                        progress_callback=progress_callback,
                        stages=[step.name],
                    )

                    if result.success or attempt == step.max_retries:
                        return result

                    logger.warning(
                        f"Step '{step.name}' failed (attempt {attempt + 1}), retrying...",
                    )
                    await asyncio.sleep(2**attempt)  # Exponential backoff

                except Exception as e:
                    if attempt == step.max_retries:
                        logger.exception(
                            f"Step '{step.name}' failed after {step.max_retries + 1} attempts: {e}",
                        )
                        return CommandResult(
                            success=False,
                            exit_code=-1,
                            stdout="",
                            stderr=str(e),
                            duration=0.0,
                            stages=[],
                            metadata={"error": str(e), "attempts": attempt + 1},
                        )

                    logger.warning(f"Step '{step.name}' failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(2**attempt)

            # This should never be reached
            raise RuntimeError(f"Step '{step.name}' execution failed unexpectedly")

        # Execute all steps in the batch
        tasks = [execute_step(step) for step in batch]
        return await asyncio.gather(*tasks)

    async def execute_pipeline(
        self, pipeline_name: str, steps: list[OrchestrationStep], **kwargs,
    ) -> OrchestrationResult:
        """
        Execute a named pipeline with workflow management.
        """
        workflow_id = f"{pipeline_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Store running workflow
        task = asyncio.create_task(self.execute_workflow(steps, workflow_id=workflow_id, **kwargs))
        self._running_workflows[workflow_id] = task

        try:
            return await task
        finally:
            # Clean up
            self._running_workflows.pop(workflow_id, None)

    def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel a running workflow.
        """
        if workflow_id in self._running_workflows:
            task = self._running_workflows[workflow_id]
            task.cancel()
            del self._running_workflows[workflow_id]
            return True
        return False

    def get_running_workflows(self) -> list[str]:
        """
        Get list of running workflow IDs.
        """
        return list(self._running_workflows.keys())

    def cleanup(self) -> None:
        """
        Clean up all running workflows.
        """
        for task in self._running_workflows.values():
            task.cancel()
        self._running_workflows.clear()
        self.command_engine.cleanup()


# Predefined workflow templates
def create_build_pipeline(context: ProjectContext) -> list[OrchestrationStep]:
    """
    Create a standard build pipeline for a project.
    """
    steps = []

    # Validation step
    steps.append(
        OrchestrationStep(
            name="validate",
            description="Validate project structure",
            command=(
                ["python", "-m", "py_compile", "*.py"]
                if context.project_type.value == "python"
                else ["echo", "validation"]
            ),
            timeout=30,
        ),
    )

    # Install dependencies
    if context.dependencies:
        if context.project_type.value == "python":
            steps.append(
                OrchestrationStep(
                    name="install_deps",
                    description="Install dependencies",
                    command=["pip", "install", "-r", "requirements.txt"],
                    dependencies=["validate"],
                ),
            )
        elif context.project_type.value == "node":
            steps.append(
                OrchestrationStep(
                    name="install_deps",
                    description="Install dependencies",
                    command=["npm", "install"],
                    dependencies=["validate"],
                ),
            )

    # Run tests
    if context.test_command:
        steps.append(
            OrchestrationStep(
                name="test",
                description="Run tests",
                command=context.test_command.split(),
                dependencies=["install_deps"],
            ),
        )

    # Build project
    if context.build_command:
        steps.append(
            OrchestrationStep(
                name="build",
                description="Build project",
                command=context.build_command.split(),
                dependencies=["test"],
            ),
        )

    return steps


def create_deploy_pipeline(
    context: ProjectContext, target: str = "production",
) -> list[OrchestrationStep]:
    """
    Create a deployment pipeline for a project.
    """
    steps = []

    # Build pipeline first
    build_steps = create_build_pipeline(context)
    steps.extend(build_steps)

    # Deploy step
    if context.project_type.value == "python":
        steps.append(
            OrchestrationStep(
                name="deploy",
                description=f"Deploy to {target}",
                command=["twine", "upload", "dist/*"],
                dependencies=["build"],
                timeout=300,
            ),
        )
    elif context.project_type.value == "node":
        steps.append(
            OrchestrationStep(
                name="deploy",
                description=f"Deploy to {target}",
                command=["npm", "publish"],
                dependencies=["build"],
                timeout=300,
            ),
        )

    return steps
