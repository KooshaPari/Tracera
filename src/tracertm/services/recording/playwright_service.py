"""Playwright web testing service for QA Integration (STORY-007).

Executes Playwright browser automation and captures screenshots/videos.
"""

from __future__ import annotations

import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tracertm.models.execution_config import ExecutionEnvironmentConfig
    from tracertm.services.execution import ExecutionService


class PlaywrightExecutionError(Exception):
    """Raised when Playwright execution fails."""


class PlaywrightExecutionService:
    """Service for executing Playwright browser tests."""

    def __init__(self, execution_service: ExecutionService) -> None:
        """Initialize Playwright execution service.

        Args:
            execution_service: ExecutionService instance for artifact storage.
        """
        self._exec_service = execution_service

    async def execute(
        self,
        execution_id: str,
        url: str | None = None,
        script: str | None = None,
        *,
        screenshot: bool = True,
        video: bool = False,
        trace: bool = False,
        use_docker: bool = False,
    ) -> dict[str, Any]:
        """Execute Playwright browser automation and store artifacts.

        Args:
            execution_id: Execution ID (must exist and be in 'pending' status).
            url: URL to navigate to (optional if script provided).
            script: Python script to execute (optional if url provided).
            screenshot: Capture screenshot (default: True).
            video: Capture video (default: False).
            trace: Capture trace (default: False).
            use_docker: Use Docker container if True (default: False uses native subprocess).

        Returns:
            Dict with keys: success, artifacts (list of artifact_ids), error_message.

        Raises:
            PlaywrightExecutionError: If execution not found or Playwright fails.
        """
        execution = await self._exec_service.get(execution_id)
        if not execution:
            msg = f"Execution {execution_id} not found"
            raise PlaywrightExecutionError(msg)
        if execution.status != "pending":
            msg = f"Execution {execution_id} is {execution.status}, expected pending"
            raise PlaywrightExecutionError(msg)

        config = await self._exec_service.get_config(execution.project_id)
        if config and not config.playwright_enabled:
            msg = "Playwright is disabled for this project"
            raise PlaywrightExecutionError(msg)

        # Use config defaults if not specified
        if screenshot is None:
            screenshot = config.auto_screenshot if config else True
        if video is None:
            video = config.auto_video if config else False

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            artifacts: list[str] = []

            try:
                if use_docker and execution.container_id:
                    result = await self._execute_in_container(
                        execution_id,
                        url,
                        script,
                        tmp_path,
                        screenshot=screenshot,
                        video=video,
                        trace=trace,
                        config=config,
                    )
                else:
                    # Native subprocess execution (default)
                    result = await self._execute_subprocess(
                        execution_id,
                        url,
                        script,
                        tmp_path,
                        screenshot=screenshot,
                        video=video,
                        trace=trace,
                        config=config,
                    )

                if not result["success"]:
                    await self._exec_service.complete(
                        execution_id,
                        exit_code=1,
                        error_message=result.get("error_message"),
                    )
                    return result

                # Store artifacts
                if screenshot and (tmp_path / "screenshot.png").exists():
                    artifact = await self._exec_service.store_artifact(
                        execution_id,
                        tmp_path / "screenshot.png",
                        "screenshot",
                        filename=f"{execution_id}_screenshot.png",
                    )
                    if artifact:
                        artifacts.append(artifact.id)

                if video and (tmp_path / "video.webm").exists():
                    artifact = await self._exec_service.store_artifact(
                        execution_id,
                        tmp_path / "video.webm",
                        "video",
                        filename=f"{execution_id}_video.webm",
                    )
                    if artifact:
                        artifacts.append(artifact.id)

                if trace and (tmp_path / "trace.zip").exists():
                    artifact = await self._exec_service.store_artifact(
                        execution_id,
                        tmp_path / "trace.zip",
                        "trace",
                        filename=f"{execution_id}_trace.zip",
                    )
                    if artifact:
                        artifacts.append(artifact.id)

            except Exception as e:
                await self._exec_service.complete(
                    execution_id,
                    exit_code=1,
                    error_message=str(e),
                )
                msg = f"Playwright execution failed: {e}"
                raise PlaywrightExecutionError(msg) from e
            else:
                return {
                    "success": True,
                    "artifacts": artifacts,
                }

    async def _execute_subprocess(
        self,
        _execution_id: str,
        url: str | None,
        script: str | None,
        workdir: Path,
        *,
        screenshot: bool,
        video: bool,
        trace: bool,
        config: ExecutionEnvironmentConfig | None,
    ) -> dict[str, Any]:
        """Execute Playwright via subprocess."""
        script_path = workdir / "playwright_script.py"
        self._write_playwright_script(script_path, url, script, screenshot, video, trace, config)

        try:
            proc = await asyncio.create_subprocess_exec(
                "python",
                str(script_path),
                cwd=str(workdir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            _stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
            if proc.returncode != 0:
                return {
                    "success": False,
                    "error_message": f"Playwright failed: {stderr.decode()[:500]}",
                }
        except TimeoutError:
            return {
                "success": False,
                "error_message": "Playwright execution timed out after 300s",
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error_message": "Playwright not installed. Install with: pip install playwright && playwright install",
            }
        else:
            return {"success": True}

    async def _execute_in_container(
        self,
        execution_id: str,
        url: str | None,
        script: str | None,
        workdir: Path,
        *,
        screenshot: bool,
        video: bool,
        trace: bool,
        config: ExecutionEnvironmentConfig | None,
    ) -> dict[str, Any]:
        """Execute Playwright inside Docker container."""
        docker = self._exec_service.docker()
        execution = await self._exec_service.get(execution_id)
        if not execution or not execution.container_id or not docker:
            return await self._execute_subprocess(
                execution_id,
                url,
                script,
                workdir,
                screenshot=screenshot,
                video=video,
                trace=trace,
                config=config,
            )

        script_path = workdir / "playwright_script.py"
        self._write_playwright_script(script_path, url, script, screenshot, video, trace, config)

        # Copy script into container (path inside Docker container, not host)
        container_script = "/tmp/playwright_script.py"  # nosec B108 -- path inside Docker container
        code, _, stderr = await docker._run(
            "cp",
            str(script_path),
            f"{execution.container_id}:{container_script}",
            timeout=30,
        )
        if code != 0:
            return {
                "success": False,
                "error_message": f"Failed to copy script to container: {stderr[:200]}",
            }

        # Run playwright inside container
        code, _stdout, stderr = await docker.exec(
            execution.container_id,
            ["python", container_script],
            timeout=300,
        )
        if code != 0:
            return {
                "success": False,
                "error_message": f"Playwright failed in container: {stderr[:500]}",
            }

        # Copy artifacts back from container
        for artifact_file in ["screenshot.png", "video.webm", "trace.zip"]:
            code, _, _ = await docker._run(
                "cp",
                f"{execution.container_id}:/tmp/{artifact_file}",
                str(workdir / artifact_file),
                timeout=30,
            )

        return {"success": True}

    def _write_playwright_script(
        self,
        script_path: Path,
        url: str | None,
        script: str | None,
        screenshot: bool,
        video: bool,
        trace: bool,
        config: ExecutionEnvironmentConfig | None,
    ) -> None:
        """Write Playwright Python script to file."""
        browser = config.playwright_browser if config else "chromium"
        headless = config.playwright_headless if config else True
        width = config.playwright_viewport_width if config else 1280
        height = config.playwright_viewport_height if config else 720

        if script:
            user_script = script
        elif url:
            user_script = f"""await page.goto("{url}")
await page.wait_for_load_state("networkidle")"""
        else:
            user_script = "pass"

        content = f"""#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.{browser}.launch(headless={str(headless).lower()})
        context = await browser.new_context(
            viewport={{'width': {width}, 'height': {height}}},
            record_video_dir="/tmp" if {str(video).lower()} else None,
        )
        if {str(trace).lower()}:
            await context.tracing.start(screenshots=True, snapshots=True)

        page = await context.new_page()

        try:
{self._indent(user_script, 12)}

            if {str(screenshot).lower()}:
                await page.screenshot(path="/tmp/screenshot.png", full_page=True)

            if {str(trace).lower()}:
                await context.tracing.stop(path="/tmp/trace.zip")
        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
"""
        script_path.write_text(content, encoding="utf-8")
        script_path.chmod(0o755)

    def _indent(self, text: str, spaces: int) -> str:
        """Indent text by given number of spaces."""
        indent = " " * spaces
        return "\n".join(indent + line if line.strip() else line for line in text.split("\n"))
