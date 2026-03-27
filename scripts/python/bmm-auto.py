#!/usr/bin/env python3
"""BMM Workflow Automation Script.

Automates BMad Method workflows using auggie/claude CLI with streaming JSON support.
Supports parallel execution, live user interaction, and cross-project portability.
"""

import argparse
import asyncio
import json
import subprocess
from dataclasses import dataclass
from enum import Enum
from itertools import starmap
from pathlib import Path
from typing import Any

import yaml


class WorkflowStatus(Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    WAITING_USER = "waiting_user"
    COMPLETE = "complete"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class WorkflowTask:
    """Represents a single workflow task."""

    id: str
    name: str
    agent: str
    command: str
    status_type: str  # required, optional, recommended
    output_path: str | None = None
    note: str | None = None
    dependencies: list[str] | None = None
    status: WorkflowStatus = WorkflowStatus.PENDING

    def __post_init__(self) -> None:
        """__post_init__ implementation."""
        if self.dependencies is None:
            self.dependencies = []


class BMMAutomation:
    """Main automation orchestrator for BMM workflows."""

    def __init__(self, project_root: Path, cli_tool: str = "auto", verbose: bool = False) -> None:
        """Initialize."""
        self.project_root = project_root
        self.verbose = verbose
        self.bmad_folder = project_root / ".bmad"
        self.docs_folder = project_root / "docs"
        self.workflow_status_file = self.docs_folder / "bmm-workflow-status.yaml"

        # Auto-detect or use specified CLI tool
        self.cli_tool = self._detect_cli_tool() if cli_tool == "auto" else cli_tool

        # Load configuration
        self.config = self._load_config()
        self.workflow_status = self._load_workflow_status()

    def _detect_cli_tool(self) -> str:
        """Detect available CLI tool (auggie or claude)."""
        if subprocess.run(["which", "auggie"], capture_output=True).returncode == 0:
            return "auggie"
        if subprocess.run(["which", "claude"], capture_output=True).returncode == 0:
            return "claude"
        msg = "Neither auggie nor claude CLI found. Please install one."
        raise RuntimeError(msg)

    def _load_config(self) -> dict[str, Any]:
        """Load BMM configuration."""
        config_file = self.bmad_folder / "bmm" / "config.yaml"
        if not config_file.exists():
            return {}
        with Path(config_file).open(encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_workflow_status(self) -> dict[str, Any] | None:
        """Load workflow status file."""
        if not self.workflow_status_file.exists():
            return None
        with Path(self.workflow_status_file).open(encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _save_workflow_status(self) -> None:
        """Save updated workflow status."""
        if self.workflow_status:
            with Path(self.workflow_status_file).open("w", encoding="utf-8") as f:
                yaml.dump(self.workflow_status, f, default_flow_style=False, sort_keys=False)

    def check_initialization(self) -> bool:
        """Check if project is initialized with BMM."""
        return self.bmad_folder.exists() and self.workflow_status_file.exists() and self.workflow_status is not None

    async def run_init(self) -> bool:
        """Run workflow initialization if needed."""
        if self.check_initialization():
            return True

        success = await self._run_workflow(
            agent="bmad-master",
            workflow_command="/bmad:bmm:workflows:workflow-status:init",
            interactive=True,
        )

        if success:
            self.workflow_status = self._load_workflow_status()
        return success

    def _parse_workflow_tasks(self) -> list[WorkflowTask]:
        """Parse workflow status into executable tasks."""
        if not self.workflow_status or "workflow_status" not in self.workflow_status:
            return []

        tasks = []
        workflow_data = self.workflow_status["workflow_status"]

        for phase_data in workflow_data.values():
            for workflow_id, workflow_info in phase_data.items():
                # Skip if already completed (has file path instead of status)
                current_status = workflow_info.get("status", "")
                if isinstance(current_status, str) and current_status.startswith("docs/"):
                    continue

                # Check if included (for optional workflows)
                if not workflow_info.get("included", True):
                    continue

                task = WorkflowTask(
                    id=workflow_id,
                    name=workflow_id.replace("-", " ").title(),
                    agent=workflow_info["agent"],
                    command=workflow_info["command"],
                    status_type=workflow_info["status"],
                    output_path=workflow_info.get("output"),
                    note=workflow_info.get("note"),
                )
                tasks.append(task)

        return tasks

    def _build_agent_prompt(self, workflow_command: str, _structured_output: bool = True) -> str:
        """Build prompt for agent with structured output instructions."""
        return f"""Execute the workflow: {workflow_command}

CRITICAL INSTRUCTIONS FOR STRUCTURED OUTPUT:
1. When you need user input, output JSON in this format:
   {{"type": "user_input", "question": "your question", "options": ["a", "b", "c"]}}

2. When you complete a section and need approval, output:
   {{"type": "checkpoint", "section": "section name", "content": "generated content", "next": "what comes next"}}

3. When you complete the workflow, output:
   {{"type": "complete", "output_file": "path/to/file.md", "summary": "what was accomplished"}}

4. For progress updates, output:
   {{"type": "progress", "step": "current step", "message": "status message"}}

Follow the workflow instructions exactly. Use the structured JSON format above for all interactions.
"""

    async def _run_workflow(
        self,
        agent: str,
        workflow_command: str,
        interactive: bool = True,
        structured: bool = True,
    ) -> bool:
        """Run a single workflow using CLI tool."""
        if self.cli_tool == "auggie":
            return await self._run_auggie_workflow(agent, workflow_command, interactive, structured)
        return await self._run_claude_workflow(agent, workflow_command, interactive, structured)

    async def _run_auggie_workflow(
        self,
        agent: str,
        workflow_command: str,
        interactive: bool,
        structured: bool,
    ) -> bool:
        """Run workflow using auggie CLI."""
        # Load agent configuration
        agent_file = self.bmad_folder / "bmm" / "agents" / f"{agent}.agent.yaml"
        if not agent_file.exists():
            agent_file = self.bmad_folder / "core" / "agents" / f"{agent}.agent.yaml"

        if not agent_file.exists():
            return False

        # Build command
        cmd = ["auggie"]

        if interactive:
            # Interactive mode - let user interact directly
            cmd.extend(["--workspace-root", str(self.project_root), "--instruction", workflow_command])
        else:
            # Automated mode with structured output
            prompt = self._build_agent_prompt(workflow_command, structured)
            cmd.extend([
                "--print",
                "--output-format",
                "json" if structured else "text",
                "--workspace-root",
                str(self.project_root),
                "--instruction",
                prompt,
            ])

        if self.verbose:
            pass

        try:
            if interactive:
                # Run interactively
                result = subprocess.run(cmd, cwd=self.project_root)
                return result.returncode == 0
            # Run with output capture
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)

            if result.returncode == 0:
                if structured:
                    self._process_structured_output(result.stdout)
                return True
            return False
        except Exception:
            return False

    async def _run_claude_workflow(
        self,
        _agent: str,
        workflow_command: str,
        interactive: bool,
        structured: bool,
    ) -> bool:
        """Run workflow using claude CLI with streaming JSON support."""
        # Build command
        cmd = ["claude"]

        if interactive:
            cmd.extend([workflow_command])
        else:
            prompt = self._build_agent_prompt(workflow_command, structured)
            cmd.extend(["--print", "--output-format", "stream-json" if structured else "text", prompt])

        if self.verbose:
            pass

        try:
            if interactive:
                result = subprocess.run(cmd, cwd=self.project_root)
                return result.returncode == 0
            # Use streaming JSON for real-time processing
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Process streaming output
            stdout = process.stdout
            if stdout is None:
                process.wait()
                return process.returncode == 0
            for line in stdout:
                if line.strip():
                    try:
                        data = json.loads(line)
                        self._process_streaming_message(data)
                    except json.JSONDecodeError:
                        if self.verbose:
                            pass

            process.wait()
            return process.returncode == 0
        except Exception:
            return False

    def _process_structured_output(self, output: str) -> None:
        """Process structured JSON output from workflow."""
        try:
            data = json.loads(output)
            if isinstance(data, dict):
                self._process_streaming_message(data)
            elif isinstance(data, list):
                for item in data:
                    self._process_streaming_message(item)
        except json.JSONDecodeError:
            pass

    def _process_streaming_message(self, data: dict[str, Any]) -> None:
        """Process a single streaming message."""
        msg_type = data.get("type", "")

        if msg_type == "user_input":
            # Handle user input request
            question = data.get("question", "")
            options = data.get("options", [])
            self._handle_user_input(question, options)

        elif msg_type == "checkpoint":
            # Handle checkpoint/approval
            section = data.get("section", "")
            content = data.get("content", "")
            next_step = data.get("next", "")
            self._handle_checkpoint(section, content, next_step)

        elif msg_type == "complete":
            # Handle completion
            data.get("output_file", "")
            data.get("summary", "")

        elif msg_type == "progress":
            # Handle progress update
            data.get("step", "")
            data.get("message", "")

        # Unknown message type
        elif self.verbose:
            pass

    def _handle_user_input(self, _question: str, options: list[str]) -> None:
        """Handle user input request."""
        if options:
            for _i, _opt in enumerate(options, 1):
                pass
        return input("Your answer: ")
        # tracked: https://github.com/KooshaPari/trace/issues/233

    def _handle_checkpoint(self, _section: str, _content: str, _next_step: str) -> None:
        """Handle checkpoint approval."""
        return input("\n[c] Continue, [e] Edit, [s] Skip: ").lower()

    async def run_workflow_sequence(
        self,
        workflow_ids: list[str] | None = None,
        parallel: bool = False,
        interactive: bool = True,
    ) -> None:
        """Run a sequence of workflows."""
        tasks = self._parse_workflow_tasks()

        if workflow_ids:
            tasks = [t for t in tasks if t.id in workflow_ids]

        if not tasks:
            return

        for _task in tasks:
            pass

        if parallel and len(tasks) > 1:
            # Run compatible workflows in parallel
            await self._run_parallel_workflows(tasks, interactive)
        else:
            # Run sequentially
            for task in tasks:
                await self._run_single_task(task, interactive)

    async def _run_single_task(self, task: WorkflowTask, interactive: bool) -> None:
        """Run a single workflow task."""
        if task.note:
            pass

        task.status = WorkflowStatus.RUNNING
        success = await self._run_workflow(agent=task.agent, workflow_command=task.command, interactive=interactive)

        if success:
            task.status = WorkflowStatus.COMPLETE
            self._update_workflow_status(task)
        else:
            task.status = WorkflowStatus.FAILED

    async def _run_parallel_workflows(self, tasks: list[WorkflowTask], interactive: bool) -> None:
        """Run compatible workflows in parallel."""
        # Group tasks by agent to avoid conflicts
        agent_groups = {}
        for task in tasks:
            if task.agent not in agent_groups:
                agent_groups[task.agent] = []
            agent_groups[task.agent].append(task)

        # Run each agent's tasks sequentially, but different agents in parallel
        async def run_agent_tasks(_agent: str, agent_tasks: list[WorkflowTask]) -> None:
            for task in agent_tasks:
                await self._run_single_task(task, interactive)

        # Create tasks for each agent group
        agent_coroutines = list(starmap(run_agent_tasks, agent_groups.items()))

        # Run all agent groups in parallel
        await asyncio.gather(*agent_coroutines)

    def _update_workflow_status(self, task: WorkflowTask) -> None:
        """Update workflow status file after task completion."""
        if not self.workflow_status:
            return

        # Find and update the task in workflow_status
        for phase_data in self.workflow_status["workflow_status"].values():
            if task.id in phase_data:
                # Mark as complete with output path
                if task.output_path:
                    phase_data[task.id]["status"] = task.output_path
                else:
                    phase_data[task.id]["status"] = "complete"
                break

        self._save_workflow_status()

    def show_status(self) -> None:
        """Display current workflow status."""
        if not self.workflow_status:
            return

        tasks = self._parse_workflow_tasks()
        sum(1 for t in tasks if t.status == WorkflowStatus.COMPLETE)

        # Group by phase
        current_phase = None
        for phase_key, phase_data in self.workflow_status["workflow_status"].items():
            phase_name = phase_key.replace("_", " ").title()
            if phase_name != current_phase:
                current_phase = phase_name

            for workflow_info in phase_data.values():
                status = workflow_info.get("status", "pending")
                "✅" if isinstance(status, str) and status.startswith("docs/") else "⏳"
                workflow_info.get("status", "unknown")

                if workflow_info.get("note"):
                    pass


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="BMM Workflow Automation - Automate BMad Method workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize a new project
  %(prog)s init

  # Show current status
  %(prog)s status

  # Run all pending workflows interactively
  %(prog)s run --interactive

  # Run specific workflows
  %(prog)s run brainstorm-project research

  # Run Phase 0 (Discovery) workflows in parallel
  %(prog)s run --phase 0 --parallel

  # Run all workflows automatically (non-interactive)
  %(prog)s run --auto
        """,
    )

    parser.add_argument("command", choices=["init", "status", "run", "next"], help="Command to execute")

    parser.add_argument("workflows", nargs="*", help="Specific workflow IDs to run (for run command)")

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)",
    )

    parser.add_argument(
        "--cli",
        choices=["auto", "auggie", "claude"],
        default="auto",
        help="CLI tool to use (default: auto-detect)",
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        default=True,
        help="Run workflows interactively (default)",
    )

    parser.add_argument("--auto", action="store_true", help="Run workflows automatically without user interaction")

    parser.add_argument("--parallel", action="store_true", help="Run compatible workflows in parallel")

    parser.add_argument("--phase", type=int, choices=[0, 1, 2, 3], help="Run all workflows in a specific phase")

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Create automation instance
    automation = BMMAutomation(project_root=args.project_root, cli_tool=args.cli, verbose=args.verbose)

    # Execute command
    if args.command == "init":
        asyncio.run(automation.run_init())

    elif args.command == "status":
        automation.show_status()

    elif args.command == "run":
        interactive = not args.auto
        asyncio.run(
            automation.run_workflow_sequence(
                workflow_ids=args.workflows or None,
                parallel=args.parallel,
                interactive=interactive,
            ),
        )

    elif args.command == "next":
        # Run the next pending workflow
        tasks = automation._parse_workflow_tasks()
        if tasks:
            asyncio.run(automation._run_single_task(tasks[0], interactive=True))


if __name__ == "__main__":
    main()
