# Migration Code Examples: Before & After

**Purpose:** Concrete examples showing how to migrate from crun custom implementations to pheno-sdk shared libraries.

---

## 1. Error Handling

### Before: Custom Exceptions

```python
# crun/shared/exceptions.py
class CrunError(Exception):
    """Base exception for crun."""
    def __init__(self, message: str, context: dict = None):
        self.message = message
        self.context = context or {}
        super().__init__(message)

class ValidationError(CrunError):
    """Validation error."""
    pass

class ExecutionError(CrunError):
    """Execution error."""
    pass

class ConfigError(CrunError):
    """Configuration error."""
    pass

# Usage in crun code
from crun.shared.exceptions import ValidationError, ExecutionError

def validate_input(data: dict):
    if not data.get("name"):
        raise ValidationError("Name is required", context={"data": data})
```

### After: pheno.exceptions

```python
# No custom exceptions needed - use pheno.exceptions
from pheno.exceptions import ValidationError, ExecutionError, ConfigurationError

def validate_input(data: dict):
    if not data.get("name"):
        raise ValidationError(
            "Name is required",
            context={"data": data},
            category="validation"
        )
```

**Benefits:**
- ✅ Rich error context built-in
- ✅ Error categorization
- ✅ Consistent error handling
- ✅ Better error reporting

---

## 2. Retry Logic

### Before: Custom Retry Decorator

```python
# crun/shared/utils.py
import time
from functools import wraps

def retry_on_error(max_attempts: int = 3, delay: int = 1):
    """Custom retry decorator."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))
        return wrapper
    return decorator

# Usage
@retry_on_error(max_attempts=5, delay=2)
def call_api():
    # API call logic
    pass
```

### After: pheno.resilience

```python
# Use pheno.resilience
from pheno.resilience import with_retry, RetryConfig

# Simple usage
@with_retry(RetryConfig(max_attempts=5, backoff_multiplier=2))
async def call_api():
    # API call logic
    pass

# Advanced usage with custom config
retry_config = RetryConfig(
    max_attempts=5,
    backoff_multiplier=2,
    max_backoff=60,
    retry_on=(ConnectionError, TimeoutError),
    on_retry=lambda attempt, error: logger.warning(f"Retry {attempt}: {error}")
)

@with_retry(retry_config)
async def call_api():
    # API call logic
    pass
```

**Benefits:**
- ✅ Battle-tested retry logic
- ✅ Configurable backoff strategies
- ✅ Selective exception handling
- ✅ Retry callbacks

---

## 3. Circuit Breaker

### Before: No Circuit Breaker

```python
# crun code - no circuit breaker pattern
def call_external_service():
    try:
        response = requests.get("https://api.example.com")
        return response.json()
    except Exception as e:
        logger.error(f"API call failed: {e}")
        raise
```

### After: pheno.resilience Circuit Breaker

```python
from pheno.resilience import with_circuit_breaker, CircuitBreakerConfig

# Configure circuit breaker
cb_config = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=ConnectionError
)

@with_circuit_breaker(cb_config)
async def call_external_service():
    response = await client.get("https://api.example.com")
    return response.json()
```

**Benefits:**
- ✅ Prevents cascading failures
- ✅ Automatic recovery
- ✅ Configurable thresholds
- ✅ Better resilience

---

## 4. Logging

### Before: Custom Logger

```python
# crun/shared/logger.py
import logging
from typing import Any

class CrunLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs)

# Usage
from crun.shared.logger import CrunLogger
logger = CrunLogger(__name__)
logger.info("Processing request", user_id=123)
```

### After: pheno.logging

```python
# Use pheno.logging
from pheno.logging import get_logger

logger = get_logger(__name__)

# Structured logging with rich context
logger.info(
    "Processing request",
    extra={
        "user_id": 123,
        "request_id": "abc-123",
        "duration_ms": 45
    }
)

# Automatic correlation ID
from pheno.correlation_id import set_correlation_id
set_correlation_id("request-123")
logger.info("Processing")  # Correlation ID automatically included
```

**Benefits:**
- ✅ Structured logging
- ✅ Automatic correlation IDs
- ✅ JSON output support
- ✅ Better observability

---

## 5. Configuration

### Before: Custom Config Loading

```python
# crun/config/loader.py
import yaml
import os
from typing import Any, Dict

class ConfigLoader:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self._config = None
    
    def load(self) -> Dict[str, Any]:
        with open(self.config_path) as f:
            self._config = yaml.safe_load(f)
        
        # Override with environment variables
        for key, value in self._config.items():
            env_key = f"CRUN_{key.upper()}"
            if env_key in os.environ:
                self._config[key] = os.environ[env_key]
        
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

# Usage
from crun.config.loader import ConfigLoader
config = ConfigLoader("config.yaml")
config.load()
max_workers = int(config.get("max_workers", 4))
```

### After: pheno.config

```python
# Define typed config schema
from pheno.config import BaseConfig
from pydantic import Field

class CrunConfig(BaseConfig):
    """Typed configuration for crun."""
    max_workers: int = Field(default=4, ge=1, le=32)
    timeout: int = Field(default=300, ge=1)
    log_level: str = Field(default="INFO")
    database_url: str = Field(default="sqlite:///crun.db")
    
    class Config:
        env_prefix = "CRUN_"
        env_file = ".env"

# Usage
from pheno.config import ConfigManager
from crun.config.schema import CrunConfig

config = ConfigManager.load(CrunConfig, config_file="config.yaml")

# Type-safe access
max_workers = config.max_workers  # Type: int, validated
log_level = config.log_level      # Type: str
```

**Benefits:**
- ✅ Type-safe configuration
- ✅ Automatic validation
- ✅ Environment variable handling
- ✅ IDE autocomplete

---

## 6. CLI Commands

### Before: Custom CLI

```python
# crun/cli/main.py
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def execute(
    plan: str = typer.Argument(..., help="Path to plan file"),
    workers: int = typer.Option(4, help="Number of workers"),
    verbose: bool = typer.Option(False, help="Verbose output")
):
    """Execute a plan."""
    console.print(f"[blue]Executing plan: {plan}[/blue]")
    
    # Load config
    from crun.config.loader import ConfigLoader
    config = ConfigLoader("config.yaml")
    config.load()
    
    # Execute
    from crun.execution.executor import Executor
    executor = Executor(workers=workers)
    result = executor.execute(plan)
    
    console.print(f"[green]Completed: {result}[/green]")

if __name__ == "__main__":
    app()
```

### After: pheno.cli

```python
# crun/cli/commands.py
from pheno.cli import create_cli_app, command
from pheno.config import get_config
from pheno.logging import get_logger

logger = get_logger(__name__)
app = create_cli_app("crun")

@command(app)
def execute(
    plan: str,
    workers: int = 4,
    verbose: bool = False
):
    """Execute a plan."""
    # Config automatically loaded
    config = get_config()
    
    # Logging automatically configured
    logger.info("Executing plan", extra={"plan": plan, "workers": workers})
    
    # Execute
    from crun.execution.executor import Executor
    executor = Executor(workers=workers)
    result = executor.execute(plan)
    
    logger.info("Completed", extra={"result": result})
    return result

if __name__ == "__main__":
    app()
```

**Benefits:**
- ✅ Automatic config loading
- ✅ Automatic logging setup
- ✅ Consistent CLI patterns
- ✅ Better error handling

---

## 7. Metrics Collection

### Before: Custom Metrics

```python
# crun/shared/metrics.py
from typing import Dict
from datetime import datetime

class MetricsCollector:
    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, list] = {}
    
    def increment(self, name: str, value: int = 1):
        self.counters[name] = self.counters.get(name, 0) + value
    
    def gauge(self, name: str, value: float):
        self.gauges[name] = value
    
    def histogram(self, name: str, value: float):
        if name not in self.histograms:
            self.histograms[name] = []
        self.histograms[name].append(value)

# Usage
from crun.shared.metrics import MetricsCollector
metrics = MetricsCollector()
metrics.increment("requests_total")
metrics.gauge("active_connections", 42)
```

### After: pheno.observability

```python
# Use pheno.observability
from pheno.observability import MetricsCollector

metrics = MetricsCollector(service_name="crun")

# Counter with labels
metrics.increment(
    "requests_total",
    labels={"endpoint": "/api/v1", "method": "POST"}
)

# Gauge
metrics.gauge("active_connections", 42)

# Histogram
metrics.histogram("request_duration_seconds", 0.123)

# Timer context manager
with metrics.timer("operation_duration"):
    # Operation logic
    pass
```

**Benefits:**
- ✅ OpenTelemetry integration
- ✅ Label support
- ✅ Timer utilities
- ✅ Better observability

---

## 8. Async Utilities

### Before: Custom Async Utils

```python
# crun/shared/async_utils.py
import asyncio
from typing import List, Callable, Any

async def run_parallel(tasks: List[Callable], max_concurrent: int = 10):
    """Run tasks in parallel with concurrency limit."""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def bounded_task(task):
        async with semaphore:
            return await task()
    
    return await asyncio.gather(*[bounded_task(t) for t in tasks])

# Usage
from crun.shared.async_utils import run_parallel
results = await run_parallel([task1, task2, task3], max_concurrent=5)
```

### After: pheno.shared

```python
# Use pheno.shared async utilities
from pheno.shared.async_utils import run_parallel, with_timeout, gather_with_limit

# Run with concurrency limit
results = await gather_with_limit(
    [task1(), task2(), task3()],
    limit=5
)

# Run with timeout
result = await with_timeout(
    my_async_function(),
    timeout=30.0
)

# Batch processing
from pheno.shared.async_utils import batch_process

async def process_item(item):
    # Process logic
    pass

results = await batch_process(
    items=[1, 2, 3, 4, 5],
    processor=process_item,
    batch_size=10,
    max_concurrent=5
)
```

**Benefits:**
- ✅ Battle-tested utilities
- ✅ Better error handling
- ✅ Timeout support
- ✅ Batch processing

---

## 9. Workflow Orchestration

### Before: Custom Executor

```python
# crun/execution/executor.py
from typing import List, Dict, Any

class Executor:
    def __init__(self, workers: int = 4):
        self.workers = workers
    
    def execute(self, plan: str) -> Dict[str, Any]:
        # Load plan
        tasks = self._load_plan(plan)
        
        # Execute tasks
        results = []
        for task in tasks:
            result = self._execute_task(task)
            results.append(result)
        
        return {"status": "completed", "results": results}
    
    def _execute_task(self, task: Dict) -> Any:
        # Task execution logic
        pass

# Usage
from crun.execution.executor import Executor
executor = Executor(workers=4)
result = executor.execute("plan.json")
```

### After: pheno.workflow

```python
# Use pheno.workflow
from pheno.workflow import WorkflowEngine, WorkflowStep, WorkflowContext

# Define workflow steps
class LoadPlanStep(WorkflowStep):
    async def execute(self, context: WorkflowContext):
        plan = await self.load_plan(context.input["plan_path"])
        context.data["tasks"] = plan["tasks"]
        return context

class ExecuteTasksStep(WorkflowStep):
    async def execute(self, context: WorkflowContext):
        tasks = context.data["tasks"]
        results = []
        for task in tasks:
            result = await self.execute_task(task)
            results.append(result)
        context.data["results"] = results
        return context

# Create workflow
workflow = WorkflowEngine(
    name="execute_plan",
    steps=[LoadPlanStep(), ExecuteTasksStep()]
)

# Execute
result = await workflow.execute({"plan_path": "plan.json"})
```

**Benefits:**
- ✅ Structured workflow definition
- ✅ Context management
- ✅ Checkpointing support
- ✅ Better error handling

---

## 10. Database Access

### Before: Direct Database Access

```python
# crun/database/connection.py
import sqlite3
from typing import List, Dict, Any

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

# Usage
from crun.database.connection import Database
db = Database("crun.db")
db.connect()
results = db.execute("SELECT * FROM tasks WHERE status = ?", ("pending",))
```

### After: pheno.database

```python
# Use pheno.database
from pheno.database import AsyncDatabase, Repository
from pydantic import BaseModel

# Define model
class Task(BaseModel):
    id: int
    name: str
    status: str

# Define repository
class TaskRepository(Repository[Task]):
    table_name = "tasks"
    model = Task

# Usage
from pheno.database import get_database

db = await get_database()
task_repo = TaskRepository(db)

# Type-safe queries
pending_tasks = await task_repo.find_by(status="pending")
task = await task_repo.get(id=1)
await task_repo.create(Task(name="New Task", status="pending"))
```

**Benefits:**
- ✅ Type-safe database access
- ✅ Repository pattern
- ✅ Async support
- ✅ Connection pooling

---

## Summary

These examples show how migrating from custom implementations to pheno-sdk shared libraries provides:

1. **Less Code** - Eliminate custom implementations
2. **Better Quality** - Battle-tested patterns
3. **More Features** - Rich functionality built-in
4. **Consistency** - Uniform patterns across projects
5. **Maintainability** - Single source of truth

**Next Step:** Start with error handling migration (easiest, highest impact)

