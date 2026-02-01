# Quality Engineering System - Technical Specification

**Document Type**: Technical Implementation Guide
**Status**: Ready for Development
**Target Audience**: Backend/Frontend Developers

---

## 1. Database Schema Extensions

### 1.1 Migration Script: ExecutionEnvironment

```python
# alembic/versions/018_add_execution_environment.py
"""Add execution environment models."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # ExecutionEnvironment table
    op.create_table(
        'execution_environments',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('project_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('environment_type', sa.String(50), nullable=False),
        sa.Column('runtime', sa.String(50), nullable=False),
        sa.Column('repo_url', sa.String(1000), nullable=False),
        sa.Column('repo_branch', sa.String(255), nullable=False, server_default='main'),
        sa.Column('repo_auth_type', sa.String(50), nullable=True),
        sa.Column('package_manager', sa.String(50), nullable=False),
        sa.Column('setup_script', sa.Text, nullable=True),
        sa.Column('environment_variables', sa.JSON, nullable=False, server_default='{}'),
        sa.Column('cpu_cores_limit', sa.Integer, nullable=False, server_default='2'),
        sa.Column('memory_limit_mb', sa.Integer, nullable=False, server_default='2048'),
        sa.Column('timeout_seconds', sa.Integer, nullable=False, server_default='3600'),
        sa.Column('detected_frameworks', sa.JSON, nullable=False, server_default='[]'),
        sa.Column('test_command', sa.String(500), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('last_tested_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('health_check_error', sa.Text, nullable=True),
        sa.Column('capture_screenshots', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('capture_videos', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('capture_console_logs', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('capture_network_logs', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('capture_coverage', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('version', sa.Integer, nullable=False, server_default='1'),
        sa.Column('integration_credential_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['integration_credential_id'], ['integration_credentials.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index('idx_exec_env_project', 'execution_environments', ['project_id'])
    op.create_index('idx_exec_env_status', 'execution_environments', ['status'])
    op.create_index('idx_exec_env_runtime', 'execution_environments', ['runtime'])

    # ExecutionSession table
    op.create_table(
        'execution_sessions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('environment_id', sa.String(36), nullable=False),
        sa.Column('test_run_id', sa.String(36), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer, nullable=True),
        sa.Column('container_id', sa.String(255), nullable=True),
        sa.Column('container_status', sa.String(50), nullable=True),
        sa.Column('stdout_log_url', sa.String(1000), nullable=True),
        sa.Column('stderr_log_url', sa.String(1000), nullable=True),
        sa.Column('cpu_used_percent', sa.Float, nullable=True),
        sa.Column('memory_used_mb', sa.Integer, nullable=True),
        sa.Column('peak_memory_mb', sa.Integer, nullable=True),
        sa.Column('tests_executed', sa.Integer, nullable=False, server_default='0'),
        sa.Column('tests_passed', sa.Integer, nullable=False, server_default='0'),
        sa.Column('tests_failed', sa.Integer, nullable=False, server_default='0'),
        sa.Column('test_coverage_percent', sa.Float, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('error_code', sa.String(50), nullable=True),
        sa.Column('git_commit_sha', sa.String(64), nullable=True),
        sa.Column('git_branch', sa.String(255), nullable=True),
        sa.Column('github_check_run_id', sa.String(255), nullable=True),
        sa.Column('github_pr_number', sa.Integer, nullable=True),
        sa.Column('session_metadata', sa.JSON, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['environment_id'], ['execution_environments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index('idx_exec_session_env', 'execution_sessions', ['environment_id'])
    op.create_index('idx_exec_session_test_run', 'execution_sessions', ['test_run_id'])
    op.create_index('idx_exec_session_status', 'execution_sessions', ['status'])
    op.create_index('idx_exec_session_git_commit', 'execution_sessions', ['git_commit_sha'])

    # ExecutionArtifact table
    op.create_table(
        'execution_artifacts',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('test_result_id', sa.String(36), nullable=False),
        sa.Column('execution_session_id', sa.String(36), nullable=False),
        sa.Column('artifact_type', sa.String(50), nullable=False),
        sa.Column('artifact_name', sa.String(255), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('storage_path', sa.String(1000), nullable=False),
        sa.Column('storage_backend', sa.String(50), nullable=False, server_default='s3'),
        sa.Column('file_size_bytes', sa.Integer, nullable=False),
        sa.Column('width', sa.Integer, nullable=True),
        sa.Column('height', sa.Integer, nullable=True),
        sa.Column('duration_seconds', sa.Float, nullable=True),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('test_step_index', sa.Integer, nullable=True),
        sa.Column('is_processed', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('processing_metadata', sa.JSON, nullable=False, server_default='{}'),
        sa.Column('is_public', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('share_token', sa.String(255), nullable=True),
        sa.Column('version', sa.Integer, nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['test_result_id'], ['test_results.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['execution_session_id'], ['execution_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('share_token'),
    )

    op.create_index('idx_artifact_result', 'execution_artifacts', ['test_result_id'])
    op.create_index('idx_artifact_session', 'execution_artifacts', ['execution_session_id'])
    op.create_index('idx_artifact_type', 'execution_artifacts', ['artifact_type'])
    op.create_index('idx_artifact_backend', 'execution_artifacts', ['storage_backend'])

    # TestNodeMetadata table
    op.create_table(
        'test_node_metadata',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('graph_id', sa.String(255), nullable=False),
        sa.Column('item_id', sa.String(255), nullable=False),
        sa.Column('last_test_result', sa.String(50), nullable=True),
        sa.Column('last_execution_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('execution_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('pass_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('fail_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('pass_rate', sa.Float, nullable=True),
        sa.Column('test_coverage_percent', sa.Float, nullable=True),
        sa.Column('coverage_status', sa.String(50), nullable=True),
        sa.Column('primary_artifact_id', sa.String(36), nullable=True),
        sa.Column('artifact_ids', sa.JSON, nullable=False, server_default='[]'),
        sa.Column('test_status', sa.String(50), nullable=False, server_default='untested'),
        sa.Column('is_flaky', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('flaky_indicator', sa.Float, nullable=True),
        sa.Column('node_display_config', sa.JSON, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['graph_id', 'item_id'], ['graph_nodes.graph_id', 'graph_nodes.item_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['primary_artifact_id'], ['execution_artifacts.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('graph_id', 'item_id'),
    )

    op.create_index('idx_node_metadata_graph', 'test_node_metadata', ['graph_id'])
    op.create_index('idx_node_metadata_status', 'test_node_metadata', ['test_status'])
    op.create_index('idx_node_metadata_coverage', 'test_node_metadata', ['test_coverage_percent'])

def downgrade():
    op.drop_table('test_node_metadata')
    op.drop_table('execution_artifacts')
    op.drop_table('execution_sessions')
    op.drop_table('execution_environments')
```

---

## 2. Service Implementation Examples

### 2.1 ExecutionEnvironmentService

```python
# src/tracertm/services/execution_environment_service.py
"""Service for managing test execution environments."""

import subprocess
import asyncio
import logging
from typing import Optional
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from tracertm.models.execution_environment import ExecutionEnvironment
from tracertm.repositories.execution_environment_repository import ExecutionEnvironmentRepository

logger = logging.getLogger(__name__)


class ExecutionEnvironmentService:
    """Manages execution environment creation, validation, and health checks."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ExecutionEnvironmentRepository(session)

    async def create_environment(
        self,
        project_id: str,
        name: str,
        repo_url: str,
        repo_branch: str,
        runtime: str,
        package_manager: str,
        environment_type: str = "docker",
        setup_script: Optional[str] = None,
        description: Optional[str] = None,
    ) -> ExecutionEnvironment:
        """
        Create new execution environment.

        Args:
            project_id: Project ID
            name: Environment name
            repo_url: Repository URL
            repo_branch: Branch to use (default: main)
            runtime: Runtime image (e.g., "node:20", "python:3.12")
            package_manager: Package manager (npm, pip, cargo)
            environment_type: docker | nix | local
            setup_script: Additional setup commands
            description: Optional description

        Returns:
            Created ExecutionEnvironment instance
        """
        env = ExecutionEnvironment(
            project_id=project_id,
            name=name,
            description=description,
            environment_type=environment_type,
            runtime=runtime,
            repo_url=repo_url,
            repo_branch=repo_branch,
            package_manager=package_manager,
            setup_script=setup_script,
            status="pending",  # Will update after validation
        )

        self.session.add(env)
        await self.session.flush()

        # Validate environment
        try:
            await self.health_check(env.id)
            env.status = "active"
        except Exception as e:
            env.status = "error"
            env.health_check_error = str(e)
            logger.error(f"Health check failed for environment {env.id}: {e}")

        await self.session.flush()
        return env

    async def detect_test_frameworks(
        self,
        environment_id: str,
    ) -> list[str]:
        """
        Detect test frameworks in repository.

        Checks for:
        - Jest (package.json)
        - Pytest (setup.py, pyproject.toml, pytest.ini)
        - Playwright (package.json, playwright.config.ts)
        - Cypress (cypress.config.js, cypress.config.ts)
        - Go testing (go test)
        - Rust cargo-test (Cargo.toml)
        """
        env = await self.repo.get_by_id(environment_id)
        if not env:
            raise ValueError(f"Environment {environment_id} not found")

        frameworks = []

        # Clone/fetch repository to temporary location
        temp_dir = Path(f"/tmp/detect-{environment_id}")
        temp_dir.mkdir(exist_ok=True, parents=True)

        try:
            # Clone repo
            result = await self._run_command(
                ["git", "clone", "--depth", "1", "-b", env.repo_branch, env.repo_url, str(temp_dir)],
                timeout=30,
            )

            if result.returncode != 0:
                logger.warning(f"Failed to clone {env.repo_url}: {result.stderr}")
                return frameworks

            # Check for various test frameworks
            if (temp_dir / "package.json").exists():
                frameworks.extend(await self._detect_node_frameworks(temp_dir))

            if (temp_dir / "pyproject.toml").exists() or (temp_dir / "setup.py").exists():
                frameworks.extend(await self._detect_python_frameworks(temp_dir))

            if (temp_dir / "Cargo.toml").exists():
                frameworks.append("cargo-test")

            if (temp_dir / "go.mod").exists():
                frameworks.append("go-test")

        finally:
            # Cleanup
            await self._run_command(["rm", "-rf", str(temp_dir)])

        # Update environment
        env.detected_frameworks = frameworks
        await self.session.flush()

        return frameworks

    async def _detect_node_frameworks(self, repo_path: Path) -> list[str]:
        """Detect Node.js test frameworks."""
        frameworks = []
        package_json = repo_path / "package.json"

        if not package_json.exists():
            return frameworks

        import json
        package_data = json.loads(package_json.read_text())

        deps = {
            **package_data.get("dependencies", {}),
            **package_data.get("devDependencies", {}),
        }

        if "jest" in deps:
            frameworks.append("jest")
        if "mocha" in deps:
            frameworks.append("mocha")
        if "vitest" in deps:
            frameworks.append("vitest")
        if "playwright" in deps or "@playwright/test" in deps:
            frameworks.append("playwright")
        if "cypress" in deps:
            frameworks.append("cypress")
        if "ava" in deps:
            frameworks.append("ava")

        return frameworks

    async def _detect_python_frameworks(self, repo_path: Path) -> list[str]:
        """Detect Python test frameworks."""
        frameworks = []

        # Check pyproject.toml
        pyproject = repo_path / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text()
            if "pytest" in content:
                frameworks.append("pytest")
            if "unittest" in content:
                frameworks.append("unittest")
            if "nose" in content:
                frameworks.append("nose")

        return frameworks

    async def health_check(
        self,
        environment_id: str,
    ) -> dict[str, bool]:
        """
        Verify environment is properly configured.

        Checks:
        1. Repository is accessible
        2. Runtime image/interpreter available
        3. Package manager installed
        4. Dependencies installable
        5. Test command runnable

        Returns dict with check results
        """
        env = await self.repo.get_by_id(environment_id)
        if not env:
            raise ValueError(f"Environment {environment_id} not found")

        checks = {
            "repo_accessible": False,
            "runtime_available": False,
            "package_manager_available": False,
            "dependencies_installable": False,
        }

        try:
            # Check 1: Repository accessible
            result = await self._run_command(
                ["git", "ls-remote", "--heads", env.repo_url, env.repo_branch],
                timeout=10,
            )
            checks["repo_accessible"] = result.returncode == 0

            # Check 2: Runtime available (Docker)
            if env.environment_type == "docker":
                result = await self._run_command(
                    ["docker", "pull", env.runtime],
                    timeout=60,
                )
                checks["runtime_available"] = result.returncode == 0
            else:
                checks["runtime_available"] = True  # Assume local runtime available

            # Check 3: Package manager
            pm_check_cmd = self._get_package_manager_check_cmd(env.package_manager)
            result = await self._run_command(pm_check_cmd, timeout=10)
            checks["package_manager_available"] = result.returncode == 0

            # Check 4: Dependency installation (via docker or local)
            # This would involve actually trying to install dependencies

            # Check 5: Test command
            if env.test_command:
                checks["test_runnable"] = await self._test_command(env)

            # Overall status
            if not all(checks.values()):
                errors = [k for k, v in checks.items() if not v]
                raise RuntimeError(f"Health checks failed: {', '.join(errors)}")

        except Exception as e:
            env.status = "error"
            env.health_check_error = str(e)
            await self.session.flush()
            raise

        env.status = "active"
        env.last_tested_at = datetime.utcnow()
        await self.session.flush()

        return checks

    async def _run_command(
        self,
        cmd: list[str],
        timeout: int = 30,
    ) -> subprocess.CompletedProcess:
        """Run command with timeout and capture output."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {' '.join(cmd)}")
            raise

    def _get_package_manager_check_cmd(self, pm: str) -> list[str]:
        """Get command to check if package manager is available."""
        commands = {
            "npm": ["npm", "--version"],
            "pip": ["pip", "--version"],
            "cargo": ["cargo", "--version"],
            "go": ["go", "version"],
            "yarn": ["yarn", "--version"],
            "pnpm": ["pnpm", "--version"],
        }
        return commands.get(pm, ["which", pm])

    async def _test_command(self, env: ExecutionEnvironment) -> bool:
        """Test if test command would work."""
        # This would involve spinning up a container and testing
        # Simplified version shown here
        return True
```

### 2.2 ExecutionSessionService

```python
# src/tracertm/services/execution_session_service.py
"""Service for managing test execution sessions."""

import asyncio
import logging
from typing import Optional, AsyncGenerator
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.execution_session import ExecutionSession, ExecutionSessionStatus
from tracertm.models.test_run import TestRun
from tracertm.repositories.execution_session_repository import ExecutionSessionRepository
from tracertm.services.docker_test_runner import DockerTestRunner

logger = logging.getLogger(__name__)


class ExecutionSessionService:
    """Manages test execution sessions and orchestration."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ExecutionSessionRepository(session)
        self.runner = DockerTestRunner()

    async def create_session(
        self,
        environment_id: str,
        test_run_id: str,
        git_commit_sha: Optional[str] = None,
        git_branch: Optional[str] = None,
    ) -> ExecutionSession:
        """Create new execution session."""
        session = ExecutionSession(
            environment_id=environment_id,
            test_run_id=test_run_id,
            status=ExecutionSessionStatus.PENDING,
            git_commit_sha=git_commit_sha,
            git_branch=git_branch,
        )

        self.session.add(session)
        await self.session.flush()

        logger.info(
            f"Created execution session {session.id}",
            extra={
                'session_id': session.id,
                'environment_id': environment_id,
                'test_run_id': test_run_id,
            }
        )

        return session

    async def start_execution(
        self,
        session_id: str,
        test_suite_id: Optional[str] = None,
        test_case_ids: Optional[list[str]] = None,
    ) -> asyncio.Task:
        """
        Start test execution (returns async task).

        Can execute:
        - Entire test suite
        - Specific test cases
        - Based on test_run configuration
        """
        session = await self.repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Create task for execution
        task = asyncio.create_task(
            self._execute_tests(session, test_suite_id, test_case_ids)
        )

        return task

    async def _execute_tests(
        self,
        session: ExecutionSession,
        test_suite_id: Optional[str],
        test_case_ids: Optional[list[str]],
    ) -> None:
        """Execute tests and update session with results."""
        try:
            session.status = ExecutionSessionStatus.PROVISIONING
            session.started_at = datetime.utcnow()
            await self.session.flush()

            # 1. Provision container
            container_id = await self.runner.provision_container(
                environment_id=session.environment_id,
                session_id=session.id,
            )
            session.container_id = container_id
            session.status = ExecutionSessionStatus.RUNNING
            await self.session.flush()

            # 2. Execute tests
            results = await self.runner.execute_tests(
                container_id=container_id,
                session_id=session.id,
                test_suite_id=test_suite_id,
                test_case_ids=test_case_ids,
            )

            # 3. Update session with results
            session.tests_executed = results['total']
            session.tests_passed = results['passed']
            session.tests_failed = results['failed']
            session.test_coverage_percent = results.get('coverage_percent')
            session.status = ExecutionSessionStatus.COMPLETED
            session.completed_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)
            session.status = ExecutionSessionStatus.FAILED
            session.error_message = str(e)
            session.completed_at = datetime.utcnow()

        finally:
            # Cleanup
            if session.container_id:
                await self.runner.cleanup_container(session.container_id)

            await self.session.flush()

    async def get_execution_status(
        self,
        session_id: str,
    ) -> dict[str, any]:
        """Get real-time execution status."""
        session = await self.repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return {
            "session_id": session.id,
            "status": session.status.value,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "tests_executed": session.tests_executed,
            "tests_passed": session.tests_passed,
            "tests_failed": session.tests_failed,
            "test_coverage_percent": session.test_coverage_percent,
            "container_id": session.container_id,
            "error_message": session.error_message,
        }

    async def stream_execution_logs(
        self,
        session_id: str,
    ) -> AsyncGenerator[str, None]:
        """Stream execution logs in real-time."""
        session = await self.repo.get_by_id(session_id)
        if not session or not session.container_id:
            raise ValueError(f"Session {session_id} not found or not running")

        # Stream logs from Docker container
        async for line in self.runner.stream_logs(session.container_id):
            yield line

    async def cancel_execution(self, session_id: str) -> bool:
        """Cancel running execution."""
        session = await self.repo.get_by_id(session_id)
        if not session:
            return False

        if session.container_id:
            await self.runner.cleanup_container(session.container_id)

        session.status = ExecutionSessionStatus.CANCELLED
        session.completed_at = datetime.utcnow()
        await self.session.flush()

        return True
```

---

## 3. API Endpoint Examples

### 3.1 Test Execution Endpoints

```python
# src/tracertm/api/routes/execution.py
"""API endpoints for test execution."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from tracertm.services.execution_session_service import ExecutionSessionService
from tracertm.services.test_environment_orchestrator import TestEnvironmentOrchestrator
from tracertm.database.connection import get_session

router = APIRouter(prefix="/api/projects/{projectId}/execution", tags=["execution"])


class ExecuteTestSuiteRequest(BaseModel):
    """Request to execute a test suite."""
    test_suite_id: str
    environment_id: Optional[str] = None
    git_commit_sha: Optional[str] = None
    git_branch: Optional[str] = None
    github_pr_id: Optional[int] = None


@router.post("/test-suites/{testSuiteId}/execute")
async def execute_test_suite(
    project_id: str,
    test_suite_id: str,
    request: ExecuteTestSuiteRequest,
    background_tasks: BackgroundTasks,
):
    """Trigger execution of a test suite."""
    try:
        async with get_session() as session:
            orchestrator = TestEnvironmentOrchestrator(session)

            execution_session = await orchestrator.execute_test_suite(
                test_suite_id=test_suite_id,
                environment_id=request.environment_id,
                git_commit_sha=request.git_commit_sha,
                git_branch=request.git_branch,
                github_pr_id=request.github_pr_id,
            )

            # Start execution in background
            background_tasks.add_task(
                orchestrator.monitor_and_post_results,
                execution_session.id,
            )

            return {
                "session_id": execution_session.id,
                "status": execution_session.status.value,
                "message": "Test execution started",
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{sessionId}/status")
async def get_session_status(project_id: str, session_id: str):
    """Get execution session status."""
    try:
        async with get_session() as session:
            service = ExecutionSessionService(session)
            status = await service.get_execution_status(session_id)
            return status
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.websocket("/sessions/{sessionId}/logs")
async def stream_session_logs(websocket, project_id: str, session_id: str):
    """Stream execution logs via WebSocket."""
    await websocket.accept()

    try:
        async with get_session() as session:
            service = ExecutionSessionService(session)

            async for line in service.stream_execution_logs(session_id):
                await websocket.send_text(line)

    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()


@router.post("/sessions/{sessionId}/cancel")
async def cancel_execution(project_id: str, session_id: str):
    """Cancel running test execution."""
    try:
        async with get_session() as session:
            service = ExecutionSessionService(session)
            success = await service.cancel_execution(session_id)

            if success:
                return {"message": "Execution cancelled"}
            else:
                raise HTTPException(status_code=404, detail="Session not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 4. Frontend Component Examples

### 4.1 Execution Control Panel

```typescript
// frontend/apps/web/src/components/execution/ExecutionControlPanel.tsx
import { useState } from 'react';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import { Badge } from '@tracertm/ui/components/Badge';
import { Progress } from '@tracertm/ui/components/Progress';
import { Play, Square, RotateCcw } from 'lucide-react';

interface ExecutionControlPanelProps {
  testSuiteId: string;
  projectId: string;
  onExecutionStart: (sessionId: string) => void;
}

export function ExecutionControlPanel({
  testSuiteId,
  projectId,
  onExecutionStart,
}: ExecutionControlPanelProps) {
  const [isExecuting, setIsExecuting] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);

  const handleExecute = async () => {
    try {
      setIsExecuting(true);
      setProgress(0);
      setLogs([]);

      const response = await fetch(
        `/api/projects/${projectId}/execution/test-suites/${testSuiteId}/execute`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            environment_id: 'default',
          }),
        }
      );

      const data = await response.json();
      setSessionId(data.session_id);
      onExecutionStart(data.session_id);

      // Open WebSocket for streaming logs
      const ws = new WebSocket(
        `ws://localhost:3000/api/projects/${projectId}/execution/sessions/${data.session_id}/logs`
      );

      ws.onmessage = (event) => {
        setLogs((prev) => [...prev, event.data]);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      // Poll for status
      const statusInterval = setInterval(async () => {
        const statusResponse = await fetch(
          `/api/projects/${projectId}/execution/sessions/${data.session_id}/status`
        );
        const status = await statusResponse.json();

        if (status.tests_executed > 0) {
          setProgress(
            (status.tests_passed / status.tests_executed) * 100
          );
        }

        if (
          status.status === 'completed' ||
          status.status === 'failed'
        ) {
          clearInterval(statusInterval);
          setIsExecuting(false);
        }
      }, 2000);

    } catch (error) {
      console.error('Execution failed:', error);
      setIsExecuting(false);
    }
  };

  const handleCancel = async () => {
    if (!sessionId) return;

    try {
      await fetch(
        `/api/projects/${projectId}/execution/sessions/${sessionId}/cancel`,
        { method: 'POST' }
      );
      setIsExecuting(false);
    } catch (error) {
      console.error('Cancel failed:', error);
    }
  };

  return (
    <Card className="p-6">
      <div className="space-y-4">
        {/* Control Buttons */}
        <div className="flex gap-2">
          <Button
            onClick={handleExecute}
            disabled={isExecuting}
            className="gap-2"
          >
            <Play className="w-4 h-4" />
            {isExecuting ? 'Running...' : 'Execute Tests'}
          </Button>

          {isExecuting && (
            <Button
              onClick={handleCancel}
              variant="destructive"
              className="gap-2"
            >
              <Square className="w-4 h-4" />
              Cancel
            </Button>
          )}
        </div>

        {/* Progress */}
        {isExecuting && (
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm font-medium">Progress</span>
              <span className="text-sm text-gray-600">
                {Math.round(progress)}%
              </span>
            </div>
            <Progress value={progress} />
          </div>
        )}

        {/* Logs */}
        {logs.length > 0 && (
          <div className="mt-4">
            <h3 className="text-sm font-semibold mb-2">Execution Log</h3>
            <div className="bg-gray-900 text-white p-3 rounded font-mono text-xs max-h-64 overflow-y-auto">
              {logs.slice(-20).map((log, i) => (
                <div key={i}>{log}</div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
```

### 4.2 Artifact Viewer with Gallery

```typescript
// frontend/apps/web/src/components/execution/ArtifactGallery.tsx
import { useState } from 'react';
import { ChevronLeft, ChevronRight, Download, ZoomIn } from 'lucide-react';
import { Button } from '@tracertm/ui/components/Button';

interface Artifact {
  id: string;
  artifact_name: string;
  artifact_type: 'screenshot' | 'video' | 'log';
  storage_path: string;
  captured_at: string;
  test_step_index?: number;
}

interface ArtifactGalleryProps {
  artifacts: Artifact[];
}

export function ArtifactGallery({ artifacts }: ArtifactGalleryProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [zoomLevel, setZoomLevel] = useState(100);

  const current = artifacts[currentIndex];

  if (!current) {
    return <div className="text-center text-gray-500">No artifacts</div>;
  }

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev === 0 ? artifacts.length - 1 : prev - 1));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev === artifacts.length - 1 ? 0 : prev + 1));
  };

  const handleDownload = () => {
    window.open(`/api/artifacts/${current.id}/download`, '_blank');
  };

  const handleZoomIn = () => {
    setZoomLevel((prev) => Math.min(prev + 25, 200));
  };

  return (
    <div className="space-y-4">
      {/* Main Display */}
      <div className="relative bg-gray-100 rounded-lg overflow-hidden">
        <div
          className="flex items-center justify-center overflow-auto"
          style={{
            maxHeight: '500px',
            backgroundColor: '#f3f4f6',
          }}
        >
          {current.artifact_type === 'screenshot' && (
            <img
              src={`/api/artifacts/${current.id}/view`}
              alt={current.artifact_name}
              style={{
                maxWidth: '100%',
                maxHeight: '500px',
                transform: `scale(${zoomLevel / 100})`,
              }}
            />
          )}
          {current.artifact_type === 'video' && (
            <video
              src={`/api/artifacts/${current.id}/view`}
              controls
              style={{ maxWidth: '100%', maxHeight: '500px' }}
            />
          )}
        </div>

        {/* Controls */}
        <div className="absolute top-2 right-2 flex gap-2">
          {current.artifact_type === 'screenshot' && (
            <Button
              size="sm"
              variant="outline"
              onClick={handleZoomIn}
              title="Zoom in"
            >
              <ZoomIn className="w-4 h-4" />
            </Button>
          )}
          <Button
            size="sm"
            variant="outline"
            onClick={handleDownload}
            title="Download"
          >
            <Download className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Metadata */}
      <div className="text-sm text-gray-600 space-y-1">
        <p>
          <strong>Captured:</strong>{' '}
          {new Date(current.captured_at).toLocaleString()}
        </p>
        {current.test_step_index !== undefined && (
          <p>
            <strong>Test Step:</strong> {current.test_step_index}
          </p>
        )}
      </div>

      {/* Thumbnail Strip */}
      {artifacts.length > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-2">
          {artifacts.map((artifact, idx) => (
            <button
              key={artifact.id}
              onClick={() => setCurrentIndex(idx)}
              className={`flex-shrink-0 transition-all ${
                currentIndex === idx ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              <img
                src={`/api/artifacts/${artifact.id}/preview?size=64`}
                alt={artifact.artifact_name}
                className="w-16 h-16 object-cover rounded"
              />
            </button>
          ))}
        </div>
      )}

      {/* Navigation */}
      {artifacts.length > 1 && (
        <div className="flex items-center justify-between pt-2">
          <Button size="sm" variant="outline" onClick={handlePrevious}>
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <span className="text-sm text-gray-600">
            {currentIndex + 1} / {artifacts.length}
          </span>
          <Button size="sm" variant="outline" onClick={handleNext}>
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
```

---

## 5. GitHub Integration Code Example

### 5.1 Webhook Handler

```python
# src/tracertm/services/github_webhook_handler.py
"""Handle GitHub webhooks for test triggering."""

import hmac
import hashlib
import logging
from typing import Optional

from tracertm.services.execution_session_service import ExecutionSessionService
from tracertm.services.test_environment_orchestrator import TestEnvironmentOrchestrator
from tracertm.services.github_check_runs_service import GitHubCheckRunsService

logger = logging.getLogger(__name__)


class GitHubWebhookHandler:
    """Process GitHub webhooks and trigger test execution."""

    def __init__(self, session):
        self.session = session
        self.orchestrator = TestEnvironmentOrchestrator(session)
        self.github_service = GitHubCheckRunsService(session)

    async def handle_push_event(self, payload: dict) -> dict:
        """Handle GitHub push event."""
        repo = payload['repository']
        branch = payload['ref'].split('/')[-1]
        commit_sha = payload['after']

        logger.info(
            f"Push event received",
            extra={
                'repo': repo['full_name'],
                'branch': branch,
                'commit_sha': commit_sha,
            }
        )

        # Find mapping for this repo
        mapping = await self._find_mapping(repo['full_name'], branch)
        if not mapping:
            logger.info(f"No mapping found for {repo['full_name']}")
            return {"success": False, "message": "No integration mapping"}

        # Execute tests
        try:
            session = await self.orchestrator.execute_test_suite(
                test_suite_id=mapping.test_suite_id,
                environment_id=mapping.environment_id,
                git_commit_sha=commit_sha,
                git_branch=branch,
            )

            return {
                "success": True,
                "session_id": session.id,
                "status": "started",
            }

        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    async def handle_pull_request_event(self, payload: dict) -> dict:
        """Handle GitHub pull request event."""
        action = payload['action']

        if action not in ['opened', 'synchronize', 'reopened']:
            logger.info(f"Ignoring PR action: {action}")
            return {"success": True, "message": f"Action {action} ignored"}

        pr = payload['pull_request']
        repo = payload['repository']

        logger.info(
            f"PR event received",
            extra={
                'repo': repo['full_name'],
                'pr_number': pr['number'],
                'commit_sha': pr['head']['sha'],
            }
        )

        # Similar to push, but with GitHub callback
        mapping = await self._find_mapping(repo['full_name'], pr['head']['ref'])
        if not mapping:
            return {"success": False, "message": "No integration mapping"}

        try:
            session = await self.orchestrator.execute_test_suite(
                test_suite_id=mapping.test_suite_id,
                environment_id=mapping.environment_id,
                git_commit_sha=pr['head']['sha'],
                git_branch=pr['head']['ref'],
                github_pr_id=pr['number'],
                github_repo=repo['full_name'],
            )

            # Schedule result posting
            import asyncio
            asyncio.create_task(
                self._post_results_to_github(session, pr, repo, mapping)
            )

            return {
                "success": True,
                "session_id": session.id,
                "status": "started",
            }

        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def _post_results_to_github(
        self,
        session,
        pr: dict,
        repo: dict,
        mapping,
    ) -> None:
        """Post test results to GitHub PR."""
        # Wait for execution to complete
        max_waits = 600  # 10 minutes
        wait_count = 0

        while session.status in ['pending', 'provisioning', 'running']:
            if wait_count >= max_waits:
                logger.error(f"Execution timeout for session {session.id}")
                break

            await asyncio.sleep(1)
            wait_count += 1

            # Refresh session
            session = await self.session.get(session.id)

        # Post check run
        try:
            await self.github_service.update_check_run(
                session,
                status='completed',
                conclusion='success' if session.tests_failed == 0 else 'failure',
            )

            # Post comment
            await self.github_service.post_test_results_comment(
                session,
                mapping=mapping,
                pr_number=pr['number'],
            )

        except Exception as e:
            logger.error(f"Failed to post results: {e}", exc_info=True)

    @staticmethod
    def verify_signature(
        payload: bytes,
        signature: str,
        secret: str,
    ) -> bool:
        """Verify GitHub webhook signature."""
        expected = 'sha256=' + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)
```

---

## 6. Testing Examples

### 6.1 Unit Test

```python
# tests/unit/services/test_execution_environment_service.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from tracertm.services.execution_environment_service import ExecutionEnvironmentService
from tracertm.models.execution_environment import ExecutionEnvironment


@pytest.fixture
async def service(async_session):
    """Create service instance."""
    return ExecutionEnvironmentService(async_session)


@pytest.mark.asyncio
async def test_create_environment_success(service):
    """Test environment creation."""
    env = await service.create_environment(
        project_id="proj-1",
        name="Test Environment",
        repo_url="https://github.com/example/repo.git",
        repo_branch="main",
        runtime="node:20",
        package_manager="npm",
    )

    assert env.id is not None
    assert env.project_id == "proj-1"
    assert env.name == "Test Environment"
    assert env.status in ["active", "error"]


@pytest.mark.asyncio
async def test_detect_frameworks_detects_jest(service, tmp_path):
    """Test Jest detection."""
    # Create fake package.json
    pkg_json = tmp_path / "package.json"
    pkg_json.write_text('{"devDependencies": {"jest": "^29.0.0"}}')

    frameworks = await service._detect_node_frameworks(tmp_path)

    assert "jest" in frameworks


@pytest.mark.asyncio
async def test_health_check_fails_on_missing_repo(service):
    """Test health check fails for missing repo."""
    env = ExecutionEnvironment(
        project_id="proj-1",
        name="Test",
        environment_type="docker",
        runtime="node:20",
        repo_url="https://github.com/nonexistent/repo.git",
        repo_branch="main",
        package_manager="npm",
    )

    with pytest.raises(Exception):
        await service.health_check(env.id)
```

### 6.2 Integration Test

```python
# tests/integration/test_execution_end_to_end.py
@pytest.mark.asyncio
async def test_execute_test_suite_end_to_end(
    async_session,
    mock_docker_client,
    test_project,
    test_suite,
):
    """Test full execution flow."""
    # Setup
    orchestrator = TestEnvironmentOrchestrator(async_session)

    environment = await orchestrator.create_environment(
        project_id=test_project.id,
        repo_url="https://github.com/example/test-repo.git",
        runtime="node:20",
        package_manager="npm",
    )

    # Execute
    session = await orchestrator.execute_test_suite(
        test_suite_id=test_suite.id,
        environment_id=environment.id,
    )

    # Verify
    assert session.status == ExecutionSessionStatus.COMPLETED or ExecutionSessionStatus.FAILED
    assert session.tests_executed > 0
    assert session.container_id is not None
```

---

## 7. Configuration Reference

### 7.1 Environment Variables

```bash
# Execution Service Configuration
EXECUTION_ENVIRONMENT_TYPE=docker  # docker, nix, local
DOCKER_HOST=unix:///var/run/docker.sock
DEFAULT_CONTAINER_TIMEOUT_SECONDS=3600
DEFAULT_MEMORY_LIMIT_MB=2048
DEFAULT_CPU_LIMIT=2

# Artifact Storage
ARTIFACT_STORAGE_BACKEND=s3  # s3, local, gcs
ARTIFACT_S3_BUCKET=tracertm-artifacts
ARTIFACT_S3_REGION=us-east-1
ARTIFACT_STORAGE_PATH=/var/tracertm/artifacts  # For local storage

# GitHub Integration
GITHUB_APP_ID=1234567
GITHUB_APP_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----...
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Artifact Retention
ARTIFACT_RETENTION_DAYS=90
ARTIFACT_MAX_SIZE_MB=1000
```

---

This technical specification provides the implementation details needed to build the QA execution system. It covers database schemas, services, API endpoints, frontend components, and testing strategies.
