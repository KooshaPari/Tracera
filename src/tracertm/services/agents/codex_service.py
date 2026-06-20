"""Codex CLI agent service for QA Integration (STORY-008).

Integrates with OpenAI Codex CLI for AI-powered code review, image/video analysis, and test generation.
"""

from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from tracertm.models.codex_agent import CodexAgentInteraction
from tracertm.repositories.execution_repository import ExecutionArtifactRepository
from tracertm.services.recording.ffmpeg_pipeline import FFmpegPipeline

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from tracertm.services.execution import ExecutionService


class CodexExecutionError(Exception):
    """Raised when Codex execution fails."""


@dataclass
class CodexTask:
    """Definition of a Codex agent task."""

    task_type: str  # review_image, review_video, code_review, generate_test, custom
    prompt: str
    input_files: list[str] | None = None
    codebase_dir: str | None = None
    full_auto: bool = False  # --full-auto for CI/CD
    sandbox: str = "workspace-write"  # read-only, workspace-write, danger-full-access
    timeout_seconds: int = 300
    model: str = "o3"  # o3, o4-mini, gpt-4


class CodexAgentService:
    """Integration with OpenAI Codex CLI using OAuth authentication.

    Authentication Methods:
    1. OAuth (default): codex login - opens browser for ChatGPT login
    2. Device Code: codex login --device-auth - for headless/SSH environments
    3. API Key: OPENAI_API_KEY env var - for CI/CD
    """

    def __init__(
        self,
        session: AsyncSession,
        execution_service: ExecutionService,
        *,
        codex_command: str | None = None,
        ffmpeg_pipeline: FFmpegPipeline | None = None,
    ) -> None:
        """Initialize Codex agent service.

        Args:
            session: Database session.
            execution_service: ExecutionService for artifact access.
            codex_command: Override Codex command (default: "codex").
            ffmpeg_pipeline: FFmpegPipeline for video frame extraction.
        """
        self.session = session
        self._exec_service = execution_service
        self._codex_cmd = codex_command or os.getenv("CODEX_COMMAND", "codex")
        self._ffmpeg = ffmpeg_pipeline or FFmpegPipeline()
        self._artifact_repo = ExecutionArtifactRepository(session)

    async def check_availability(self) -> tuple[bool, str]:
        """Check if Codex CLI is installed."""
        try:
            proc = await asyncio.create_subprocess_exec(
                self._codex_cmd,
                "--version",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
        except FileNotFoundError:
            return False, "Codex CLI not found (npm install -g @openai/codex)"
        else:
            if proc.returncode == 0:
                return True, stdout.decode().strip()
            return False, "Codex CLI not working"

    async def check_auth_status(self) -> tuple[bool, str]:
        """Check if authenticated with Codex."""
        try:
            proc = await asyncio.create_subprocess_exec(
                self._codex_cmd,
                "auth",
                "status",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            output = stdout.decode().lower()
            authenticated = "authenticated" in output or "logged in" in output
            return authenticated, stdout.decode().strip()
        except (OSError, subprocess.SubprocessError, UnicodeDecodeError) as e:
            return False, str(e)

    async def setup_oauth(self, device_auth: bool = False) -> str:
        """Initiate OAuth flow.

        Args:
            device_auth: Use device code flow (for headless environments).

        Returns:
            Instructions/URL for user to visit.
        """
        cmd = [self._codex_cmd, "login"]
        if device_auth:
            cmd.append("--device-auth")
        proc = await asyncio.create_subprocess_exec(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            msg = f"OAuth setup failed: {stderr.decode()}"
            raise CodexExecutionError(msg)
        return stdout.decode()

    async def run_task(
        self,
        task: CodexTask,
        project_id: str,
        *,
        execution_id: str | None = None,
        artifact_id: str | None = None,
    ) -> CodexAgentInteraction:
        """Execute a Codex agent task and record interaction.

        Args:
            task: CodexTask definition.
            project_id: Project ID.
            execution_id: Optional execution ID.
            artifact_id: Optional artifact ID being reviewed.

        Returns:
            CodexAgentInteraction record.
        """
        # Create interaction record
        interaction = CodexAgentInteraction(
            id=str(uuid4()),
            project_id=project_id,
            execution_id=execution_id,
            artifact_id=artifact_id,
            task_type=task.task_type,
            input_data=asdict(task),
            prompt=task.prompt,
            status="pending",
        )
        self.session.add(interaction)
        await self.session.flush()

        try:
            # Build command
            cmd = [self._codex_cmd, "exec"]
            cmd.extend(["--task", task.prompt])
            cmd.extend(["--model", task.model])
            cmd.extend(["--sandbox", task.sandbox])

            if task.full_auto:
                cmd.append("--full-auto")

            if task.codebase_dir:
                cmd.extend(["--cwd", task.codebase_dir])

            if task.input_files:
                for file_path in task.input_files:
                    cmd.extend(["--file", file_path])

            # Update status
            interaction.status = "running"
            interaction.started_at = datetime.now(UTC)
            await self.session.flush()

            # Execute
            env = self._get_sanitized_env()
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )

            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=task.timeout_seconds)

            output_text = stdout.decode()
            interaction.output_data = {
                "raw_output": output_text,
                "parsed": self._parse_output(output_text),
                "exit_code": proc.returncode,
            }
            interaction.response = output_text
            interaction.status = "completed" if proc.returncode == 0 else "failed"
            completed_at = datetime.now(UTC)
            interaction.completed_at = completed_at
            if interaction.started_at:
                delta = completed_at - interaction.started_at
                interaction.duration_ms = int(delta.total_seconds() * 1000)

            if proc.returncode != 0:
                interaction.error_message = stderr.decode()[:1000]

        except TimeoutError:
            interaction.status = "failed"
            interaction.error_message = f"Task timed out after {task.timeout_seconds}s"
            interaction.completed_at = datetime.now(UTC)
        except (OSError, subprocess.SubprocessError, UnicodeDecodeError) as e:
            interaction.status = "failed"
            interaction.error_message = str(e)[:1000]
            interaction.completed_at = datetime.now(UTC)

        await self.session.flush()
        await self.session.refresh(interaction)
        return interaction

    async def review_image(
        self,
        artifact_id: str,
        prompt: str,
        project_id: str,
        *,
        execution_id: str | None = None,
    ) -> CodexAgentInteraction:
        """Have Codex review an image artifact (screenshot, diagram, etc.)."""
        artifact = await self._artifact_repo.get_by_id(artifact_id)
        if not artifact:
            msg = f"Artifact {artifact_id} not found"
            raise CodexExecutionError(msg)
        if artifact.artifact_type not in {"screenshot", "gif"}:
            msg = f"Artifact type {artifact.artifact_type} not supported for image review"
            raise CodexExecutionError(msg)

        task = CodexTask(
            task_type="review_image",
            prompt=f"Review this image: {prompt}",
            input_files=[artifact.file_path],
            sandbox="read-only",
        )
        return await self.run_task(task, project_id, execution_id=execution_id, artifact_id=artifact_id)

    async def review_video(
        self,
        artifact_id: str,
        prompt: str,
        project_id: str,
        *,
        execution_id: str | None = None,
        max_frames: int = 10,
    ) -> CodexAgentInteraction:
        """Have Codex review a video by analyzing key frames.

        Extracts frames at regular intervals and sends to Codex.
        """
        artifact = await self._artifact_repo.get_by_id(artifact_id)
        if not artifact:
            msg = f"Artifact {artifact_id} not found"
            raise CodexExecutionError(msg)
        if artifact.artifact_type != "video":
            msg = f"Artifact type {artifact.artifact_type} not supported for video review"
            raise CodexExecutionError(msg)

        frame_dir = tempfile.mkdtemp(prefix="codex_frames_")
        try:
            # Extract frames
            frames = await self._ffmpeg.extract_frames(artifact.file_path, frame_dir, interval_seconds=2.0)

            # Limit frames
            frames = frames[:max_frames]

            task = CodexTask(
                task_type="review_video",
                prompt=f"Review these video frames showing a user interaction: {prompt}",
                input_files=[str(f) for f in frames],
                sandbox="read-only",
            )
            return await self.run_task(task, project_id, execution_id=execution_id, artifact_id=artifact_id)
        finally:
            shutil.rmtree(frame_dir, ignore_errors=True)

    async def code_review(
        self,
        file_paths: list[str],
        prompt: str,
        project_id: str,
        *,
        codebase_dir: str | None = None,
        execution_id: str | None = None,
    ) -> CodexAgentInteraction:
        """Have Codex review code files."""
        task = CodexTask(
            task_type="code_review",
            prompt=prompt,
            input_files=file_paths,
            codebase_dir=codebase_dir,
            sandbox="read-only",
        )
        return await self.run_task(task, project_id, execution_id=execution_id)

    async def generate_test(
        self,
        file_paths: list[str],
        prompt: str,
        project_id: str,
        *,
        codebase_dir: str | None = None,
        execution_id: str | None = None,
    ) -> CodexAgentInteraction:
        """Have Codex generate tests for code files."""
        task = CodexTask(
            task_type="generate_test",
            prompt=f"Generate comprehensive tests: {prompt}",
            input_files=file_paths,
            codebase_dir=codebase_dir,
            sandbox="workspace-write",
        )
        return await self.run_task(task, project_id, execution_id=execution_id)

    def _get_sanitized_env(self) -> dict[str, str]:
        """Get sanitized environment for Codex execution."""
        env = os.environ.copy()
        # Keep only safe env vars
        safe_keys = {
            "PATH",
            "HOME",
            "USER",
            "SHELL",
            "OPENAI_API_KEY",  # For CI/CD fallback
            "CODEX_COMMAND",
        }
        return {k: v for k, v in env.items() if k in safe_keys}

    def _parse_output(self, output: str) -> dict[str, Any]:
        """Parse Codex output (basic implementation)."""
        # Try to extract JSON if present
        import json
        import re

        json_match = re.search(r"\{.*\}", output, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        return {"text": output}
