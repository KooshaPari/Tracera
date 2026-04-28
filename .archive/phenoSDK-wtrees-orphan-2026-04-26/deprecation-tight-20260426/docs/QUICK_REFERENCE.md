# Pheno SDK Quick Reference

## 🚀 Quick Start

```python
# Install
pip install pheno-sdk

# Import what you need
from pheno.analytics.architecture import ArchitectureDetector
from pheno.async.orchestration import TaskOrchestrator
from pheno.resilience import CircuitBreaker, ExponentialBackoffRetry
from pheno.security.sandbox import SecuritySandbox, PathValidator
from pheno.architecture.hexagonal import DIContainer
```

---

## 📊 Architecture Detection

```python
# Detect architecture patterns
detector = ArchitectureDetector()
report = detector.detect(Path("/path/to/project"))

print(f"Patterns: {report.detected_patterns}")
print(f"Confidence: {report.confidence_scores}")
print(f"Recommendations: {report.recommendations}")
```

---

## ⚡ Async Orchestration

```python
# Setup orchestrator
orchestrator = TaskOrchestrator(config, storage, executor)
await orchestrator.start()

# Submit task
task_id = await orchestrator.submit_task(my_function, arg1, arg2)

# Wait for result
result = await orchestrator.wait_for_task(task_id)

# Create workflow
workflow_id = await orchestrator.create_workflow("workflow", [
    (task1, (), {}),
    (task2, (), {}),
    (task3, (), {})
])

await orchestrator.stop()
```

---

## 🔄 Resilience Patterns

```python
# Circuit breaker
breaker = CircuitBreaker("service", CircuitBreakerConfig())
result = await breaker.call_async(my_function, arg1, arg2)

# Retry strategy
retry = ExponentialBackoffRetry(RetryConfig(max_attempts=3))
result = await retry.execute_async(my_function, arg1, arg2)

# Decorator
@with_retry(max_attempts=3, strategy="exponential")
async def my_function():
    pass
```

---

## 🔒 Security Sandbox

```python
# Path validation
validator = PathValidator(PathValidationConfig())
safe_path = validator.validate_path("/safe/path/file.txt")

# Security sandbox
sandbox = SecuritySandbox(SandboxConfig())
with sandbox:
    result = sandbox.execute_safely(my_function, arg1, arg2)

# Resource limits
limits = ResourceLimits(ResourceLimitConfig())
limits.enforce_limits()
```

---

## 🏗️ Hexagonal Architecture

```python
# DI Container
container = DIContainer()
container.register(MyService, MyServiceImpl, singleton=True)
service = container.get(MyService)

# Port/Adapter
port_adapter = PortAdapter(port_registry, adapter_registry)
port_adapter.connect("user_repo", "db_adapter")
user = await port_adapter.call_port("user_repo", user_id)
```

---

## 📦 Storage Backends

```python
# In-memory
from pheno.async.storage import InMemoryTaskStorage
storage = InMemoryTaskStorage()

# File-based
from pheno.async.storage import FileTaskStorage
storage = FileTaskStorage(Path("/storage"))

# Database
from pheno.async.storage import DatabaseTaskStorage
storage = DatabaseTaskStorage("/path/to/db.db")

# Redis
from pheno.async.storage import RedisTaskStorage
storage = RedisTaskStorage("redis://localhost:6379/0")
```

---

## 🎯 Common Patterns

### Error Handling
```python
from pheno.resilience import ErrorHandler, ErrorCategorizer

handler = ErrorHandler(ErrorCategorizer())
error_info = handler.create_error_info(exception, context)
result = await handler.handle_error(error_info)
```

### Progress Tracking
```python
from pheno.async.monitoring import TaskMonitor

monitor = TaskMonitor()
monitor.start_task_progress(task_id, total_steps=100)
monitor.update_task_progress(task_id, completed_steps=50)
monitor.complete_task_progress(task_id, success=True)
```

### Health Checking
```python
from pheno.resilience.health import HealthChecker, HealthMonitor

class MyHealthChecker(HealthChecker):
    async def check_health(self):
        return HealthCheck("my_service", HealthStatus.HEALTHY)

monitor = HealthMonitor()
monitor.add_checker("my_service", MyHealthChecker())
health = await monitor.get_overall_health()
```

---

## 🔧 Configuration Examples

### Architecture Detection
```python
config = ArchitectureDetectorConfig(
    min_confidence=0.3,
    max_depth=10,
    include_hidden=False,
    skip_directories=[".git", "node_modules"]
)
```

### Task Orchestration
```python
config = OrchestrationConfig(
    max_concurrent_tasks=10,
    task_timeout=300.0,
    enable_metrics=True,
    storage_backend="redis"
)
```

### Circuit Breaker
```python
config = CircuitBreakerConfig(
    failure_threshold=5,
    failure_window=60.0,
    recovery_timeout=30.0,
    enable_monitoring=True
)
```

### Security Sandbox
```python
config = SandboxConfig(
    isolated_filesystem=True,
    allow_network=False,
    allow_subprocess=False,
    max_file_size=10*1024*1024
)
```

---

## 📈 Monitoring & Metrics

```python
# Get metrics
metrics = orchestrator.get_metrics()
health = monitor.get_health_status()
error_stats = error_handler.get_error_metrics()

# Monitor progress
progress = monitor.get_task_progress(task_id)
workflow_progress = monitor.get_workflow_progress(workflow_id)
```

---

## 🚨 Error Handling

```python
# Common exceptions
from pheno.resilience import CircuitBreakerOpenError, MaxRetriesExceededError
from pheno.security.sandbox import SandboxViolationError, PathValidationError
from pheno.architecture.hexagonal import CircularDependencyError

try:
    result = await breaker.call_async(func)
except CircuitBreakerOpenError:
    print("Service unavailable")
except MaxRetriesExceededError:
    print("Max retries exceeded")
except SandboxViolationError:
    print("Security violation")
```

---

## 🔍 Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Get detailed information
report = detector.get_detailed_analysis(project_path)
stats = orchestrator.get_executor_stats()
security_report = sandbox.generate_security_report()
```

---

## 📚 Further Reading

- [Complete Documentation](PHASE_5_SDK_MODULES.md)
- [API Reference](api/)
- [Examples](examples/)
- [Migration Guide](migration/)
- [Best Practices](best-practices/)
