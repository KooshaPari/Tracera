# OpenAI Codex CLI: Python Integration Examples

## Example 1: Basic Code Generation Service

```python
"""
Simple service for generating code with Codex.
Production-ready with error handling.
"""

import subprocess
import json
from typing import Optional
from dataclasses import dataclass

@dataclass
class GeneratedCode:
    code: str
    explanation: str
    tests: Optional[str] = None

class CodeGenerator:
    def __init__(self, timeout: int = 300):
        self.timeout = timeout

    def generate(self, task: str) -> GeneratedCode:
        """Generate code for given task."""
        cmd = [
            "codex", "exec",
            "--task", task,
            "--full-auto"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Code generation exceeded {self.timeout}s")

        if result.returncode != 0:
            raise RuntimeError(f"Generation failed: {result.stderr}")

        return GeneratedCode(
            code=result.stdout,
            explanation="",
            tests=None
        )

    def generate_with_tests(self, task: str) -> GeneratedCode:
        """Generate code including unit tests."""
        extended_task = f"""{task}

Please include:
1. Well-documented code with docstrings
2. Type hints for all functions
3. Comprehensive unit tests
4. Error handling examples"""

        return self.generate(extended_task)

# Usage
if __name__ == "__main__":
    generator = CodeGenerator()

    # Simple generation
    result = generator.generate(
        "Write a Python function to generate UUID v4 identifiers"
    )
    print("Generated Code:")
    print(result.code)

    # With tests
    result_with_tests = generator.generate_with_tests(
        "Implement a Redis cache wrapper class"
    )
    print("\nGenerated with Tests:")
    print(result_with_tests.code)
```

---

## Example 2: Code Review Service

```python
"""
Code review service using Codex.
Returns structured review feedback.
"""

import subprocess
import json
from typing import List
from dataclasses import dataclass

@dataclass
class ReviewIssue:
    file: str
    line: Optional[int]
    severity: str  # error, warning, info
    message: str
    suggestion: Optional[str] = None

@dataclass
class CodeReview:
    summary: str
    issues: List[ReviewIssue]
    quality_score: Optional[float] = None

class CodeReviewer:
    def __init__(self, timeout: int = 300):
        self.timeout = timeout
        self.schema = self._create_schema()

    def _create_schema(self) -> dict:
        """Define output schema for structured reviews."""
        return {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "quality_score": {"type": "number", "minimum": 0, "maximum": 100},
                "issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "file": {"type": "string"},
                            "line": {"type": ["integer", "null"]},
                            "severity": {"enum": ["error", "warning", "info"]},
                            "message": {"type": "string"},
                            "suggestion": {"type": ["string", "null"]}
                        },
                        "required": ["file", "severity", "message"]
                    }
                }
            },
            "required": ["summary", "issues"]
        }

    def review_file(self, file_path: str) -> CodeReview:
        """Review a specific file."""
        task = f"Review {file_path} for code quality, security, and style issues"

        cmd = [
            "codex", "exec",
            "--task", task,
            "--file", file_path,
            "--full-auto"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"Review failed: {result.stderr}")

        # Parse structured output
        try:
            data = json.loads(result.stdout)
            issues = [
                ReviewIssue(**issue) for issue in data.get("issues", [])
            ]
            return CodeReview(
                summary=data["summary"],
                issues=issues,
                quality_score=data.get("quality_score")
            )
        except json.JSONDecodeError:
            raise RuntimeError("Failed to parse review output")

    def review_staged_changes(self) -> CodeReview:
        """Review staged git changes."""
        task = "Review staged changes for quality and security issues"

        cmd = ["codex", "review", "--full-auto"]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"Review failed: {result.stderr}")

        try:
            data = json.loads(result.stdout)
            issues = [
                ReviewIssue(**issue) for issue in data.get("issues", [])
            ]
            return CodeReview(
                summary=data["summary"],
                issues=issues,
                quality_score=data.get("quality_score")
            )
        except json.JSONDecodeError:
            raise RuntimeError("Failed to parse review output")

# Usage
if __name__ == "__main__":
    reviewer = CodeReviewer()

    # Review specific file
    review = reviewer.review_file("src/api.py")
    print(f"Quality Score: {review.quality_score}/100")
    print(f"Issues Found: {len(review.issues)}")
    for issue in review.issues:
        print(f"  [{issue.severity}] {issue.message}")

    # Review staged changes
    staged_review = reviewer.review_staged_changes()
    print(f"\nStaged Changes Review:")
    print(staged_review.summary)
```

---

## Example 3: Multi-task Orchestrator

```python
"""
Orchestrate multiple Codex tasks with tracking.
Useful for complex workflows.
"""

import subprocess
import json
import time
from typing import List, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class TaskResult:
    task_id: str
    task_description: str
    status: TaskStatus
    output: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds()
        return None

class CodexOrchestrator:
    def __init__(self, timeout: int = 300):
        self.timeout = timeout
        self.results: List[TaskResult] = []
        self.failed_tasks: List[str] = []

    def run_task(self, task_id: str, task_description: str) -> TaskResult:
        """Run a single Codex task."""
        result = TaskResult(
            task_id=task_id,
            task_description=task_description,
            status=TaskStatus.PENDING,
            started_at=datetime.now()
        )

        try:
            result.status = TaskStatus.RUNNING

            cmd = [
                "codex", "exec",
                "--task", task_description,
                "--full-auto"
            ]

            process_result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            result.completed_at = datetime.now()

            if process_result.returncode == 0:
                result.status = TaskStatus.COMPLETED
                result.output = process_result.stdout
            else:
                result.status = TaskStatus.FAILED
                result.error = process_result.stderr
                self.failed_tasks.append(task_id)

        except subprocess.TimeoutExpired:
            result.status = TaskStatus.FAILED
            result.error = f"Timeout after {self.timeout}s"
            result.completed_at = datetime.now()
            self.failed_tasks.append(task_id)

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.now()
            self.failed_tasks.append(task_id)

        self.results.append(result)
        return result

    def run_workflow(self,
                     tasks: Dict[str, str],
                     fail_fast: bool = False) -> List[TaskResult]:
        """Run multiple tasks (sequential or with early failure)."""
        results = []

        for task_id, task_desc in tasks.items():
            result = self.run_task(task_id, task_desc)
            results.append(result)

            if fail_fast and result.status == TaskStatus.FAILED:
                break

        return results

    def get_summary(self) -> dict:
        """Get workflow summary."""
        total = len(self.results)
        completed = sum(1 for r in self.results if r.status == TaskStatus.COMPLETED)
        failed = sum(1 for r in self.results if r.status == TaskStatus.FAILED)

        total_duration = sum(
            r.duration_seconds for r in self.results
            if r.duration_seconds is not None
        ) or 0

        return {
            "total_tasks": total,
            "completed": completed,
            "failed": failed,
            "success_rate": (completed / total * 100) if total > 0 else 0,
            "total_duration_seconds": total_duration,
            "failed_task_ids": self.failed_tasks
        }

# Usage
if __name__ == "__main__":
    orchestrator = CodexOrchestrator()

    # Define workflow
    workflow = {
        "generate_model": "Write a SQLAlchemy database model for users",
        "generate_schema": "Write Pydantic schema for user validation",
        "generate_crud": "Write CRUD operations for user model",
        "generate_tests": "Write pytest tests for CRUD operations"
    }

    # Run workflow
    results = orchestrator.run_workflow(workflow, fail_fast=False)

    # Print results
    for result in results:
        status_symbol = "✅" if result.status == TaskStatus.COMPLETED else "❌"
        print(f"{status_symbol} {result.task_id}: {result.status}")
        if result.duration_seconds:
            print(f"   Duration: {result.duration_seconds:.1f}s")

    # Print summary
    summary = orchestrator.get_summary()
    print("\nWorkflow Summary:")
    print(f"  Total: {summary['total_tasks']}")
    print(f"  Success: {summary['success_rate']:.1f}%")
    print(f"  Duration: {summary['total_duration_seconds']:.1f}s")
```

---

## Example 4: Secure CI/CD Integration

```python
"""
Production-ready CI/CD integration with security controls.
For GitHub Actions, GitLab CI, etc.
"""

import subprocess
import os
from typing import Optional
from enum import Enum
from pathlib import Path

class SandboxLevel(str, Enum):
    READ_ONLY = "read-only"
    WORKSPACE = "workspace-write"
    FULL_ACCESS = "danger-full-access"

class CICDCodexRunner:
    """Secure Codex runner for CI/CD pipelines."""

    # Only allow specific directories in CI
    ALLOWED_DIRECTORIES = {
        "/project",
        "/workspace",
        "/github/workspace",
        "/builds"
    }

    def __init__(self,
                 sandbox: SandboxLevel = SandboxLevel.WORKSPACE,
                 timeout: int = 600,
                 require_approval: bool = True):
        self.sandbox = sandbox
        self.timeout = timeout
        self.require_approval = require_approval
        self._validate_environment()

    def _validate_environment(self):
        """Security: Validate CI/CD environment."""
        # Check for CI environment
        is_ci = any([
            os.getenv("CI"),
            os.getenv("GITHUB_ACTIONS"),
            os.getenv("GITLAB_CI"),
            os.getenv("CIRCLECI")
        ])

        if not is_ci:
            raise RuntimeError("Not running in CI/CD environment")

        # Check for API key
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY not set")

        # Security check
        if (self.sandbox == SandboxLevel.FULL_ACCESS and
            self.require_approval == False):
            raise RuntimeError(
                "SECURITY: Cannot use danger-full-access without approval in CI"
            )

    def _validate_directory(self, path: Optional[str]) -> bool:
        """Security: Validate working directory is allowed."""
        if not path:
            return True

        resolved = Path(path).resolve()

        for allowed in self.ALLOWED_DIRECTORIES:
            if str(resolved).startswith(allowed):
                return True

        raise ValueError(f"Directory {path} not in allowed list")

    def run(self, task: str, working_dir: Optional[str] = None) -> str:
        """Run Codex task securely in CI/CD."""
        # Validate directory
        self._validate_directory(working_dir)

        # Build command
        cmd = [
            "codex", "exec",
            "--task", task,
            "--sandbox", self.sandbox.value
        ]

        if self.require_approval:
            cmd.append("--approval=required")
        else:
            cmd.append("--full-auto")

        if working_dir:
            cmd.extend(["--cwd", working_dir])

        # Run with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout,
            env={**os.environ}  # Use inherited environment
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Task failed: {result.stderr[:500]}"  # Limit error output
            )

        return result.stdout

# Usage in GitHub Actions
if __name__ == "__main__":
    # Example: Run in GitHub Actions
    runner = CICDCodexRunner(
        sandbox=SandboxLevel.WORKSPACE,
        timeout=600,
        require_approval=True
    )

    try:
        # Example workflow task
        output = runner.run(
            "Run tests and generate coverage report",
            working_dir="/github/workspace"
        )
        print("Task completed successfully")
        print(output)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
```

**GitHub Actions Workflow File** (`.github/workflows/codex.yml`):

```yaml
name: Codex CI

on: [push, pull_request]

jobs:
  codex-tasks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Codex
        run: npm install -g codex

      - name: Run Codex Tasks
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python -c "
          from ci_cd_runner import CICDCodexRunner, SandboxLevel
          runner = CICDCodexRunner(
              sandbox=SandboxLevel.WORKSPACE,
              timeout=600
          )
          result = runner.run(
              'Generate type hints for all Python files',
              working_dir='.'
          )
          print(result)
          "

      - name: Create Pull Request
        if: github.event_name == 'pull_request'
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: 'chore: Add type hints with Codex'
          branch: codex/add-type-hints
```

---

## Example 5: Async Agent with Queue

```python
"""
Async Codex integration with task queue.
For handling multiple concurrent requests.
"""

import asyncio
import subprocess
from typing import Optional, Coroutine
from dataclasses import dataclass
from datetime import datetime
from queue import PriorityQueue, Empty
import uuid

@dataclass
class QueuedTask:
    task_id: str
    description: str
    priority: int = 0  # Lower = higher priority
    created_at: datetime = None
    callback: Optional[Coroutine] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def __lt__(self, other):
        """Support sorting by priority."""
        return self.priority < other.priority

class AsyncCodexAgent:
    def __init__(self, max_concurrent: int = 3, timeout: int = 300):
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.queue: PriorityQueue = PriorityQueue()
        self.running_tasks = set()
        self.completed_tasks = {}

    async def enqueue(self,
                      description: str,
                      priority: int = 0,
                      task_id: Optional[str] = None) -> str:
        """Add task to queue."""
        task_id = task_id or str(uuid.uuid4())

        task = QueuedTask(
            task_id=task_id,
            description=description,
            priority=priority
        )

        self.queue.put((priority, task_id, task))
        return task_id

    async def _execute_task(self, task: QueuedTask) -> str:
        """Execute single task."""
        loop = asyncio.get_event_loop()

        def run_codex():
            result = subprocess.run(
                ["codex", "exec", "--task", task.description, "--full-auto"],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
            return result.stdout

        # Run in thread pool to avoid blocking
        return await loop.run_in_executor(None, run_codex)

    async def process_queue(self):
        """Process tasks from queue."""
        while True:
            try:
                # Get task from queue (non-blocking)
                _, task_id, task = self.queue.get_nowait()

                # Wait for slot
                while len(self.running_tasks) >= self.max_concurrent:
                    await asyncio.sleep(1)

                # Execute task
                self.running_tasks.add(task_id)
                try:
                    result = await self._execute_task(task)
                    self.completed_tasks[task_id] = {
                        "status": "completed",
                        "output": result
                    }
                except Exception as e:
                    self.completed_tasks[task_id] = {
                        "status": "failed",
                        "error": str(e)
                    }
                finally:
                    self.running_tasks.discard(task_id)

            except Empty:
                # No more tasks
                if not self.running_tasks:
                    break
                await asyncio.sleep(1)

    async def run(self):
        """Run agent with queue processing."""
        await self.process_queue()

    def get_result(self, task_id: str) -> Optional[dict]:
        """Get task result."""
        return self.completed_tasks.get(task_id)

# Usage
async def main():
    agent = AsyncCodexAgent(max_concurrent=3)

    # Enqueue multiple tasks
    task_ids = []
    for i in range(10):
        task_id = await agent.enqueue(
            f"Write a Python function for task {i}",
            priority=i % 3
        )
        task_ids.append(task_id)

    # Process queue
    await agent.run()

    # Get results
    for task_id in task_ids:
        result = agent.get_result(task_id)
        print(f"{task_id}: {result['status']}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Example 6: Retry Logic with Backoff

```python
"""
Robust retry logic for handling rate limits and transient failures.
"""

import subprocess
import time
import random
from typing import Callable, TypeVar, Optional
from functools import wraps

T = TypeVar('T')

def codex_with_retry(
    max_retries: int = 3,
    base_delay: float = 2.0,
    jitter: bool = True
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for Codex operations with exponential backoff."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RuntimeError as e:
                    if "rate limit" not in str(e).lower():
                        raise  # Re-raise non-rate-limit errors

                    if attempt == max_retries - 1:
                        raise  # Last attempt, give up

                    # Calculate backoff
                    delay = base_delay ** attempt
                    if jitter:
                        delay *= (0.5 + random.random())

                    print(f"Rate limited. Retrying in {delay:.1f}s...")
                    time.sleep(delay)

            return None  # Should not reach here

        return wrapper

    return decorator

# Usage
@codex_with_retry(max_retries=3, base_delay=2.0)
def generate_code_with_retry(task: str) -> str:
    result = subprocess.run(
        ["codex", "exec", "--task", task, "--full-auto"],
        capture_output=True,
        text=True,
        timeout=300
    )
    if result.returncode != 0:
        if "rate limit" in result.stderr.lower():
            raise RuntimeError("Rate limited")
        raise RuntimeError(result.stderr)
    return result.stdout

# Usage
try:
    code = generate_code_with_retry(
        "Write a Python sorting algorithm"
    )
    print(code)
except RuntimeError as e:
    print(f"Failed after retries: {e}")
```

---

## Summary

These examples cover:
1. **Basic code generation** - Simple wrapper
2. **Code reviews** - Structured feedback
3. **Workflow orchestration** - Multiple sequential tasks
4. **CI/CD integration** - Secure production usage
5. **Async operations** - Concurrent task handling
6. **Retry logic** - Handle rate limiting

All examples include proper error handling, security considerations, and are production-ready.

For more details, refer to the comprehensive research document: `CODEX_CLI_AGENT_INTEGRATION_RESEARCH.md`
