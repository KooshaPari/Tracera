# Pheno Kit

This kit provides functionality for pheno operations.

## 📦 Overview

The pheno kit is part of the Pheno SDK ecosystem and provides:

- Core pheno functionality
- Integration with other kits
- Comprehensive testing
- Full documentation

## 🚀 Quick Start

```python
from pheno.pheno import PhenoKit

# Initialize the kit
kit = PhenoKit()

# Use the kit
result = kit.process()
```

## 📚 API Reference

### Classes

#### StreamManager

High-level streaming manager for WebSocket and SSE connections.

This is a facade over the streaming infrastructure. For full protocol
implementations, use stream-kit package.

Example:
    manager = StreamManager()
    await manager.register_websocket("conn1", websocket, ["chat"])
    await manager.broadcast("chat", {"message": "Hello"})

#### Database

Universal database abstraction.

#### MissingSupabaseConfig

Raised when Supabase configuration is missing or invalid.

#### OutputCaptureConfig

Optional configuration for CLIs that write output to disk.

#### CLIRoleConfig

Role-specific configuration loaded from JSON manifests.

#### CLIClientConfig

Raw CLI client configuration before internal defaults are applied.

#### ResolvedCLIRole

Runtime representation of a CLI role with resolved prompt path.

#### ResolvedCLIClient

Runtime configuration after merging defaults and validating paths.

#### RegistryLoadError

Raised when configuration files are invalid or missing critical data.

#### ClinkRegistry

Loads CLI client definitions and exposes them for schema generation/runtime use.

#### _ConfigMock



#### CLIInternalDefaults

Internal defaults applied to a CLI client during registry load.

#### ServiceInfo

Runtime information about a managed service.

#### PortRegistry

Registry for ports.

#### SmartPortAllocator

Smart port allocator with conflict resolution.

Features:
- Semi-static port allocation (consistent ports across runs)
- Automatic conflict detection and resolution
- Process detection and management
- Stale instance cleanup
- Port range management

#### ServiceTemplate

Base template for service types.

#### PythonASGIService

Template for Python ASGI applications.

Supports: FastAPI, FastMCP, Litestar, Starlette, Quart, etc.

Usage:
    service = PythonASGIService(
        name="zen-mcp-server",
        app_path="server:app",
        port=50002,
        workers=1,
        reload=False
    ).to_service_config()

    # Override environment variables
    service.env["MCP_BASE_PATH"] = "/mcp"
    service.tunnel_health_endpoint = "/mcp/healthz"

#### GoHTTPService

Template for Go HTTP servers.

Usage:
    service = GoHTTPService(
        name="api",
        module_dir=Path("backend/api"),
        port=8080,
        path_prefix="/api/v1"
    ).to_service_config()

#### NextJSService

Template for Next.js applications.

Usage:
    service = NextJSService(
        name="frontend",
        app_dir=Path("frontend/web-next"),
        port=3000,
        dev_mode=True
    ).to_service_config()

#### StaticSiteService

Template for static site servers.

Usage:
    service = StaticSiteService(
        name="docs",
        root_dir=Path("dist"),
        port=8080
    ).to_service_config()

#### ResourceManager

Manages resource usage for sandboxed operations.

#### OrchestrationError

Raised when orchestration operations fail.

#### OrchestratorConfig

Configuration for the orchestrator.

#### ServiceOrchestrator

Advanced service orchestrator with dependency management and monitoring.

Provides comprehensive orchestration capabilities including:
- Dependency resolution and ordering
- Parallel and sequential execution modes
- Health monitoring and auto-recovery
- Graceful shutdown with dependency ordering
- Progress tracking and status reporting

#### KInfraError

Base exception for all KInfra operations.

#### PortAllocationError

Raised when port allocation fails.

#### TunnelError

Raised when tunnel operations fail.

#### ServiceConflictError

Raised when service conflicts cannot be resolved.

#### ProcessManagementError

Raised when process management operations fail.

#### ConfigurationError

Raised when configuration validation fails.

#### ServiceError

Raised when service management operations fail.

#### LookupRequest

Request model for API lookup tool.

#### LookupTool

Simple tool that wraps user queries with API lookup instructions.

#### TableColumn



#### SchemaSnapshot



#### SchemaDiff



#### SchemaSync

Synchronise Supabase metadata with generated schema snapshots.

#### DeploymentCheck



#### DeploymentChecker



#### ContentType

Types of content that can be generated.

#### ContentGenerationConfig

Configuration for content generation.

#### ContentRequest

Request for content generation.

#### ContentResponse

Response from content generation.

#### LLMProvider

Protocol for LLM providers.

#### ContentGenerator

Generic content generator using various LLM providers.

#### RegistryType

Types of registries supported by the unified system.

#### RegistryConfig

Configuration for a registry instance.

#### UnifiedRegistryManager

Central manager for all registries in the system.

Provides a single point of access for all registry operations and ensures
consistency across the codebase.

#### RegistryMigrator

Utility class for migrating from old registry implementations.

#### QualityPlugin

Abstract base class for quality analysis plugins.

#### PluginRegistry

Stores plugin hooks keyed by adapter type/name.

#### QualityToolRegistry

Registry for quality analysis tools.

#### QualityFrameworkExporter

Export quality analysis framework for use in other projects.

#### QualityFrameworkImporter

Import quality analysis framework from exported package.

#### SeverityLevel

Severity levels for issues.

#### ImpactLevel

Quality issue impact levels.

#### QualityIssue

Represents a quality analysis issue.

#### QualityMetrics

Quality analysis metrics.

#### QualityConfig

Quality analysis configuration.

#### QualityReport

Comprehensive quality analysis report.

#### QualityAnalyzer

Abstract base class for quality analysis tools.

#### QualityImporter

Abstract base class for quality report importers.

#### JSONImporter

Import quality reports from JSON format.

#### CSVImporter

Import quality reports from CSV format.

#### XMLImporter

Import quality reports from XML format.

#### QualityReportImporter

Main importer that can handle multiple formats.

#### QualityFrameworkIntegration

Integration class for quality analysis framework.

#### QualityUtils

Utility functions for quality analysis.

#### QualityExporter

Abstract base class for quality report exporters.

#### JSONExporter

Export quality reports to JSON format.

#### HTMLExporter

Export quality reports to HTML format.

#### MarkdownExporter

Export quality reports to Markdown format.

#### CSVExporter

Export quality reports to CSV format.

#### XMLExporter

Export quality reports to XML format.

#### QualityAnalysisManager

Main manager for quality analysis operations.

#### Config



#### AppConfig

Core application settings.

#### MorphConfig

Morph-specific runtime options exposed via pheno.config.

#### DatabaseConfig

Database connection settings.

#### RedisConfig

Redis connection details tuned for ``redis-py`` compatibility.

Callers can forward ``RedisConfig.model_dump()`` directly to client
constructors for ergonomic setup.

#### ConfigManager

Hierarchical configuration loader with optional hot reload.

#### MorphIntegrationSettings



#### RouterIntegrationSettings



#### RetryConfig

Retry behavior configuration.

#### AzureOpenAIConfig

Azure OpenAI provider configuration.

#### ProviderConfigs

Container for all provider configurations.

#### JWTError

JWT operation error.

#### PIIPattern

PII pattern definitions.

#### PIIScanner

Scan and redact PII from text.

Example:
    scanner = PIIScanner()
    text = "Contact john@example.com or call 555-123-4567"
    redacted = scanner.redact(text)
    # "Contact [EMAIL] or call [PHONE]"

#### AuthProvider

Protocol for authentication providers.

#### MFAAdapter

Base interface for multi-factor authentication adapters.

#### TokenManager

Manage OAuth tokens for AuthKit using the shared FileTokenManager.

#### CredentialManager

Base interface for secure credential storage.

#### MFAAdapterRegistry

Central in-memory registry for MFA adapters.

#### AuthProviderRegistry

Registry interface for managing auth provider implementations.

#### InteractiveCredentialManager

Manage OAuth credentials with interactive prompts.

Handles secure storage and retrieval of OAuth credentials
with interactive fallback for missing values.

Example:
    manager = InteractiveCredentialManager("my_app")

    # Get credentials (prompts if not found)
    creds = manager.get_credentials(
        required_fields=["client_id", "client_secret"]
    )

    # Save for next time
    manager.save_credentials(creds)

#### CachedToken

Cached token with metadata.

#### TokenCache

In-memory token cache with TTL support.

Example:
    cache = TokenCache()

    # Store token
    cache.set(
        "user123",
        token="abc123",
        expires_in=3600
    )

    # Retrieve token
    cached = cache.get("user123")
    if cached and not cached.is_expired():
        print(cached.token)

#### EncryptedTokenStorage

Persistent token storage with optional encryption.

Stores tokens to disk with optional XOR encryption.
For production use, consider using stronger encryption.

Example:
    storage = EncryptedTokenStorage(
        storage_path=Path("~/.config/myapp/tokens.json"),
        encryption_key="my-secret-key"
    )

    # Save token
    storage.save("user123", token="abc123", expires_in=3600)

    # Load token
    cached = storage.load("user123")

#### _StoredTokens

Serializable representation of :class:`AuthTokens`.

#### _TokenStorage

Lightweight encrypted JSON storage.

#### FileTokenManager

Token manager backed by an in-memory cache with optional disk persistence.

Parameters
----------
storage_path:
    Location of the JSON file used to persist tokens. When omitted,
    only the in-memory cache is used.
encryption_key:
    Optional XOR key used to obfuscate the JSON on disk.

#### TOTPHandler

Time-based One-Time Password (TOTP) handler.

Implements RFC 6238 TOTP algorithm for generating and validating
time-based one-time passwords.

Example:
    handler = TOTPHandler(secret="BASE32SECRET")

    # Generate current code
    code = handler.generate()

    # Verify code
    is_valid = handler.verify(code)

#### MFAHandler

Generic MFA handler with support for multiple methods.

Example:
    handler = MFAHandler()

    # Register TOTP
    handler.register_totp("user@example.com", "BASE32SECRET")

    # Verify code
    is_valid = handler.verify_totp("user@example.com", "123456")

#### ProviderType

Supported authentication provider types.

#### MFAMethod

Supported multi-factor authentication methods.

#### AuthTokens

Authentication tokens returned by providers.

#### Credentials

Authentication credentials supplied to cloud providers.

#### MFAContext

Context passed to MFA adapters when additional verification is required.

#### AuthResult

Result container returned by AuthManager.authenticate.

#### AuthError

Base exception for authentication errors.

#### AuthenticationError

Credential or permission issues.

#### AuthorizationError

Raised when authorization fails.

#### TokenExpiredError

Raised when a token has expired.

#### MFARequiredError

Raised when MFA is required for authentication.

#### ProviderError

Raised when a provider-specific error occurs.

#### TokenError

Raised for token parsing or storage failures.

#### CredentialError

Raised when credential material is invalid or missing.

#### PlaywrightOAuthAdapter

Adapter for Playwright-based OAuth automation.

Requires playwright to be installed separately.
This is a lightweight adapter that can work with or without playwright.

Example:
    # Requires: pip install playwright && playwright install
    adapter = PlaywrightOAuthAdapter()

    tokens = adapter.authenticate(
        auth_url="https://oauth.example.com/authorize",
        success_pattern="code="
    )

#### MockBrowserAdapter

Mock browser adapter for testing OAuth flows.

Simulates browser interactions without requiring Playwright.

Example:
    adapter = MockBrowserAdapter(
        mock_response={"code": "test_auth_code"}
    )
    result = adapter.authenticate("https://example.com")

#### AuthManager

Application-facing authentication orchestrator.

#### OAuthTokens

OAuth token container.

#### SessionOAuthBroker

OAuth session broker for managing authentication flows.

Simple OAuth token management without external dependencies.
For production use, consider using authlib or similar libraries.

Example:
    broker = SessionOAuthBroker(
        client_id="your-client-id",
        token_endpoint="https://oauth.example.com/token"
    )

    # Get tokens
    tokens = broker.exchange_code_for_tokens(auth_code)

    # Refresh tokens
    new_tokens = broker.refresh_tokens(tokens.refresh_token)

#### RegistryProviderMixin

Mixin that wires a provider to a CapabilityModelRegistry subclass.

Subclasses must set REGISTRY_CLASS to a class implementing:
  - list_models()
  - resolve(name_or_alias)
  - get_capabilities(name_or_alias)

#### ModelCategory

Categories for model capabilities and tool requirements.

#### ProviderRequestContext

Additional metadata supplied by routing layers when invoking providers.

These fields are optional and allow downstream adapters to make informed decisions
about prioritisation, budgeting, and telemetry without coupling the provider surface
to a specific router implementation.

#### ProviderResponseMetadata

Supplementary metadata returned by provider adapters.

#### ModelProvider

Base class for model providers.

#### ModelProviderRegistry

Unified model provider registry using BaseRegistry.

Simplified implementation that uses BaseRegistry for storage and lookup. Maintains
singleton pattern and provider priority order.

#### BaseAllocator

Base class for resource allocators.

#### FixedAllocator

Fixed allocation strategy.

Allocates the minimum of requested units and configured limits.

#### ProportionalAllocator

Proportional allocation strategy.

Allocates resources proportional to available budget.

#### DynamicAllocator

Dynamic allocation strategy.

Adjusts allocation based on current utilization levels.

#### PriorityAllocator

Priority-based allocation strategy.

Allocates more resources to higher priority requests.

#### AdaptiveAllocator

Adaptive allocation strategy.

Learns from historical patterns to optimize allocations.

#### BudgetStatusRenderer

Renders budget status and allocation information.

#### TextRenderer

Text-based rendering for budgets and allocations.

#### JsonRenderer

JSON-based rendering for budgets and allocations.

#### HtmlRenderer

HTML-based rendering for budgets and allocations.

#### AlertRenderer

Renders alerts and warnings for resource management.

#### BudgetPeriod

Budget tracking periods.

#### AllocationStrategy

Resource allocation strategies.

#### ResourceBudget

Generic resource budget configuration.

Can be used for tokens, API calls, cloud costs, or any constrained resource.

#### ResourceAllocation

Individual resource allocation.

Tracks allocation of resources for a specific request or operation.

#### BudgetLoader

Loads and validates resource budgets from configuration.

#### AllocationLoader

Loads and manages resource allocations with validation.

#### ResourceLimitsLoader

Loads and manages resource limits and constraints.

#### UsageTracker

Track resource usage over time.

Maintains time-series data for resource consumption.

#### HistoricalAnalyzer

Analyze historical usage patterns.

Provides insights into resource consumption trends and patterns.

#### PredictivePlanner

Predictive planning for resource budgets.

Forecasts future usage and provides budget recommendations.

#### StorageBackend

Abstract interface for storage backends.

#### InMemoryStorage

In-memory storage backend.

#### RedisStorage

Redis-based storage backend.

Provides persistent storage with time-series support.

#### ResourceCache

Cache layer for resource data.

Provides in-memory caching with optional persistence backend.

#### StorageManager

Manages storage backend operations and data migration.

#### ResourceBudgetManager

Manages resource budgets and allocations.

Supports multiple resource types (tokens, API calls, costs, etc.) with flexible
allocation strategies and storage backends.

#### AsyncTaskExecutor

Async task executor that runs tasks in asyncio event loop.

#### SyncTaskExecutor

Synchronous task executor that runs tasks in thread pool.

#### TaskWorker

Individual task worker.

#### WorkerPool

Pool of task workers.

#### HybridTaskExecutor

Hybrid executor that can run both async and sync tasks.

#### ProcessTaskExecutor

Process-based task executor for CPU-intensive tasks.

#### TaskExecutionEngine

High-level task execution engine with multiple strategies.

#### TaskMetrics



#### ProgressTracker

Track and display progress for multiple operations.

Features:
- Multiple progress bars
- Percentage display
- Status indicators
- ETA calculation

Example:
    tracker = ProgressTracker(title="Build Progress")
    tracker.add_task("compile", total=100)
    tracker.update_task("compile", completed=50)

#### MetricsCollector

Collects and aggregates metrics from various sources.

Consolidates metrics collection from infra/monitoring, MCP QA, and observability
stacks into a unified interface.

#### TaskMonitor

High-level task monitoring system.

#### TaskStatus



#### TaskPriority



#### TaskResult

Result of a completed task.

#### TaskConfig

Configuration for a task.

#### Task



#### OrchestrationConfig

Configuration for service orchestration.

#### TaskStorage

Abstract interface for task storage.

#### TaskExecutor

Abstract base class for task executors.

#### TaskManager

Manages task lifecycle and execution.

#### TaskScheduler

Schedules tasks with cost optimization and prioritization.

#### WorkflowEngine

Simple workflow execution engine.

Example:
    engine = WorkflowEngine()
    execution = await engine.execute(workflow, context)

#### TaskOrchestrator

Main orchestrator that coordinates all async task management.

#### InMemoryTaskStorage

In-memory task storage for development/testing.

#### FileTaskStorage

File-based storage backend for tasks.

#### DatabaseTaskStorage

SQLite database storage backend for tasks.

#### RedisTaskStorage

Redis-based task storage for production.

#### ToolStatus

Status of a tool execution.

#### SessionStatus

Status of an MCP session.

#### McpServer

MCP server configuration.

Represents an MCP server that can be connected to.

Example:
    >>> server = McpServer(
    ...     url="http://localhost:8000",
    ...     name="local-mcp",
    ...     auth_token="secret"
    ... )

#### McpSession

MCP session.

Represents an active connection to an MCP server.

Example:
    >>> session = McpSession(
    ...     session_id="session-123",
    ...     server=server,
    ...     status=SessionStatus.CONNECTED
    ... )

#### McpTool

MCP tool definition.

Represents a tool that can be executed via MCP.

Example:
    >>> tool = McpTool(
    ...     name="search",
    ...     description="Search documentation",
    ...     parameters={"query": {"type": "string", "required": True}}
    ... )

#### ToolExecution

Tool execution context.

Tracks the execution of a tool with parameters and results.

Example:
    >>> execution = ToolExecution(
    ...     tool=tool,
    ...     parameters={"query": "hello"},
    ...     session=session
    ... )

#### ToolResult

Tool execution result.

Contains the output and metadata from a tool execution.

Example:
    >>> result = ToolResult(
    ...     output={"results": [...]},
    ...     success=True,
    ...     metadata={"execution_time": 1.23}
    ... )

#### Resource

Snapshot of a deployed cloud resource and its metadata.

#### WorkflowExecution

Workflow execution record.

#### McpManager

Central MCP manager.

Coordinates MCP operations using dependency injection.
Provides a unified API for all MCP functionality.

Example:
    >>> manager = McpManager()
    >>>
    >>> # Connect to server
    >>> session = await manager.connect(server)
    >>>
    >>> # Execute tool
    >>> result = await manager.execute_tool("search", {"query": "hello"})
    >>>
    >>> # Access resources
    >>> config = await manager.get_resource("config://app/database")

#### CommandCategory

Command category enumeration.

#### ProjectType

Types of projects supported by the command engine.

#### CLICommand

CLI command definition.

#### CommandRegistry

Centralized command registry for all CLI systems.

#### CLIAdapter

CLI Adapter for translating CLI commands to use cases.

This adapter is responsible for:
- Input validation and transformation
- Calling appropriate use cases
- Formatting output for CLI display
- Error handling and user feedback

#### CLIContext

CLI context manager.

#### SimpleCLI

Simple CLI implementation.

#### RichCLIAdapter

Rich CLI adapter for enhanced terminal output.

#### ClickCLIAdapter

Click CLI adapter.

#### ArgparseCLIAdapter

Argparse CLI adapter.

#### RichCLI

Rich CLI implementation.

#### Args



#### Storage

Universal storage client with pluggable backends.

#### SyncStrategy

Synchronization strategy enumeration.

#### SyncResult

Result of synchronization operation.

#### CICDSynchronizer

CI/CD synchronization orchestrator.

#### SoftDependencyManager

Manager for soft dependencies across projects.

#### CICDRepository

Repository port for CI/CD configuration storage.

#### CICDConfigProvider

Configuration provider port.

#### CICDSyncProvider

Synchronization provider port.

#### CICDTemplateProvider

Template provider port.

#### CICDQualityProvider

Quality integration provider port.

#### CICDNotificationProvider

Notification provider port.

#### CICDArtifactProvider

Artifact management provider port.

#### CICDDeploymentProvider

Deployment provider port.

#### PipelineStage

Pipeline stage enumeration.

#### CICDEvent

CI/CD event enumeration.

#### CICDConfig

CI/CD configuration for a project.

#### CICDTemplate

CI/CD template definition.

#### CICDPipeline

Generated CI/CD pipeline.

#### CICDGenerator

Abstract base class for CI/CD generators.

#### TemplateLoader

Custom template loader for CI/CD templates.

#### TemplateEngine

Template engine for CI/CD generation.

#### TemplateRegistry

Registry for CI/CD templates.

#### Environment



#### BaseLoader



#### TemplateError

Template-related errors.

#### MockTemplate



#### PhenoCICDGenerator

Pheno CI/CD generator implementation.

#### CICDGeneratorFactory

Factory for creating CI/CD generators.

#### CICDCLI

CI/CD CLI interface.

#### QualityGateIntegrator

Quality gate integrator for CI/CD pipelines.

#### QualityCheckConfig

Quality check configuration.

#### CICDManager

Main CI/CD management system.

#### FileSystemRepository

File system implementation of CI/CD repository.

#### DefaultConfigProvider

Default configuration provider.

#### FileSystemSyncProvider

File system implementation of sync provider.

#### InMemoryTemplateProvider

In-memory implementation of template provider.

#### EnvLoadError

Raised when environment loading fails.

#### EnvConfig

Configuration for environment loading.

#### BudgetLimit

Defines spending limits for a given entity.

#### BudgetUsage

Tracks usage within the configured windows.

#### BudgetManager

In-memory budget tracker with daily/monthly windows.

#### RateLimitRule

Token bucket configuration for a specific key.

#### _BucketState



#### TokenBucketRateLimiter

Per-key token bucket limiter with async locking.

#### BaseFactory

Fallback factory when polyfactory not available.

#### AsyncFactory

Fallback async factory when polyfactory not available.

#### FreezeTime

Context manager to freeze time for testing.

Example:
    def test_with_frozen_time():
        with FreezeTime("2025-01-01 12:00:00"):
            # Time is frozen
            now = datetime.now()
            assert now.year == 2025

#### BaseRegistry

Thread-safe base registry implementation.

Implements all registry protocols with in-memory storage and thread safety.
Can be extended for specific use cases.

Example:
    >>> class ToolRegistry(BaseRegistry[McpTool]):
    ...     pass
    >>>
    >>> registry = ToolRegistry()
    >>> registry.register("search", search_tool)
    >>> tool = registry.get("search")

#### Lifecycle

Service lifecycle strategies.

#### ServiceDefinition

Definition of a service in the container.

#### Scope

Scope for scoped service instances.

#### Container

Dependency injection container with auto-wiring.

Features:
- Auto-wiring via type hints
- Lifecycle management (singleton, transient, scoped)
- Circular dependency detection
- Constructor injection
- Named services and aliases

Example:
    >>> container = Container()
    >>> container.register(IDatabase, PostgresDatabase, lifecycle=Lifecycle.SINGLETON)
    >>> container.register(IService, UserService, lifecycle=Lifecycle.TRANSIENT)
    >>> service = container.resolve(IService)  # Auto-wires PostgresDatabase

#### HexagonalError

Base exception for hexagonal architecture errors.

#### PortNotFoundError

Raised when a port is not found.

#### AdapterNotFoundError

Raised when an adapter is not found.

#### ServiceNotFoundError

Raised when a service is not found.

#### CircularDependencyError

Raised when circular dependency is detected.

#### ServiceConfig



#### HexagonalConfig

Configuration for hexagonal architecture.

#### Port

Network port value object with validation.

#### Adapter

Abstract base class for adapters.

#### UseCase

Structured use case with flows.

#### DomainService

Abstract base class for domain services.

#### ApplicationService

Abstract base class for application services.

#### ServiceRegistry

Registry for managing services.

#### DIContainer

Dependency injection container.

#### AdapterRegistry

Unified adapter registry that consolidates adapter management functionality.

#### PortAdapter

Port-adapter connector.

#### ServiceProvider

Service provider for hexagonal architecture.

#### HealthStatus

Health status enumeration.

#### HealthCheck

A health check definition.

#### HealthConfig

Configuration for health monitoring.

#### HealthChecker

Manages and executes health checks.

Consolidates health checking from infra/monitoring, MCP QA, and observability stacks
into a unified interface.

#### HealthMonitor

Poll upstream health and notify fallback servers of status changes.

#### TimeoutConfig

Configuration for timeout handling.

#### TimeoutError

Base timeout error.

#### OperationTimeoutError

Raised when an operation times out.

#### TimeoutHandler

Handles timeouts for operations.

#### ErrorCategory

Error categories for consistent handling.

#### ErrorSeverity

Error severity levels.

#### ErrorInfo

Detailed error information.

Attributes:
    exception: The exception that occurred
    category: Error category
    severity: Error severity
    context: Error context
    traceback_str: Formatted traceback
    metadata: Additional metadata
    retry_count: Number of retries attempted
    original_exception: Original exception if wrapped

#### ErrorCategorizer

Categorizes errors based on various heuristics.

#### ErrorHandler

Generic error handler with categorization and custom handlers.

This class provides:
- Automatic error categorization
- Severity determination
- Custom error handlers per category
- Error statistics tracking

Example:
    >>> handler = ErrorHandler()
    >>> handler.register_handler(
    ...     ErrorCategory.NETWORK,
    ...     lambda error: print(f"Network error: {error.exception}")
    ... )
    >>> error_info = handler.create_error_info(ConnectionError("Failed"))
    >>> await handler.handle_error(error_info)

#### ErrorTracker

Tracks and analyzes errors.

#### ErrorMetrics

Metrics for error tracking.

Attributes:
    total_errors: Total number of errors
    errors_by_category: Count of errors by category
    errors_by_severity: Count of errors by severity
    successful_operations: Count of successful operations
    retry_attempts: Total retry attempts
    circuit_breaker_activations: Times circuit breaker opened

#### ErrorAnalyzer

Analyzes error patterns and trends.

#### RetryError

Raised when retry attempts are exhausted.

#### MaxRetriesExceededError

Raised when maximum retries are exceeded.

#### RetryStrategy

Configurable retry strategy with exponential backoff.

Example:
    strategy = RetryStrategy(max_attempts=3, backoff_factor=2.0)
    result = strategy.execute(lambda: make_request())

#### ExponentialBackoffRetry

Exponential backoff retry strategy.

#### LinearBackoffRetry

Linear backoff retry strategy.

#### ConstantDelayRetry

Constant delay retry strategy.

#### FibonacciBackoffRetry

Fibonacci backoff retry strategy.

#### AdaptiveRetry

Adaptive retry strategy that adjusts based on success/failure patterns.

#### RetryManager

Manages multiple retry strategies.

#### BulkheadConfig

Configuration for bulkhead pattern.

#### BulkheadFullError

Raised when bulkhead is full and cannot accept more calls.

#### ResourcePool

Manages a pool of resources with concurrency limits.

#### Bulkhead

Bulkhead pattern implementation for resource isolation.

#### BulkheadManager

Manages multiple bulkheads.

#### CircuitBreakerState

States of the circuit breaker.

#### CircuitBreakerConfig

Configuration for circuit breaker.

#### CircuitBreakerError

Raised when circuit breaker is open.

#### CircuitBreakerOpenError

Raised when circuit breaker is open.

#### CircuitBreaker

Circuit breaker implementation.

#### CircuitBreakerManager

Manages multiple circuit breakers.

#### ErrorContext

Context information for an error.

#### FallbackConfig

Configuration for fallback handling.

#### FallbackError

Raised when fallback operations fail.

#### FallbackStrategy

Abstract base class for fallback strategies.

#### FallbackHandler

Handles fallback mechanisms for operations.

#### PlatformInfo

Information about a deployment platform.

#### PlatformDetector

Auto-detect deployment platform from project structure.

Checks for platform-specific files and configurations.

#### DeployConfig

Wrapper grouping deployment behaviour configuration.

#### PackageDetector

Detect which pheno-sdk packages are actually used in a project.

Uses multiple strategies:
1. Parse requirements.txt
2. Scan Python imports
3. Check for common usage patterns

#### Deployer

Multi-cloud deployment orchestrator.

#### StepStatus

Status for progress steps.

#### ProgressStep

A step in the vendoring process.

#### FallbackConsole

Fallback console when Rich is not available.

#### PhenoUI

UI manager for pheno-vendor CLI.

Provides rich progress bars, spinners, and summary panels. Falls back to simple
output if Rich is not available.

#### StepProgressContext

Context manager for step progress tracking.

#### VendorChecker

Check and manage pheno-vendor package freshness.

#### BuildHookGenerator

Generate platform-specific build hooks and configurations.

Creates scripts and config files that use vendored pheno-sdk packages.

#### ArtifactValidator

Validate generated artifacts and deployment readiness.

Ensures generated build scripts and configurations are valid.

#### ConfigValidationError

Configuration validation error.

#### EnvironmentConfig

Manage environment-specific configuration.

Handles loading and validating configuration files for different deployment
environments.

#### EnvVarManager

Manage environment variables for deployment.

Handles loading, validating, and managing environment variables across different
deployment platforms.

#### Worker



#### UnifiedError

Base exception with context.

#### UnifiedErrorHandler

Unified error handler combining all error handling functionality.

Features:
- Error classification
- Retry logic with exponential backoff
- Circuit breaker pattern
- Structured error responses

#### ZenMCPError

Base exception class for PyDevKit errors.

#### NetworkError

Connection or network issues.

#### ValidationError

Raised when configuration validation fails.

#### ResourceNotFoundError

Resource doesn't exist.

#### RateLimitError

Rate limiting errors.

#### ExternalServiceError

External service errors.

#### StructuredError

Structured error with enhanced context (from enhanced.py).

#### ErrorHandlingError

Base exception for error handling errors (from core/types.py).

#### RetryableError

Base class for errors that should be retried (from retry.py).

#### NonRetryableError

Base class for errors that should not be retried (from retry.py).

#### EventBus

Manage event handlers and dispatch events.

#### WebhookServer

Webhook server with HMAC verification.

#### NATSConnectionFactory



#### NatsEventBus



#### Registry

Generic threadsafe registry with namespaced keys.

#### SearchableRegistry

Registry with search capabilities.

Extends basic registry with search and filtering.

Example:
    >>> registry = SearchableToolRegistry()
    >>> tools = registry.search("database")
    >>> tools = registry.filter(category="data", tags=["sql"])

#### ObservableRegistry

Registry with observation capabilities.

Allows subscribing to registry changes.

Example:
    >>> registry = ObservableToolRegistry()
    >>> registry.on_register(lambda name, item: print(f"Registered: {name}"))
    >>> registry.register("search", search_tool)  # Triggers callback

#### CategorizedRegistry

Registry with category support.

Organizes items into categories.

Example:
    >>> registry = CategorizedToolRegistry()
    >>> registry.register("search", search_tool, category="data")
    >>> data_tools = registry.list_by_category("data")
    >>> categories = registry.list_categories()

#### MetadataRegistry

Registry with metadata support.

Stores and retrieves metadata for items.

Example:
    >>> registry = MetadataToolRegistry()
    >>> registry.set_metadata("search", {"version": "1.0", "author": "alice"})
    >>> metadata = registry.get_metadata("search")

#### LogLevel



#### LogEntry

Individual log entry.

#### Logger



#### LoggerFactory

Factory interface responsible for constructing configured loggers.

Allows adapters to supply pre-configured logger instances with shared transports,
filters, or formatters.

#### SpanContext

Lightweight context carriers used to propagate tracing metadata.

Fields follow OpenTelemetry conventions so adapters can interoperate with popular
tracing backends.

#### Span

Span operations defining the tracing surface expected by the SDK.

Implementers map these calls to underlying tracing libraries.
Notes:
    Spans created via this interface should be context-manageable to align
    with common tracing DSLs.

#### Tracer

Entry point for creating and managing spans within a trace.

Notes:
    Tracers should be safe to share across threads and async tasks.

#### TracerProvider

Provider interface used to acquire tracer instances for subsystems.

Notes:
    Typically implemented by OpenTelemetry or custom tracer registries.

#### Counter

Simple counter metric.

Example:
    counter = Counter("requests")
    counter.increment()
    counter.increment(5)
    print(counter.value)  # 6

#### Histogram

Histogram metric for tracking distributions.

Example:
    histogram = Histogram("response_time")
    histogram.observe(0.123)
    histogram.observe(0.456)
    stats = histogram.statistics()

#### Gauge

Gauge metric (can go up or down).

Example:
    gauge = Gauge("memory_usage")
    gauge.set(1024)
    gauge.increment(512)
    print(gauge.value)  # 1536

#### Meter

Entry point for creating metric instruments scoped to a component.

Notes:
    Instruments created from a meter share the same resource and exporter settings.

#### MeterProvider

Provider interface for acquiring meters for instrumentation scopes.

Notes:
    Typically implemented by observability SDKs like OpenTelemetry.

#### Alert

Structured alert representation consumed by alerting adapters.

Notes:
    Alerts should be immutable snapshots of the triggering condition.

#### Alerter

Port describing how alerts are sent to external notification channels.

Notes:
    Implementations may integrate with email, chat, or incident platforms.

#### ObservabilityBootstrapper

Bootstrap interface for initialising observability subsystems.

Implementations typically wire up logging, tracing, metrics, and health checks
during application startup.

#### StreamMessageType

Types of streaming messages (technology-agnostic).

#### StreamMessage

Individual streaming message (domain value object).

#### ConnectionInfo

Information about a streaming connection (domain value object).

#### StreamProtocol

Port contract: Adapters implement streaming protocols.

#### StreamManagerProtocol

Port contract: Adapters implement connection management.

#### Entity

Base entity with identity.

#### ValueObject

Base value object (immutable).

#### AggregateRoot

Aggregate root with domain events.

#### DomainEvent

Base domain event.

#### VectorClient

Unified client for vector search with progressive embedding.

Provides a simple interface to:
- Generate embeddings across multiple providers (Vertex AI, OpenAI, local)
- Search across multiple backends (pgvector, Supabase, FAISS, LanceDB)
- Progressive embedding (on-demand generation for missing records)
- Hybrid search (semantic + keyword)

Example:
    ```python
    from vector_kit import VectorClient

    client = VectorClient(
        provider="vertex",
        backend_dsn="postgres://...",
    )

    # Progressive semantic search
    results = await client.search.semantic(
        query="machine learning frameworks",
        limit=20,
        ensure_embeddings=True,  # Generate missing embeddings
    )
    ```

#### EmbeddingProvider

Abstract base class for embedding providers.

#### IndexBackend

Abstract base class for vector index backends.

#### AnalyticsDependencyError

Raised when an analytics dependency is missing.

#### PortManager

Manages port allocation for agent processes.

Features:
- Thread-safe port allocation
- Port pool management
- Automatic release on timeout
- Tracking of port usage

#### HealthCheckResult

Health check result.

#### HTTPHealthCheck

HTTP endpoint health check.

#### PortHealthCheck

Port availability health check.

#### ManagedProcess

Concrete implementation of BaseProcess.

#### ProcessManager

Manages system processes and resource allocation.

#### ProcessFactory

Factory for creating process instances.

#### DefaultMonitor

Default monitor implementation.

#### MonitorFactory

Factory for creating monitors.

#### BaseMonitor

Abstract base class for process monitors.

Provides lifecycle management, signal handling, and multiple run modes. Subclass to
create custom monitors with specific behavior.

#### BaseProcess

Abstract base class for process wrappers.

Provides process lifecycle management with health checking and auto-restart
capabilities.

#### GoServiceOptions

Configuration options for building a Go service.

#### ServiceLauncher

Thin wrapper around ``ServiceOrchestrator`` for common CLI flows with optional Rich
TUI.

#### NextJSServiceOptions

Configuration options for building a Next.js service.

#### CodeAnalyticsOptions

Options controlling code analytics execution.

#### FunctionComplexity

Complexity metrics for a single function.

#### ComplexityReport

Aggregated complexity metrics for a single module or file.

#### ComplexityMetrics

Complete project-level complexity metrics (Morph-compatible).

#### DependencyEdge

Represents a directed dependency edge.

#### DependencyGraph

Represents the dependency graph of a codebase.

#### DependencyInfo

Complete project-level dependency information (Morph-compatible).

#### ArchitectureReport

Comprehensive architecture analysis report.

#### CodeAnalyticsReport

Unified analytics report combining complexity, dependencies, and architecture.

#### ArchitectureDetectorConfig

Configuration for architecture detection.

#### ArchitectureDetector

Advanced architecture pattern detector with extensible pattern library.

#### ArchitectureValidatorConfig

Configuration for architecture validation.

#### ArchitectureValidator

Validates architecture compliance and best practices.

#### PatternDetector

Advanced pattern detection tool.

#### DesignPatternDetector

Detects design patterns in code.

#### PatternRegistry

Registry for managing pattern detectors and patterns.

#### CustomPatternDetector

Custom pattern detector with configurable rules.

#### ArchitectureType

Types of architectural patterns.

#### DesignPatternType

Types of design patterns.

#### LayerType

Types of architectural layers.

#### PatternMatch

Represents a pattern match found in the codebase.

#### ArchitecturePattern

Represents an architectural pattern definition.

#### DesignPattern

Represents a design pattern definition.

#### LayerStructure

Represents the layer structure of a codebase.

#### ArchitectureMetrics

Architecture quality metrics.

#### PatternExtension

Abstract base class for pattern extensions.

#### MicroservicesPatternExtension

Extension for microservices architecture patterns.

#### DomainDrivenDesignExtension

Extension for Domain-Driven Design patterns.

#### ExtensionRegistry

Registry for managing pattern extensions.

#### AstNode

Simplified AST node representation.

#### TreeSitterAdapter



#### _TreeSitterAdapter



#### CodeEntity

Represents a code entity (function, class, method, etc.).

#### PythonASTParser

Parser for Python files using built-in AST module.

#### JavaScriptParser

Parser for JavaScript/TypeScript files using regex patterns.

#### PIIRedactor

Redactor for Personally Identifiable Information (PII) and sensitive data.

Supports redaction of:
- Passwords, API keys, tokens
- Credit card numbers
- Social Security Numbers
- Email addresses
- IP addresses
- Phone numbers
- Custom patterns

#### SecurityFilter

Logging filter that redacts sensitive information.

This filter automatically redacts PII and sensitive data from log messages
before they are written to handlers.

Example:
    import logging
    from pheno_logging.filters import SecurityFilter

    logger = logging.getLogger("app")
    logger.addFilter(SecurityFilter())

    # Sensitive data will be redacted
    logger.info("User password: secret123")
    # Output: "User password: [REDACTED]"

    logger.info("Credit card: 1234-5678-9012-3456")
    # Output: "Credit card: [REDACTED]"

#### LogHandler

Base interface for log handlers.

#### LogFormatter

Base interface for log formatters.

#### Monitor

Base interface for monitors.

#### LogRecord

Structured log record.

#### LogContext

Logging context for structured logging.

#### MetricPoint

A single metric data point.

#### LoggingError

Base exception for logging errors.

#### HandlerError

Raised when a log handler error occurs.

#### FormatterError

Raised when a log formatter error occurs.

#### MonitorError

Raised when a monitoring error occurs.

#### MetricsError

Raised when a metrics error occurs.

#### HealthCheckError

Raised when a health check error occurs.

#### LoggerImpl

Main logger implementation.

#### _JsonFormatter

Simple JSON formatter for Morph compatibility.

#### StructlogAdapter

Adapter to use structlog with pheno-logging interface.

This allows you to use structlog loggers through the pheno-logging
Logger interface, providing compatibility with both systems.

Example:
    logger = StructlogAdapter("my_service")
    logger.info("User logged in", user_id=123, ip="192.168.1.1")

#### ConsoleHandler

Console-based log handler.

#### HandlerRegistry

Central registry for log handlers.

#### FileHandler

File-based log handler.

#### SyslogHandler

Syslog-based log handler.

#### JSONHandler

JSON-formatted log handler.

#### ModelInfo

Information about the embedding model.

#### EmbeddingService

Unified embedding service (Morph-compatible).

Provides text embedding with caching and batch processing support.

#### OpenAIEmbeddings

OpenAI embeddings provider.

Requires: pip install openai

#### SentenceTransformerEmbeddings

Sentence Transformers embeddings provider (local).

Requires: pip install sentence-transformers

#### InMemoryEmbeddings

Simple in-memory embeddings for testing.

Generates random vectors for demonstration.

#### EmbeddingResult



#### BatchEmbeddingResult



#### VertexAIEmbeddingService

Service for generating Vertex AI (Gemini) embeddings with caching.

#### ProviderAdapter

Adapter that wraps an EmbeddingProvider in the Vertex-compatible API.

#### LiteLLMEmbeddingProvider

Embedder backed by `litellm.embedding` / `litellm.aembedding`.

Args:
    model: Embedding model identifier (e.g. ``"text-embedding-3-large"``)
    api_key: Optional API key (falls back to environment variables supported by litellm)
    litellm_kwargs: Additional kwargs forwarded to the litellm call

#### SentenceTransformersEmbeddingProvider

Embedding provider using HuggingFace sentence-transformers models.

Args:
    model_name: Sentence-transformers model to load
    cache_folder: Optional cache directory for model weights
    device: Device identifier ("cpu", "cuda", etc.)
    normalize_embeddings: Normalise output vectors (L2)
    encode_kwargs: Additional keyword arguments passed to ``encode``

#### QdrantVectorStore

Simple wrapper around Qdrant collections.

#### FaissVectorStore

Vector store backed by FAISS (IndexFlatL2).

#### Document

Document with embedding.

#### SearchResult

Single search result with similarity score.

#### VectorStore

Base vector store interface.

Example:
    store = FAISSVectorStore(dimension=384)

    await store.add_documents([
        Document(id="1", text="Hello", vector=vec1),
        Document(id="2", text="World", vector=vec2)
    ])

    results = await store.search(query_vector, k=5)

#### InMemoryVectorStore

Simple in-memory vector store.

#### ProgressiveEmbeddingService

Service that automatically generates embeddings on-demand during search operations.

#### SemanticSearch

Semantic search engine.

Combines embedding provider and vector store for semantic search.

Example:
    search = SemanticSearch(
        embedding_provider=OpenAIEmbeddings(),
        vector_store=FAISSVectorStore()
    )

    # Index documents
    await search.index_documents([
        "Python is a programming language",
        "JavaScript is used for web development"
    ])

    # Search
    results = await search.search("programming languages", k=5)

#### SearchResponse

Complete search response with results and metadata.

#### VectorSearchService

Service for performing vector similarity search on embedded content.

#### EnhancedVectorSearchService

Enhanced vector search service that automatically generates embeddings on-demand.

This service wraps the existing VectorSearchService and adds progressive embedding
capabilities, ensuring that search operations automatically include records that
don't have embeddings yet.

#### DeploymentStatusEnum

Deployment status enumeration.

#### DeploymentStatus

Enumeration of high-level deployment lifecycle states.

States mirror the internal pipeline steps and can be surfaced in TUIs or external
monitoring systems.

#### DeploymentEnvironmentEnum

Deployment environment enumeration.

#### DeploymentEnvironment

Deployment environment types.

#### DeploymentStrategyEnum

Deployment strategy enumeration.

#### DeploymentStrategy

Supported rollout strategies for provider-agnostic deployments.

#### ServiceStatusEnum

Service status enumeration.

#### ServiceStatus



#### ServicePort

Service port value object with protocol.

#### ServiceName

Service name value object with validation.

#### Email

Email address value object with validation.

#### URL

URL value object with validation.

#### ConfigKey

Configuration key value object.

#### ConfigValue

Configuration value value object.

#### UserId

User ID value object.

#### ServiceId

Service ID value object.

#### DeploymentId

Deployment ID value object.

#### ResourceInfo

Runtime information about a provisioned resource.

#### ProcessInfo

Information about a monitored process.

#### ProjectInfo

Information about a registered project.

#### ProjectRegistry

Registry for managing pheno-sdk project configurations.

#### UserNotFoundError

Raised when a user is not found.

#### UserAlreadyExistsError

Raised when attempting to create a duplicate user.

#### UserInactiveError

Raised when attempting to perform an action on an inactive user.

#### DeploymentNotFoundError

Raised when a deployment is not found.

#### DeploymentAlreadyExistsError

Raised when attempting to create a duplicate deployment.

#### InvalidDeploymentStateError

Raised when an invalid deployment state transition is attempted.

#### ServiceAlreadyExistsError

Raised when attempting to create a duplicate service.

#### InvalidServiceStateError

Raised when an invalid service state transition is attempted.

#### PortAlreadyInUseError

Raised when attempting to use a port that's already in use.

#### DomainError

Base exception for all domain errors.

#### BusinessRuleViolation

Raised when a business rule is violated.

#### EntityNotFoundError

Raised when an entity is not found.

#### EntityAlreadyExistsError

Raised when attempting to create a duplicate entity.

#### InvalidStateTransitionError

Raised when an invalid state transition is attempted.

#### InvariantViolationError

Raised when a domain invariant is violated.

#### UserCreated

Event emitted when a user is created.

#### UserUpdated

Event emitted when a user is updated.

#### UserDeactivated

Event emitted when a user is deactivated.

#### DeploymentCreated

Event emitted when a deployment is created.

#### DeploymentStarted

Event emitted when a deployment starts.

#### DeploymentCompleted

Event emitted when a deployment completes successfully.

#### DeploymentFailed

Event emitted when a deployment fails.

#### DeploymentRolledBack

Event emitted when a deployment is rolled back.

#### ServiceCreated

Event emitted when a service is created.

#### ServiceStarted

Event emitted when a service starts.

#### ServiceStopped

Event emitted when a service stops.

#### ServiceFailed

Event emitted when a service fails.

#### Configuration

Configuration entity.

Represents a configuration key-value pair in the system.
Configurations can be updated and have a history of changes.

Business Rules:
    - Configuration key must be unique
    - Configuration value can be any type
    - Configuration tracks creation and update times
    - Previous value is stored on update

#### Service

Service aggregate root.

Represents a running service in the infrastructure.
Manages service lifecycle and state transitions.

Business Rules:
    - Service must have unique name
    - Service must have valid port
    - State transitions must follow valid paths
    - Only stopped services can be started
    - Only running services can be stopped
    - Service emits events for all state changes

#### User

User aggregate root.

Represents a user in the system with identity, email, and name.
Users can be active or inactive.

Business Rules:
    - Email must be unique
    - Name cannot be empty
    - Inactive users cannot perform actions
    - User creation emits UserCreated event
    - User updates emit UserUpdated event
    - User deactivation emits UserDeactivated event

#### Deployment

Snapshot describing an individual deployment execution.

#### McpProvider

Protocol for MCP implementation providers.

Defines the contract for connecting to MCP servers and executing tools.
Implementations handle the actual MCP protocol communication.

Example:
    >>> provider = get_mcp_provider()  # Returns implementation
    >>> session = await provider.connect(server)
    >>> result = await provider.execute_tool(tool, {"param": "value"})
    >>> await provider.disconnect(session)

#### MonitoringProvider

Protocol for monitoring providers.

#### ToolRegistry

Protocol for tool registration and discovery.

Manages the registry of available MCP tools, allowing tools to be
registered, discovered, and retrieved by name or category.

Example:
    >>> registry = get_tool_registry()
    >>>
    >>> # Register tools
    >>> registry.register_tool(McpTool(
    ...     name="search",
    ...     description="Search documentation",
    ...     handler=search_handler
    ... ))
    >>>
    >>> # Discover tools
    >>> tools = registry.list_tools()
    >>> tool = registry.get_tool("search")

#### SessionManager

Manage user sessions with token and credential storage.

Combines TokenManager and CredentialStore for complete session management.

Example:
    session = SessionManager()

    # Store session
    session.create_session(
        "user123",
        tokens=TokenSet(access_token="..."),
        credentials={"email": "user@example.com"}
    )

    # Get session
    tokens = session.get_tokens("user123")
    email = session.get_credential("user123", "email")

    # End session
    session.end_session("user123")

#### ResourceSchemeHandler

Base class for resource scheme handlers.

#### ResourceProvider

Protocol for resource monitoring providers.

Implement this protocol to integrate with ResourceStatusWidget for
custom resource monitoring (database, cache, API limits, etc.).

Example:
    class DatabaseProvider:
        async def check_health(self) -> Dict[str, Any]:
            conn = await asyncpg.connect(self.dsn)
            start = time.perf_counter()
            await conn.fetchval("SELECT 1")
            latency = (time.perf_counter() - start) * 1000
            await conn.close()

            return {
                "connected": True,
                "latency_ms": latency,
                "type": "postgresql"
            }

#### Event

Runtime representation of a UI event.

#### SimpleEventBus

Simplified synchronous event bus for basic pub/sub scenarios.

This is a lighter-weight alternative to EventBus that runs handlers
synchronously and doesn't support wildcards or async operations.

Features:
- Synchronous event handlers
- Simple subscription management
- Minimal overhead
- Error isolation per handler

Example:
    bus = SimpleEventBus()

    @bus.on("user.created")
    def log_user_creation(event):
        print(f"User created: {event.data['email']}")

    bus.publish("user.created", {"email": "user@example.com"})

#### StoredEvent

Event stored in the event store.

#### EventStore

Event store for event sourcing and audit logging.

Features:
- Append-only event log
- Aggregate streams
- Event replay
- Multiple backends (in-memory, file-based)

Example:
    # In-memory store
    store = EventStore()

    # Append event
    event = StoredEvent(
        event_type="OrderPlaced",
        aggregate_id="order-123",
        aggregate_type="Order",
        data={"amount": 100, "items": 3},
        metadata={"user_id": "user-456"}
    )
    await store.append(event)

    # Get events for aggregate
    events = await store.get_stream("order-123")

    # Get all events of a type
    orders = await store.get_events(event_type="OrderPlaced")

    # File-based store
    file_store = EventStore(backend=FileEventStore(Path(".events")))
    await file_store.append(event)

#### RetryPolicy



#### WebhookStatus

Webhook delivery status.

#### WebhookDelivery

Webhook delivery record.

#### WebhookManager

Webhook delivery manager with retries and HMAC signing.

Features:
- Async HTTP delivery
- HMAC-SHA256 signatures
- Exponential backoff retries
- Delivery tracking
- Event callbacks

Example:
    manager = WebhookManager(secret="my-secret-key")

    # Register webhook
    webhook_id = await manager.deliver(
        url="https://example.com/webhook",
        event_type="order.placed",
        payload={"order_id": "123", "amount": 100}
    )

    # Check status
    delivery = manager.get_delivery(webhook_id)
    print(f"Status: {delivery.status}")

    # Register callback
    @manager.on_success
    async def handle_success(delivery):
        print(f"Delivered: {delivery.id}")

    # Process pending deliveries
    await manager.process_pending()

#### WebhookSigner

HMAC signature generator for webhooks.

#### WebhookReceiver

Webhook receiver with signature verification.

Example:
    receiver = WebhookReceiver(secret="my-secret-key")

    @app.post("/webhook")
    async def handle_webhook(request):
        # Verify signature
        payload = await request.body()
        signature = request.headers.get("X-Webhook-Signature")

        if not receiver.verify(payload, signature):
            return {"error": "Invalid signature"}, 401

        # Process webhook
        data = await request.json()
        await process_event(data)

        return {"status": "ok"}

#### CreateConfigurationDTO

DTO for creating a new configuration.

#### UpdateConfigurationDTO

DTO for updating a configuration.

#### ConfigurationDTO

DTO for configuration data.

#### ConfigurationFilterDTO

DTO for filtering configurations.

#### CreateServiceDTO

DTO for creating a new service.

#### UpdateServiceDTO

DTO for updating a service.

#### ServiceDTO

DTO for service data.

#### ServiceFilterDTO

DTO for filtering services.

#### ServiceHealthDTO

DTO for service health status.

#### CreateUserDTO

DTO for creating a new user.

#### UpdateUserDTO

DTO for updating a user.

#### UserDTO

DTO for user data.

#### UserFilterDTO

DTO for filtering users.

#### CreateDeploymentDTO

DTO for creating a new deployment.

#### UpdateDeploymentDTO

DTO for updating a deployment.

#### DeploymentDTO

DTO for deployment data.

#### DeploymentFilterDTO

DTO for filtering deployments.

#### DeploymentStatisticsDTO

DTO for deployment statistics.

#### CreateConfigurationUseCase

Use case for creating a new configuration.

#### UpdateConfigurationUseCase

Use case for updating a configuration.

#### GetConfigurationUseCase

Use case for getting a configuration by key.

#### ListConfigurationsUseCase

Use case for listing configurations.

#### CreateServiceUseCase

Use case for creating a new service.

#### StartServiceUseCase

Use case for starting a service.

#### StopServiceUseCase

Use case for stopping a service.

#### GetServiceUseCase

Use case for getting a service by ID.

#### ListServicesUseCase

Use case for listing services.

#### GetServiceHealthUseCase

Use case for getting service health status.

#### CreateUserUseCase

Use case for creating a new user.

#### UpdateUserUseCase

Use case for updating a user.

#### GetUserUseCase

Use case for getting a user by ID.

#### ListUsersUseCase

Use case for listing users.

#### DeactivateUserUseCase

Use case for deactivating a user.

#### CreateDeploymentUseCase

Use case for creating a new deployment.

#### StartDeploymentUseCase

Use case for starting a deployment.

#### CompleteDeploymentUseCase

Use case for completing a deployment.

#### FailDeploymentUseCase

Use case for failing a deployment.

#### RollbackDeploymentUseCase

Use case for rolling back a deployment.

#### GetDeploymentUseCase

Use case for getting a deployment by ID.

#### ListDeploymentsUseCase

Use case for listing deployments.

#### GetDeploymentStatisticsUseCase

Use case for getting deployment statistics.

#### EmailService

Email service protocol.

Defines the contract for sending emails. Adapters can implement this for different
email providers (SendGrid, AWS SES, SMTP, etc.).

#### NotificationService

Notification service protocol.

Defines the contract for sending notifications through various channels (push
notifications, SMS, webhooks, etc.).

#### MetricsService

Metrics service protocol.

Defines the contract for recording and querying metrics. Adapters can implement this
for different metrics backends (Prometheus, StatsD, CloudWatch, etc.).

#### EventPublisher

Event publisher protocol.

Defines the contract for publishing domain events. Adapters can implement this to
publish events to message queues, event stores, or other event-driven systems.

#### EventSubscriber

In-memory event subscriber.

#### Repository

Generic repository protocol.

Defines the contract for data persistence operations. All repositories should
implement this interface.

#### UserRepository

User repository protocol.

Defines the contract for user persistence operations.

#### DeploymentRepository

Deployment repository protocol.

Defines the contract for deployment persistence operations.

#### ServiceRepository

Service repository protocol.

Defines the contract for service persistence operations.

#### ConfigurationRepository

Configuration repository protocol.

Defines the contract for configuration persistence operations.

#### QueryHandler

Generic query handler protocol.

Defines the contract for handling queries in CQRS pattern. Queries are read-only
operations that return data.

#### UserQueryFilter

Filter criteria for user queries.

#### UserQueryResult

Result of a user query.

#### UserQuery

User query protocol.

Defines the contract for querying user data. Optimized for read operations with
denormalized data.

#### DeploymentQueryFilter

Filter criteria for deployment queries.

#### DeploymentQueryResult

Result of a deployment query.

#### DeploymentQuery

Deployment query protocol.

Defines the contract for querying deployment data.

#### ServiceQueryFilter

Filter criteria for service queries.

#### ServiceQueryResult

Result of a service query.

#### ServiceQuery

Service query protocol.

Defines the contract for querying service data.

#### CommandHandler

Represents a command handler with metadata.

#### CLIHandler

CLI handler protocol.

Defines the contract for CLI command handlers.

#### APIHandler

API handler protocol.

Defines the contract for REST/GraphQL API handlers.

#### MCPServerHandler

MCP (Model Context Protocol) server handler protocol.

Defines the contract for MCP server implementations.

#### EventListenerHandler

Event listener handler protocol.

Defines the contract for handling external events (webhooks, message queues).

#### ScheduledTaskHandler

Scheduled task handler protocol.

Defines the contract for handling scheduled/cron tasks.

#### CorrelationIdFilter

Logging filter to add correlation IDs to log records.

#### correlation_context

Context manager for scoped correlation ID management.

#### LRUCache

LRU Cache with O(1) get and set operations.

Example:
    cache = LRUCache(capacity=100)
    cache.set('key', 'value')
    value = cache.get('key')

#### BloomFilter

Bloom filter for probabilistic membership testing.

May return false positives but never false negatives.

Example:
    bf = BloomFilter(size=1000, num_hashes=3)
    bf.add("hello")
    bf.add("world")

    "hello" in bf  # True
    "goodbye" in bf  # False (probably)

#### CircularBuffer

Fixed-size circular buffer (ring buffer).

Example:
    buffer = CircularBuffer(capacity=3)
    buffer.append(1)
    buffer.append(2)
    buffer.append(3)
    buffer.append(4)  # Overwrites oldest item (1)

    list(buffer)  # [2, 3, 4]

#### TrieNode

Node in trie.

#### Trie

Trie data structure for efficient prefix-based operations.

Example:
    trie = Trie()
    trie.insert("hello")
    trie.insert("world")

    trie.search("hello")  # True
    trie.starts_with("hel")  # True
    trie.find_all_with_prefix("hel")  # ["hello"]

#### PriorityItem

Item for priority queue.

#### PriorityQueue

Priority queue implementation using heapq.

Lower priority numbers = higher priority (processed first).

Example:
    pq = PriorityQueue()
    pq.push("urgent", priority=1)
    pq.push("normal", priority=5)
    pq.push("low", priority=10)

    item = pq.pop()  # Returns "urgent"

#### Template

Simple string template with variable substitution.

Example:
    template = Template("Hello, {name}! You have {count} messages.")
    result = template.render(name="John", count=5)
    # "Hello, John! You have 5 messages."

#### TokenSet

Set of OAuth tokens.

Attributes:
    access_token: Access token
    refresh_token: Optional refresh token
    id_token: Optional ID token
    expires_at: Expiration timestamp (Unix time)
    scopes: List of granted scopes
    metadata: Additional metadata

#### CredentialStore

Secure credential storage for OAuth flows.

Stores credentials in memory with optional file persistence.
For production, use a proper secret manager (e.g. AWS Secrets Manager).

Example:
    store = CredentialStore()

    # Store credentials
    store.set("username", "user@example.com")
    store.set("password", "secret123", sensitive=True)

    # Retrieve credentials
    username = store.get("username")
    password = store.get("password")

    # Persist (WARNING: credentials in plaintext)
    store.save_to_file(".credentials")

#### LoggerContext

Context manager for temporary logger configuration.

Example:
    with LoggerContext("mymodule", logging.DEBUG):
        # Code here logs at DEBUG level
        pass
    # Back to original level

#### QuietLogger

Context manager that temporarily silences chatty loggers.

#### ConfigBase

Lightweight dataclass base with YAML round-tripping helpers.

#### ServerConfig

Convenience schema for describing server runtime settings.

#### AuthConfig

Simple authentication configuration container.

#### EnvLoader

Aggregate environment variables from project roots and explicit files.

#### MetricsReporter

Format and report metrics.

Example:
    collector = MetricsCollector()
    # ... collect metrics ...

    reporter = MetricsReporter(collector)
    print(reporter.format_text())

#### MetricValue

Base metric value with metadata.

Attributes:
    name: Metric name
    value: Metric value
    timestamp: Unix timestamp
    tags: Optional tags for filtering

#### MetricsAggregator

Aggregate metrics across multiple agents and time periods.

#### BearerAuth

Bearer token authentication.

Example:
    auth = BearerAuth('my-token')
    headers = auth.get_headers()
    # {'Authorization': 'Bearer my-token'}

#### BasicAuth

HTTP Basic authentication.

Example:
    auth = BasicAuth('username', 'password')
    headers = auth.get_headers()
    # {'Authorization': 'Basic dXNlcm5hbWU6cGFzc3dvcmQ='}

#### APIKeyAuth

API key authentication.

Example:
    auth = APIKeyAuth('my-api-key')
    headers = auth.get_headers()
    # {'X-API-Key': 'my-api-key'}

    # Custom header name
    auth = APIKeyAuth('my-key', header_name='X-Custom-Key')

#### QueryParamAuth

Query parameter authentication.

Example:
    auth = QueryParamAuth('my-api-key', param_name='api_key')
    params = auth.get_params()
    # {'api_key': 'my-api-key'}

#### HeaderManager

Manage HTTP headers with smart defaults.

Example:
    headers = HeaderManager()
    headers.set('X-API-Key', 'secret')
    headers.add_json_content_type()
    request_headers = headers.to_dict()

#### TaskQueue

Async task queue with concurrency control.

Example:
    queue = TaskQueue(max_workers=5)
    await queue.start()

    await queue.enqueue(my_async_function, arg1, arg2)

    await queue.stop()

#### RateLimitSemaphore

Rate limiting semaphore.

Example:
    limiter = RateLimitSemaphore(max_calls=10, time_window=60)

    async with limiter:
        await make_api_call()

#### BoundedSemaphore

Bounded semaphore for concurrency control.

Example:
    sem = BoundedSemaphore(5)

    async with sem:
        await process_item()

#### EventStoreBackend

Protocol for event store backends.

#### InMemoryEventStore

In-memory event store for testing and development.

#### FileEventStore

File-based event store for persistence.

#### PerformanceMetrics

Performance metrics.

#### ProviderBenchmark

Benchmark results for a provider/model combination.

Stores comprehensive benchmarking data including:
- Performance metrics (response time percentiles, throughput)
- Reliability metrics (success rate, error rate, timeouts)
- Cost metrics (tokens per second, cost per token)
- Resource usage (memory, CPU efficiency)

#### OperationStats

Statistical analysis for operation timings.

Provides statistical measures including:
- Central tendency (mean, median)
- Percentiles (p95, p99)
- Range (min, max)
- Sample count

#### PerformanceMonitor

Central performance monitoring system.

Features:
- Real-time performance metrics collection
- Resource usage tracking (CPU, memory)
- Operation timing statistics
- Context manager support (sync & async)
- Correlation ID integration for distributed tracing
- Weak references for tracked objects

#### MemoryLeakDetector

Detect potential memory leaks by analyzing memory trends.

#### Benchmarker

Performance benchmarking utilities.

#### ValidationRule

Validation rule.

#### Validator

Custom validator builder.

Example:
    validator = Validator()
    validator.add_rule(lambda x: len(x) > 3, "Must be longer than 3")
    validator.add_rule(lambda x: x.isalnum(), "Must be alphanumeric")

    result = validator.validate("abc123")

#### MemoryOptimizer

Coordinate memory optimisation strategies.

#### LargeFileHandler

Read large files without exhausting memory.

#### MemoryMonitor

Track process and system level memory usage.

#### TextCompressor

Utility methods for compressing text.

#### ContextManager

Store and retrieve compressed contexts.

#### MemoryStats

Snapshot of memory usage information.

#### CompressionResult

Outcome of a compression operation.

#### GarbageCollector

Convenience helpers around Python's GC.

#### QueryFilter

Fluent query filter builder.

#### QueryCache

Simple in-memory cache keyed by operation parameters.

#### ResponseValidator

Validate MCP tool responses and extract common fields.

#### FieldValidator

Generic field validator with common validation patterns.

Provides standard validation for common field types and patterns.

#### DataGenerator

Generate test data for entities with guaranteed uniqueness.

#### TimeoutManager

Manage test execution timeouts and diagnostics.

#### WaitStrategy

Wait strategies for retry delays.

#### PerformanceTracker

Track real-time performance metrics.

#### SupabaseDatabaseAdapter

Supabase database adapter with caching and RLS support.

#### DatabaseAdapter

Abstract interface for database adapters.

#### WorkflowStatus

Workflow execution status.

#### WorkflowStep

A step in a workflow.

#### WorkflowContext

Context object available during workflow execution.

#### Workflow

Simple workflow definition.

Example:
    workflow = Workflow("process_data")

    workflow.add_step("fetch", fetch_data)
    workflow.add_step("transform", transform_data)
    workflow.add_step("save", save_data)

    engine = WorkflowEngine()
    await engine.execute(workflow, {"input": "data"})

#### SagaStatus

Saga execution status.

#### SagaStep

A step in a saga with action and compensation.

Example:
    step = SagaStep(
        name="reserve_inventory",
        action=lambda ctx: inventory.reserve(ctx["order_id"]),
        compensation=lambda ctx: inventory.release(ctx["order_id"])
    )

#### SagaContext

Saga execution context.

#### Saga

Saga pattern for distributed transactions with compensation.

A saga is a sequence of local transactions where each transaction
updates data within a single service. If a transaction fails, the
saga executes compensating transactions to undo the completed steps.

Example:
    # Create saga
    saga = Saga("process_order")

    # Add steps
    saga.add_step(
        name="reserve_inventory",
        action=lambda ctx: inventory.reserve(ctx["order_id"]),
        compensation=lambda ctx: inventory.release(ctx["order_id"])
    )

    saga.add_step(
        name="charge_payment",
        action=lambda ctx: payment.charge(ctx["amount"]),
        compensation=lambda ctx: payment.refund(ctx["transaction_id"])
    )

    saga.add_step(
        name="ship_order",
        action=lambda ctx: shipping.ship(ctx["order_id"]),
        compensation=lambda ctx: shipping.cancel(ctx["shipment_id"])
    )

    # Execute saga
    executor = SagaExecutor()
    result = await executor.execute(saga, {"order_id": "123", "amount": 100})

#### SagaExecutor

Executes sagas with automatic compensation on failure.

Features:
- Sequential execution of steps
- Automatic compensation on failure
- Retry logic for failed steps
- Timeout support
- Async execution

Example:
    executor = SagaExecutor()

    # Execute saga
    result = await executor.execute(saga, initial_data)

    # Check result
    if result.status == SagaStatus.COMPLETED:
        print("Success!")
    elif result.status == SagaStatus.COMPENSATED:
        print("Failed and compensated")

#### SagaOrchestrator

Orchestrates multiple sagas with dependencies.

Example:
    orchestrator = SagaOrchestrator()

    # Register sagas
    orchestrator.register_saga("process_order", order_saga)
    orchestrator.register_saga("update_inventory", inventory_saga)

    # Execute with dependencies
    await orchestrator.execute_with_deps(
        "process_order",
        data={"order_id": "123"},
        depends_on=["update_inventory"]
    )

#### Transition

State transition.

#### State

State definition.

#### StateMachine

State machine implementation.

Example:
    # Define states
    sm = StateMachine(initial_state="draft")

    # Add states
    sm.add_state("draft")
    sm.add_state("submitted")
    sm.add_state("approved")
    sm.add_state("rejected")

    # Add transitions
    sm.add_transition("draft", "submitted", "submit")
    sm.add_transition("submitted", "approved", "approve")
    sm.add_transition("submitted", "rejected", "reject")

    # Trigger events
    sm.trigger("submit")
    print(sm.current_state)  # "submitted"

#### ScheduledJob

Scheduled job definition.

#### WorkflowScheduler

Simple workflow scheduler.

Features:
- Interval-based scheduling
- Cron-like scheduling (basic)
- Async job execution
- Job management

Example:
    scheduler = WorkflowScheduler()

    # Schedule every 5 minutes
    scheduler.schedule_interval(
        "cleanup",
        cleanup_handler,
        minutes=5
    )

    # Start scheduler
    await scheduler.start()

#### AgentStatus



#### Agent

Represents an individual agent in the system.

#### Orchestrator

Orchestrate multiple agents with dependencies.

#### WorkflowMetrics

Collect and report workflow metrics.

Example:
    metrics = WorkflowMetrics()

    metrics.record_start("process_order", "exec-123")
    # ... workflow executes ...
    metrics.record_complete("exec-123", status="success")

    stats = metrics.get_stats("process_order")
    print(f"Success rate: {stats['success_rate']}")

#### TaskComplexity

Task complexity levels for routing decisions.

#### TaskType

Types of development tasks.

#### ExecutionStrategy

Strategy for task execution.

#### AgentType

Types of agents in the system.

#### TaskRequest

Represents a development task request.

#### AgentCapability

Capabilities of an agent.

#### HybridOrchestrator

Main orchestrator that coordinates multiple agents and strategies to provide optimal
automated task execution with cost optimization and pattern-based guidance.

#### Pattern

Represents a proven development pattern.

#### PatternUsageStats

Tracks pattern usage statistics.

#### PatternEngine

Provides proven SWE-bench patterns and methodologies to guide task execution for
optimal success rates.

#### CostStrategy

Represents a cost optimization strategy.

#### UsageMetrics

Tracks usage metrics for cost optimization.

#### RoutingOptimizer

Optimizes model routing decisions based on cost, performance, and budget
constraints.

#### BudgetOptimizer

Optimizes budget allocation and spending patterns.

#### CostOptimizer

Provides intelligent cost optimization using subscription management, caching, and
smart routing strategies.

#### CostAwareWorkflow

Integrates cost optimization into workflow execution.

Provides hooks and utilities for embedding cost-aware decisions throughout the task
execution pipeline.

#### TenantContext

Represents a tenant's isolated context.

#### AgentManager

Manages multiple agents with multi-tenancy support.

Coordinates agent registration, task routing, and load balancing.

#### AgentTaskConfig

Configuration for agent task execution.

#### TaskExecutionContext

Context for task execution with runtime information.

#### AgentTaskRequest

Request to create and execute an agent task.

#### AgentTaskResult

Result of agent task execution.

#### PortAllocation

Port allocation information.

#### AgentTaskManager

Advanced Agent Task Manager with enterprise features.

This manager provides:
- Task lifecycle management
- Redis/in-memory persistence
- Port allocation
- Metrics and telemetry
- Task queueing with backpressure
- Integration with existing AgentManager

Designed to be <500 lines with modular components.

#### WorkflowExecutionResult

Result of a workflow execution.

#### HumanApprovalRequest

Request for human approval in a workflow.

#### ApprovalDecision

Human approval decision.

#### TemporalWorkflowClient

Client for managing Temporal workflows with agent orchestration features.

#### workflow



#### Client



#### TLSConfig



#### BaseWorkflow

Base class for Temporal workflows.

#### VercelDeploymentProvider

Vercel-specific deployment implementation.

#### VercelConfigProvider

Vercel-specific configuration management.

#### HTTPHealthCheckProvider

HTTP-based health check implementation.

#### AdvancedHealthChecker

Advanced health checking with custom validators.

#### PlatformAdapter



#### LocalProcessConfig

Declarative configuration for a local process to manage.

#### ReadyProbe

Async hook used to determine when a process is ready.

#### LocalServiceManager

Spawn and supervise a collection of local development processes.

#### NVMSParser

Parse Byteport NVMS format.

#### _ProviderRegistry

Thread-safe provider registry implementation.

This is a singleton that manages all registered cloud providers.

#### ProviderInfo

Detailed information about a registered provider.

#### CloudError

Base error type for all cloud provider errors.

#### QuotaError

Resource or rate limits exceeded.

#### ConflictError

Resource conflict (e.g., already exists).

#### ProvisioningError

Resource creation/modification failed.

#### InternalProviderError

Provider-side error.

#### NotSupportedError

Operation not supported by provider.

#### DeploymentConfig

Comprehensive deployment configuration sent to providers.

#### DeploymentResult

Result of a deployment operation.

#### DeploymentProvider

Abstract base class for deployment providers.

This defines the interface that all deployment providers must implement. Platform-
specific implementations (Vercel, AWS, etc.) inherit from this.

#### HealthCheckProvider

Abstract base class for health check providers.

#### ServerProvider

Abstract base class for server providers.

#### TunnelProvider

Protocol for tunnel service providers.

Implement this protocol to integrate with TunnelStatusWidget for
custom tunnel monitoring solutions.

Example:
    class NgrokProvider:
        async def get_status(self) -> Dict[str, Any]:
            response = requests.get("http://localhost:4040/api/tunnels")
            data = response.json()
            return {
                "active": bool(data.get("tunnels")),
                "url": data["tunnels"][0]["public_url"],
                "type": "ngrok"
            }

#### ConfigurationProvider

Abstract base class for configuration providers.

#### PackageInfo

Metadata for a pheno-sdk package.

#### PhenoVendor

Vendoring manager for pheno-sdk packages.

#### AlertAction

Action to perform when an alert triggers.

#### AlertConfig

Configuration describing alert thresholds and actions.

#### ScalePolicy

Policy governing how automatic scaling adjustments occur.

#### ScaleConfig

Scaling configuration applied to scalable resources.

#### PoolConfig

Connection pool configuration for database resources.

#### MetricOptions

Options controlling metric retrieval windows and filters.

#### Metric

Single data point within a time-series metric.

#### CostEstimate

Estimated cost projection for planned resource usage.

#### Cost

Actual cost incurred for resource consumption.

#### TimeRange

Inclusive time range used for metrics and log queries.

#### BackupConfig

Backup configuration including retention and scheduling.

#### Backup

Metadata describing a specific backup artifact.

#### Migration

Database migration.

#### ResourceType

Canonical resource type identifiers used across providers.

#### DeploymentState

High-level state machine describing resource deployment lifecycle.

#### Capability

Optional provider capabilities surfaced by CloudProvider.get_capabilities.

#### LogOptions

Options controlling how logs are fetched from providers.

#### LogStream

Protocol for log streams.

#### Region

Geographic region available for resource provisioning.

#### ProviderMetadata

Metadata describing a provider's capabilities and supported regions.

#### HealthCheckConfig

Configuration describing how provider health checks should behave.

#### HealthCheckStatus

Result of executing a health check against a resource.

#### ResourceConfig



#### Endpoint

Describes a network endpoint exposed by a resource.

#### ResourceFilter

Filter criteria used when listing resources across providers.

#### ResourceDependency

Declarative dependency relationship between resources.

#### RollbackConfig

Parameters controlling automated rollback behaviour after failures.

#### DeploymentSource

Configuration describing the source artifacts used for deployments.

#### DeploymentError

Structured error information returned when deployments fail.

#### InstanceInfo

Runtime information for a single resource instance.

#### ProjectConfig

Control Center project configuration built on the shared project model.

#### ProjectDeployment

Snapshot describing the state of a deployed project across providers.

#### ProjectStatus

Aggregated status and cost information for a project.

#### Scalable



#### Loggable



#### Executable



#### Backupable



#### Monitorable



#### ProviderRegistry

Specialized registry for providers with priority-based resolution.

#### DatabaseProvider

Protocol for database monitoring implementations.

Implement this protocol to integrate database monitoring into the widget.
Supports any database system (PostgreSQL, MySQL, MongoDB, etc.).

Example:
    class PostgreSQLProvider:
        def __init__(self, pool):
            self.pool = pool

        async def get_pool_stats(self) -> Dict[str, int]:
            return {
                "active": self.pool.get_size() - self.pool.get_idle_size(),
                "idle": self.pool.get_idle_size(),
                "total": self.pool.get_size(),
                "max": self.pool.get_max_size()
            }

        async def get_query_latency(self) -> float:
            start = time.perf_counter()
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return (time.perf_counter() - start) * 1000

        async def check_health(self) -> bool:
            try:
                async with self.pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                return True
            except Exception:
                return False

#### DeploymentOrchestrator

High-level orchestrator responsible for multi-provider deployments.

#### CloudProvider

Contract that Pheno cloud providers must satisfy.

#### VercelClient

Vercel API client.

#### FlyClient

Fly.io API client.

#### GeminiClient

Client for interacting with Google's Gemini API.

#### GoogleAdapter

Adapter for Google Gemini models implementing the LLM port.

This adapter provides a consistent interface for Gemini models regardless of the
underlying API changes.

#### OpenAIProvider

OpenAI provider for LLM content generation.

#### ClaudeClient

Client for interacting with Anthropic's Claude API.

#### AnthropicAdapter

Adapter for Anthropic Claude models implementing the LLM port.

This adapter provides a consistent interface for Claude models regardless of the
underlying API changes.

#### MCPServer

Model Context Protocol server for Pheno SDK.

Exposes resources, tools, and prompts for AI assistants to interact with the Pheno
SDK through the MCP protocol.

#### InMemoryUserRepository

In-memory implementation of UserRepository.

#### InMemoryDeploymentRepository

In-memory implementation of DeploymentRepository.

#### InMemoryServiceRepository

In-memory implementation of ServiceRepository.

#### InMemoryConfigurationRepository

In-memory implementation of ConfigurationRepository.

#### RedisEventPublisher

Redis-based event publisher implementation.

Publishes events to Redis channels for distributed consumption. Requires redis-py
library and a Redis server.

#### InMemoryEventPublisher

In-memory event publisher implementation.

Simple event publisher that stores events in memory and delivers them to registered
subscribers. Useful for testing and single-process applications.

Implements EventPublisher, EventSubscriber, and EventBus ports.

#### FailDeploymentRequest

Request model for failing a deployment.

#### RollbackDeploymentRequest

Request model for rolling back a deployment.

#### UserModel

SQLAlchemy model for User entity.

#### DeploymentModel

SQLAlchemy model for Deployment entity.

#### ServiceModel

SQLAlchemy model for Service entity.

#### ConfigurationModel

SQLAlchemy model for Configuration entity.

#### UserMapper

Mapper for User entity and UserModel.

#### DeploymentMapper

Mapper for Deployment entity and DeploymentModel.

#### ServiceMapper

Mapper for Service entity and ServiceModel.

#### ConfigurationMapper

Mapper for Configuration entity and ConfigurationModel.

#### SQLAlchemyUserRepository

SQLAlchemy implementation of UserRepository.

#### SQLAlchemyDeploymentRepository

SQLAlchemy implementation of DeploymentRepository.

#### SQLAlchemyServiceRepository

SQLAlchemy implementation of ServiceRepository.

#### SQLAlchemyConfigurationRepository

SQLAlchemy implementation of ConfigurationRepository.

#### ConfigurationCommands

Configuration management commands for CLI.

#### ServiceCommands

Service management commands for CLI.

#### UserCommands

User management commands for CLI.

#### DeploymentCommands

Deployment management commands for CLI.

#### TOTPAdapter

Minimal TOTP adapter placeholder.

#### EmailMFAAdapter

Simple email MFA adapter placeholder.

#### SMSMFAAdapter

Minimal SMS MFA adapter placeholder.

#### PushNotificationAdapter

Minimal push notification adapter placeholder.

#### AuthKitProvider

AuthKit aware OAuth2 provider with sensible defaults.

#### OAuth2GenericProvider

OAuth2 provider that supports any compliant authorization server.

#### Auth0Provider

Auth0 aware OAuth2 provider.

#### AsyncContext

Async context manager for testing.

Provides utilities for managing async resources in tests.

#### RepositoryConfig

Configuration for repository factory.

#### InMemoryRepository

Generic in-memory repository for testing.

Replaces multiple specific repository implementations with a single
configurable class.

Example:
    >>> # Instead of InMemoryUserRepository, InMemoryDeploymentRepository, etc.
    >>> user_repo = InMemoryRepository[User](id_field="id")
    >>> deployment_repo = InMemoryRepository[Deployment](id_field="id")
    >>>
    >>> # Use the same interface
    >>> await user_repo.save(user)
    >>> found = await user_repo.find_by_id(user_id)

#### InMemoryEventBus

Generic in-memory event bus for testing.

Replaces multiple event bus implementations.

#### MockService

Generic mock service for testing.

Provides a simple way to mock any service with configurable responses.

#### MockHTTPResponse

Mock HTTP response for testing.

Example:
    response = MockHTTPResponse(
        status_code=200,
        json_data={"message": "success"},
        headers={"Content-Type": "application/json"}
    )

#### MockHTTPServer

Mock HTTP server for testing.

Allows registering mock responses for specific URLs.

Example:
    server = MockHTTPServer()
    server.add_response("GET", "/users", json_data={"users": []})

    response = server.request("GET", "/users")
    assert response.json_data == {"users": []}

#### MockTextualApp



#### AiocacheAdapter

Wrap an aiocache cache to satisfy CacheProtocol.

#### LruCache

Async-friendly LRU cache with optional TTL and metrics instrumentation.

#### CacheProtocol

Minimal async cache protocol used by analytics utilities.

#### NullCache

No-op cache implementation.

#### CacheMetricsProtocol

Optional metrics hooks for cache implementations.

#### NullCacheMetrics

Fallback metrics collector.

#### StorageClient

Universal storage client.

Provides unified interface across storage providers.

Example:
    # Local storage
    client = StorageClient(LocalStorageProvider())

    # S3 storage
    client = StorageClient(S3StorageProvider(bucket="my-bucket"))

    # Upload file
    file = await client.upload("test.txt", b"Hello World")

    # Download file
    data = await client.download("test.txt")

    # Get presigned URL
    url = await client.get_url("test.txt", expires_in=3600)

#### StoredFile

Stored file metadata.

#### StorageProvider

Base storage provider interface.

Example:
    provider = S3StorageProvider(bucket="my-bucket")

    # Upload file
    file = await provider.upload("path/to/file.txt", data)

    # Download file
    data = await provider.download("path/to/file.txt")

    # Delete file
    await provider.delete("path/to/file.txt")

#### LocalStorageProvider

Local filesystem storage provider.

Example:
    provider = LocalStorageProvider(base_path="./storage")
    file = await provider.upload("test.txt", b"Hello")

#### InMemoryStorageProvider

In-memory storage provider for testing.

#### SupabaseStorageBackend

Supabase-based storage backend.

#### LocalStorageBackend

Local filesystem-based storage backend.

#### S3StorageBackend

AWS S3-based storage backend.

#### MetricCategory

Categories of metrics tracked for each request.

#### RequestContext

Captures request context at the time routing begins.

#### ModelSelection

Details about the model selection step.

#### ModelPerformance

Quantitative metrics captured after the response is produced.

#### QualityAssessment

Optional human or automated quality signals.

#### MetricsRecord

Flattened metrics payload ready for persistence.

#### PartialMetrics

In-flight metrics before they are flushed to storage.

#### MetricsStorage

Protocol for persisting metrics records.

#### NoOpMetricsStorage

Fallback storage that discards metrics.

#### SqliteMetricsStorage

SQLite-backed storage for metrics records.

#### MetricSeries

A series of metric points.

#### MetricsRegistry

Registry for managing multiple metrics collectors.

Provides a centralized way to manage and query metrics from different components and
services.

#### DashboardPanel

A dashboard panel configuration.

#### Dashboard

A dashboard configuration.

#### DashboardProvider

Protocol for dashboard data providers.

#### DashboardManager

Manages dashboards and their data providers.

Consolidates dashboard functionality from infra/monitoring, MCP QA, and
observability stacks into a unified interface.

#### HealthResult

Result of a health check.

#### HealthProvider

Protocol for health check providers.

#### EventHandler

Synchronous handler signature.

#### EventEmitter

Emits events to registered handlers.

Consolidates event emission from infra/monitoring, MCP QA, and observability stacks
into a unified interface.

#### EventCollector

Collects events from multiple sources.

Provides a centralized way to collect and process events from different components
and services.

#### CommandResult

Result of command execution.

#### CommandConfig

Configuration for command execution.

#### CommandExecutor

High-level command executor that combines CLI bridge and router.

Provides a simple interface for executing commands with automatic routing,
validation, and result handling.

#### CommandRunner

High-level command runner with monitoring and scheduling.

Provides a higher-level interface for command execution with monitoring, scheduling,
and result tracking.

#### MonitoringConfig

Configuration for monitoring components.

#### MonitoringManager

Unified monitoring manager.

Coordinates all monitoring components including metrics, events, dashboards, and
health checks. Provides a single interface for monitoring across the platform.

#### DashboardAdapter

Adapter for dashboard components.

Bridges existing dashboard systems with the unified monitoring layer.

#### InfraMonitoringAdapter

Adapter for infrastructure monitoring components.

Bridges existing infra/monitoring components with the unified monitoring layer.

#### MCPQAMonitoringAdapter

Adapter for MCP QA monitoring components.

Bridges existing MCP QA monitoring with the unified monitoring layer.

#### CLIMonitoringAdapter

Adapter for CLI monitoring components.

Bridges existing CLI monitoring with the unified monitoring layer.

#### UIConfig

UI-related configuration.

#### TemplateConfig

Template-related configuration.

#### IntegrationConfig

External integration configuration.

#### DevConfig

Development-related configuration.

#### BuildConfig

Build-related configuration.

#### WorkspaceConfig

Workspace-related configuration.

#### ContextConfig

Configuration for a specific context (atoms, zen, byteport, etc.).

#### ContextSystemConfig

Configuration for the context system.

#### PhenoConfig

Main configuration model for Pheno-CLI.

#### ContextDetector

Detects the appropriate context for the CLI based on various signals.

#### PhenoContext

Context object passed between CLI commands.

#### WireframeStyle

Predefined wireframe styles.

#### BaseWireframe

Base wireframe with common layout patterns.

#### SetupWireframe

Wireframe for project setup and configuration.

#### DeploymentWireframe

Wireframe for deployment operations with progress tracking.

#### ProjectWireframe

Wireframe for project management and overview.

#### ConfigurationWireframe

Wireframe for configuration management.

#### MonitoringWireframe

Wireframe for system monitoring and observability.

#### WireframeApp

App wrapper for running wireframes.

#### PhenoControlCenter

Main Pheno Control Center orchestrator.

Integrates all components to provide a unified control interface for managing
multiple pheno-sdk projects.

#### PhenoControlCenterApp

Textual-based TUI application for Pheno Control Center.

#### CLIBridge

Bridge for executing CLI commands with streaming output capture.

Provides:
- Real-time output streaming
- Environment context switching
- Command history and autocomplete data
- Process lifecycle management

#### CommandRouter

Router for dispatching commands to appropriate project contexts.

Provides routing logic for pheno-cli commands to different projects with environment
context switching and command preprocessing.

#### PhenoError

Base exception for Pheno-CLI errors.

#### ProjectError

Project-related errors.

#### ConfigError

Configuration-related errors.

#### ProjectSetup

Wrapper for our existing ProjectSetup class.

#### TemplateManager

Load and render HTML templates for fallback server responses.

#### DeploymentApp



#### TUIMonitor

TUI monitor with command input and scrollable logs.

Provides:
- Multi-project monitoring display
- Interactive command input
- Scrollable log panels
- Real-time status updates

#### MonitorEngine

Core monitoring engine that aggregates process and resource state from multiple
projects and provides unified views for different UIs.

#### SimpleTUIMonitor

Simple fallback TUI monitor using basic console output.

#### MetricsTable

Live metrics table widget.

Features:
- Real-time metric updates
- Color-coded status based on thresholds
- Trend indicators
- Sparkline charts
- Historical data tracking

#### DataGrid

Configurable data grid with sorting and filtering.

#### ComponentTheme

Predefined component themes.

#### ComponentConfig

Configuration for TUI components.

#### LogViewer

Advanced log viewer widget with filtering and search.

Features:
- Real-time log streaming
- Level-based filtering
- Search with highlighting
- Auto-scroll toggle
- Export to file

#### ActionPanel

Panel with configurable action buttons.

#### FormBuilder

Dynamic form builder with validation.

#### NotificationArea

Notification area for alerts and messages.

#### ProgressWidget

Multi-task progress widget with ETA calculation.

Features:
- Track multiple concurrent tasks
- Calculate ETA for each task
- Show overall progress
- Display task statistics
- Visual progress bars

#### _Fallback

Simple placeholder for textual widgets when not installed.

#### _Reactive

Mimic textual's reactive descriptor.

#### StatusIndicator

Configurable status indicator with different states.

#### DeploymentMonitor

Textual widget that renders real-time deployment status.

When Textual is unavailable, the class degrades to a lightweight shim so the rest of
the application can still import it.

#### DeploymentStage

Mutable record describing a single stage within a deployment pipeline.

Tracks timing, progress percentage, and log output so UI components and callbacks
can present rich status updates.

#### BaseDeployment

Abstract deployment pipeline coordinating staged execution and callbacks.

Subclasses define the concrete stages and the logic required to execute them. The
base class handles progress aggregation, callbacks, and error handling.

#### SystemServiceDeployment

Deployment pipeline for installing and configuring system services.

Designed for platforms using ``systemd`` or similar init systems. The
pipeline assumes elevated permissions are handled by the caller.

#### DockerDeployment

Deployment pipeline for building, testing, and publishing Docker images.

Integrates with the local Docker CLI and supports tagging for custom registries.

#### NPMDeployment

Deployment pipeline for publishing JavaScript/TypeScript packages to NPM.

Handles dependency installation, test execution, building, and publishing with
optional dry-run support.

#### PyPIDeployment

Deployment pipeline tailored for publishing Python packages to PyPI.

Executes validation, testing, build, upload, and verification stages with optional
support for TestPyPI during dry runs.

#### EnvironmentManager

Manages environment configuration for MCP servers.

#### CommandEngine

Unified command execution engine.

Provides comprehensive command execution with subprocess management, progress
tracking, error handling, and TUI integration.

#### ValidationStatus

Validation status.

#### ValidationResult

Validation result.

#### ProjectValidator

Validates project structure and configuration.

Provides comprehensive validation for different project types to ensure commands can
execute successfully.

#### CommandStatus

Status of command execution.

#### CommandStage

Represents a stage in command execution.

#### ParsedCommand

Result of command parsing.

#### CommandParser

Parses command strings and lists into structured components.

#### CommandComposer

Composes command strings and lists from structured components.

#### OutputFormat

Output format for command results.

#### ExecutionPipeline

Manages command execution workflows and process orchestration.

#### OrchestrationStatus

Status of orchestration.

#### OrchestrationStep

A step in an orchestration workflow.

#### OrchestrationResult

Result of orchestration execution.

#### ProcessOrchestrator

Advanced process orchestrator for complex workflows.

Provides dependency management, parallel execution, retry logic, and workflow
coordination for complex command sequences.

#### CommandValidator

Base class for command validators.

#### CommandCallback

Base class for command execution callbacks.

#### SecurityValidator

Validates command security and safety.

#### OutputValidator

Validates command output and result content.

#### LoggingCallback

Progress callback that forwards updates to the Python logging subsystem.

Logging level choices map to stage lifecycle events (info for start/end, debug for
progress, error for failures).

#### NotificationCallback

Sends notifications for command events.

#### ResultProcessor

Processes and transforms command results.

#### LoggingMixin

Mixin class to add logging capabilities to CLI frameworks.

#### MCPCLIFramework

CLI framework specialized for MCP servers.

Provides MCP-specific functionality:
- Automatic pheno-sdk path injection
- Environment management
- MCP endpoint configuration
- Service orchestration integration

#### CLIFramework

Base CLI framework for Pheno SDK projects.

Provides common functionality for building command-line interfaces:
- Subcommand routing
- Argument parsing
- Command registration
- Help generation
- Error handling

#### ZenMCPEntryPoint

Entry point constructor for the Zen MCP server.

Provides Zen-specific defaults and configuration:
- Default port: 8000
- Default domain: zen.kooshapari.com
- Zen-specific service configuration
- Integration with FastMCP and pheno-sdk packages

#### AtomsMCPEntryPoint

Entry point constructor for the Atoms MCP server.

Provides Atoms-specific defaults and configuration:
- Default port: 50002
- Default domain: atomcp.kooshapari.com
- Atoms-specific service configuration
- Integration with pheno-sdk packages

#### AtomsMCPCLI

CLI framework for the Atoms MCP server.

Provides a complete CLI interface using the pheno-sdk framework.

#### MCPServiceConfig

Configuration for MCP services with sensible defaults.

#### MCPEntryPoint

Base class for MCP server entry points.

Provides common functionality for MCP servers including:
- Service orchestration using ServiceInfra
- Automatic port allocation and tunnel management
- Health checking and monitoring
- Graceful shutdown handling

#### ProjectConfigBuilder

Builder pattern for creating project configurations.

Provides a fluent interface for building complex project configurations.

#### OrchestrationMode

Orchestration execution mode.

#### ResourceStatus



#### InfrastructureManager

Unified infrastructure and process management system.

#### ProjectContext

Context information required to execute commands for a project.

#### ConsoleProgressCallback

Simple progress callback that prints updates to stdout.

Useful for CLI workflows or debugging command pipelines without a GUI. The callback
intentionally keeps state minimal so it can be reused across multiple command runs.

#### RichProgressCallback

Progress callback that renders Rich progress bars for command stages.

Requires the ``rich`` library and is intended for advanced terminal UIs.
The callback keeps a reference to the Rich progress instance so that nested
command runs share a single UI.

#### FileCallback

Progress callback that appends stage updates to a log file.

Useful for offline auditing of command pipelines. The callback opens the file lazily
and keeps it open for the lifetime of the run to minimise I/O overhead.

#### CompositeCallback

Progress callback that fans out events to multiple underlying callbacks.

Exceptions raised by individual callbacks are logged but do not halt other
callbacks, ensuring best-effort delivery.

#### CallbackManager

Orchestrates registration and execution of command engine callbacks.

The manager keeps separate registries for progress, completion, and event-style
callbacks while recording a history of emitted events for later inspection (e.g.,
testing or analytics).

#### ProgressCallback

Contract for receiving progress updates during command execution.

#### CompletionCallback

Contract for receiving final command completion notifications.

#### CallbackEvent

Immutable record capturing an emitted callback event.

#### PerformanceSnapshot

Snapshot of performance metrics at a point in time.

#### MetricsExporter

Export metrics in various formats.

#### AgentExecutionMetric

Single agent execution metric.

#### AgentMetricsSummary

Summary of agent metrics.

#### AgentMetricsCollector

Collect and analyze MCP agent execution metrics.

#### MetricsSchemeHandler

Handler for metrics:// scheme.

Provides access to application metrics.

URI Format:
    metrics://counters/http_requests_total
    metrics://gauges/memory_usage_bytes
    metrics://histograms/response_time_seconds
    metrics://all  (get all metrics)

Example:
    >>> handler = MetricsSchemeHandler()
    >>> requests = await handler.get_resource("metrics://counters/http_requests_total")
    >>> all_metrics = await handler.get_resource("metrics://all")

#### LogsSchemeHandler

Handler for logs:// scheme.

Provides access to application logs.

URI Format:
    logs://app/errors  (get error logs)
    logs://app/all?limit=100  (get last 100 logs)
    logs://app/all?level=ERROR  (get ERROR level logs)
    logs://app/all?since=2024-01-01  (get logs since date)

Example:
    >>> handler = LogsSchemeHandler()
    >>> errors = await handler.get_resource("logs://app/errors")
    >>> recent = await handler.get_resource("logs://app/all?limit=50")

#### FileSchemeHandler

Handler for file:// scheme.

Provides read access to files on the file system.
Automatically parses JSON and YAML files.

URI Format:
    file:///absolute/path/to/file
    file://./relative/path/to/file
    file://*.json  (list all JSON files in current dir)

Example:
    >>> handler = FileSchemeHandler()
    >>> config = await handler.get_resource("file://./config.json")
    >>> files = await handler.list_resources("file://*.yaml")

#### HttpSchemeHandler

Handler for http:// and https:// schemes.

Provides access to HTTP resources.
Automatically parses JSON responses.

URI Format:
    http://example.com/api/resource
    https://api.example.com/v1/users/123

Example:
    >>> handler = HttpSchemeHandler()
    >>> data = await handler.get_resource("https://api.example.com/users/123")

#### EnvSchemeHandler

Handler for env:// scheme.

Provides access to environment variables.

URI Format:
    env://VARIABLE_NAME
    env://PREFIX_*  (list all with prefix)

Example:
    >>> handler = EnvSchemeHandler()
    >>> path = await handler.get_resource("env://PATH")
    >>> app_vars = await handler.list_resources("env://APP_*")

#### ResourceTemplate

Resource template definition with URI pattern and handler.

#### ResourceRegistry

Minimal facade until full implementation is shared.

#### ProjectGraph

Project graph for cross-tool communication and workflow orchestration.

Manages the state and coordination of complex multi-tool projects by:
- Tracking dependencies between tasks and tools
- Facilitating communication between different tool executions
- Managing project state and context sharing
- Orchestrating workflow execution based on dependencies

#### InMemoryMcpProvider

In-memory MCP provider implementation.

Stores sessions and tools in memory. Useful for testing and development.

Example:
    >>> provider = InMemoryMcpProvider()
    >>> session = await provider.connect(server)
    >>> result = await provider.execute_tool(tool, {"param": "value"})

#### InMemoryMonitoringProvider

In-memory monitoring provider implementation.

Stores metrics and workflow data in memory.

Example:
    >>> monitor = InMemoryMonitoringProvider()
    >>> await monitor.track_workflow("data-pipeline", {"user": "alice"})
    >>> await monitor.record_metric("execution_time", 1.23, {"tool": "search"})

#### InMemoryToolRegistry

In-memory tool registry implementation.

Stores tools and their handlers in memory.

Example:
    >>> registry = InMemoryToolRegistry()
    >>> registry.register_tool(
    ...     McpTool(name="search", description="Search docs"),
    ...     handler=search_handler
    ... )
    >>> tool = registry.get_tool("search")

#### InMemorySessionManager

In-memory session manager implementation.

Manages MCP sessions in memory with metadata tracking.

Example:
    >>> manager = InMemorySessionManager()
    >>> session = await manager.create_session(server)
    >>> sessions = manager.list_sessions()
    >>> await manager.close_session(session)

#### InMemoryResourceProvider

In-memory resource provider with scheme handlers.

Supports registering custom scheme handlers and provides
built-in handlers for common schemes.

Example:
    >>> provider = InMemoryResourceProvider()
    >>> provider.register_scheme("config", ConfigSchemeHandler())
    >>> config = await provider.get_resource("config://app/database")

#### ConfigSchemeHandler

Handler for config:// scheme.

Provides access to configuration values.

Example:
    >>> handler = ConfigSchemeHandler()
    >>> config = await handler.get_resource("config://app/database/host")

#### MemorySchemeHandler

Handler for memory:// scheme.

Simple in-memory key-value store.

Example:
    >>> handler = MemorySchemeHandler()
    >>> await handler.set("memory://cache/user-123", {"name": "Alice"})
    >>> user = await handler.get_resource("memory://cache/user-123")

#### WorkflowMonitoringIntegration

Main integration class for MCP workflow monitoring.

#### BasicCommandsMixin

Mixin providing basic MCP server commands.

#### AdvancedCommandsMixin

Mixin providing advanced MCP server commands.

#### MaintenanceCommandsMixin

Mixin providing maintenance commands.

#### EnhancedMCPFramework

Enhanced MCP framework with comprehensive command support.

#### MCPPerformanceMonitor

Monitor MCP protocol performance.

#### PerformanceOptimizer

Central coordinator for MCP performance optimization features.

#### CapturedCredentials



#### UnifiedCredentialBroker

In-memory credential store.

#### TestRegistry

Centralised registry for decorator-based test discovery.

#### CacheEntry



#### TestCache

Persistent cache keyed by test name and tool identifier.

A JSON file on disk stores the cached results.  The cache is intentionally
conservative: only successful runs or explicit skip markers are reused.
Changes to the Python interpreter version automatically invalidate cached
data to avoid subtle incompatibilities.

#### MCPProject



#### EndpointConfig



#### EndpointRegistry

Central registry for MCP endpoints across environments.

#### MCPOAuthCacheAdapter

Small wrapper exposing ``_get_cache_path`` for compatibility.

#### MCPClientAdapter

Convenience adapter for generic MCP clients.

The adapter normalises a couple of frequently accessed attributes so the test runner
can display friendly information without knowing the concrete client type.

#### OAuthStatusWidget

OAuth token status monitoring widget.

#### ServerStatusWidget

Display MCP server status with comprehensive monitoring.

#### TunnelStatusWidget



#### ResourceStatusWidget

Enhanced resource monitoring widget with comprehensive metrics.

Features:
- System resource monitoring (CPU, memory, disk, network)
- Database monitoring with connection pool stats
- Threshold-based alerts with color coding
- Historical trend tracking with sparklines
- TaskMetrics integration
- Protocol-based design for custom providers

#### FastHTTPResponse

Simplified response wrapper returned by :class:`FastHTTPClient`.

#### FastHTTPClient

Minimal asynchronous HTTP client used by the MCP QA tooling.

The original implementation delegated to httpx with retry/backoff logic.
To keep consolidation simple while remaining compatible we implement a
small subset of that behaviour: ``get``/``post`` helpers plus the async
context manager protocol.  When httpx is not available we fall back to the
standard library using ``urllib.request`` executed in a thread pool.

#### FunctionalityMatrixReporter

Functionality Matrix Reporter - Comprehensive Feature Coverage

Maps test results to tool capabilities, user stories, data coverage,
and test results with performance metrics.

#### ConsoleReporter

Console reporter with formatted output supporting both plain and rich modes.

#### JSONReporter

JSON reporter for machine-readable output.

#### TestReporter

Base class for test reporters.

All reporters should inherit from this class and implement the report() method.

#### MultiReporter

Composite reporter that runs multiple reporters.

Useful for generating multiple report formats in a single call.

Example:
    multi = MultiReporter([
        ConsoleReporter(),
        JSONReporter("results.json"),
        MarkdownReporter("report.md")
    ])
    multi.report(results, metadata)

#### MarkdownReporter

Markdown reporter for documentation.

#### DetailedErrorReporter

Detailed Error Reporter - Pytest-like detailed error output.

Provides comprehensive error information for debugging failed tests.

#### BaseTestRunner

Executes registered MCP QA tests.

#### BaseClientAdapter

Minimal adapter wrapper.

``BaseClientAdapter`` places no requirements on the wrapped client beyond
exposing it via the ``client`` attribute.  Projects typically subclass this
to add helpers for domain-specific tooling.

#### MetricsResourceScheme

Handler for metrics:// resources - performance metrics.

#### FilesResourceScheme

Handler for files:// resources - file system navigation.

#### SystemResourceScheme

Handler for system:// resources - system information.

#### ConfigResourceScheme

Handler for config:// resources - configuration information.

#### ResourceSchemeRegistry

Registry for resource scheme handlers.

#### ToolsResourceScheme

Handler for tools:// resources - tool information.

#### PromptsResourceScheme

Handler for prompts:// resources - system prompts.

#### LogsResourceScheme

Handler for logs:// resources - log access.

#### StaticResourceScheme

Handler for static:// resources - static content.

#### ZenResourceScheme

Handler for zen:// resources - core server information.

#### ResourceParameter

Resource template parameter definition.

#### ResourceAnnotation

Resource annotation for LLM optimization and access control.

#### ResourceContext

Context provided to resource handlers.

#### ResourceTemplateEngine

Engine for managing and executing resource templates.

#### CriticalPathAnalysis

Results of critical path analysis.

#### CommunicationMessage

A message in the project graph communication system.

#### NodeType

Types of nodes in the project graph.

#### NodeStatus

Status of nodes in the project graph.

#### AcceptanceStatus

Status of acceptance criteria.

#### QualityGateStatus

Status of quality gates.

#### GraphNode

A node in the project graph.

#### WBSNode

Work Breakdown Structure node with enhanced project management features.

#### AcceptanceCriterion

Represents an acceptance criterion with verification methods.

#### Deliverable

Represents a project deliverable with acceptance criteria.

#### QualityGate

Represents a quality gate for milestone validation.

#### UserStory

Strict user story template.

Enforces: As a <persona>, I want <goal>, so that <benefit>.
Acceptance criteria live on the node (GraphNode.acceptance_criteria).

#### RequirementSpec

Formal requirement specification.

#### TestCase

Executable test case linked to an acceptance criterion or item.

#### TeamMember

Represents a team member with skills and availability.

#### Team

Represents a team with multiple members.

#### ModelCatalogRegistry

Registry that tracks model metadata in addition to provider entries.

#### CapabilityCatalogRegistry

Registry supporting alias resolution and capability lookups.

#### OpenAIModelCatalog

Model catalog that reads OpenAI models from a JSON configuration file.

#### AnthropicModelCatalog

Model catalog seeded with Anthropic defaults.

#### GoogleModelCatalog

Model catalog for Google offerings.

#### GeminiModelCatalog

Alias of Google model catalog for Gemini.

#### AzureModelCatalog

Model catalog for Azure OpenAI deployments.

#### XAIModelCatalog

Model catalog for xAI models.

#### DialModelCatalog

Model catalog for Dial integrations.

#### OpenRouterModelCatalog

Model catalog for OpenRouter providers.

#### CustomEndpointModelCatalog

Model catalog for custom endpoint integrations.

#### UnifiedProviderRegistry

Unified Provider Registry.

Consolidates all provider registry functionality using BaseRegistry.
Inherits all features: metadata, callbacks, search, filtering, categories.

LOC Saved: ~3,200 from 8+ registry files

#### BaseProvider

Base provider class for all unified providers.

#### AnthropicProvider

Anthropic Provider - Unified.

#### GoogleProvider

Google Provider - Unified.

#### AzureProvider

Azure Provider - Unified.

#### XAIProvider

XAI Provider - Unified.

#### DialProvider

DIAL Provider - Unified.

#### OpenRouterProvider

OpenRouter provider for LLM content generation.

#### CustomProvider

Custom Provider - Unified placeholder.

#### BenchmarkResult

Benchmark result.

#### BenchmarkConfig

Benchmark configuration.

#### PerformanceBenchmark

Performance benchmark implementation.

#### MigrationResult

Migration validation result.

#### MigrationConfig

Migration configuration.

#### MigrationValidator

Migration validator implementation.

#### IntegrationValidator

Main integration validator implementation.

#### ValidationSuite

Comprehensive validation suite.

#### ValidationConfig

Validation configuration.

#### IntegrationTest

Integration test definition.

#### IntegrationError

Raised when integration validation fails.

#### PerformanceError

Raised when performance validation fails.

#### MigrationError

Raised when migration validation fails.

#### ReportFormat

Report output formats.

#### ReportConfig

Report configuration.

#### ReportGenerator

Report generator implementation.

#### SupabaseAuthError

Raised when Supabase auth operations fail.

#### SupabaseAuthClient

Lightweight helper around Supabase auth endpoints.

#### InMemorySupabaseClient

Very small in-memory store that mimics Supabase table operations.

#### InMemorySupabaseQuery



#### InMemorySupabaseAuth

Simple auth helper with a mapping of access tokens to user payloads.

#### _Result



#### AuthKit

AuthKit client for Standalone Connect OAuth flow.

#### AuthProviderProtocol

Protocol for authentication providers.

#### OAuthProviderProtocol

Protocol for OAuth providers.

#### MFAProviderProtocol

Protocol for MFA providers.

#### SessionProviderProtocol

Protocol for session management.

#### AuthStoreProtocol

Protocol for user/token storage.

#### SecurityProviderProtocol

Protocol for security utilities.

#### MFAType

Multi-factor authentication types.

#### AuthProviderType

Authentication provider types.

#### AuthUser

Unified user representation.

#### AuthToken

Unified token representation.

#### AuthSession

Unified session representation.

#### AuthRequest

Authentication request data.

#### AuthResponse

Authentication response data.

#### UnifiedAuthManager

Unified Authentication Manager.

Consolidates authentication logic from multiple implementations into a single,
coherent system.

#### SessionStorage

Abstract session storage interface.

#### FilesystemStorage

Store credentials in local filesystem.

#### MemoryStorage

Store credentials in memory (for testing).

#### ResourceLimitConfig

Configuration for resource limits.

#### ResourceExhaustedError

Raised when resource limits are exceeded.

#### ResourceLimits

Resource limits enforcement.

#### ResourceMonitor

Protocol for custom resource monitoring implementations.

Implement this protocol to provide custom resource monitoring logic.
The widget will call these methods to gather metrics.

Example:
    class CloudResourceMonitor:
        async def get_cpu_usage(self) -> float:
            # Query cloud provider API
            return await cloud_api.get_cpu_percent()

        async def get_memory_usage(self) -> Dict[str, float]:
            stats = await cloud_api.get_memory_stats()
            return {
                "used_mb": stats.used / 1024 / 1024,
                "percent": stats.percent
            }

        async def get_disk_usage(self) -> float:
            return await cloud_api.get_disk_percent()

        async def get_network_bandwidth(self) -> Dict[str, float]:
            stats = await cloud_api.get_network_stats()
            return {
                "upload_kbps": stats.tx_kbps,
                "download_kbps": stats.rx_kbps
            }

#### PolicyAction

Policy actions.

#### PolicyRule

Security policy rule.

#### PolicyViolationError

Raised when policy is violated.

#### SecurityPolicy

Security policy implementation.

#### PolicyManager

Manages multiple security policies.

#### Permission

File system permissions.

#### PermissionConfig

Configuration for permission checking.

#### PermissionError

Base exception for permission errors.

#### AccessDeniedError

Raised when access is denied.

#### InsufficientPermissionsError

Raised when user has insufficient permissions.

#### PermissionChecker

Checks and enforces file system permissions.

#### SandboxConfig

Configuration for security sandbox.

#### SandboxError

Base exception for sandbox errors.

#### SandboxViolationError

Raised when sandbox security is violated.

#### ResourceLimitError

Raised when resource limits are exceeded.

#### SecuritySandbox

Security sandbox for safe code execution.

#### PathValidationConfig

Configuration for path validation.

#### PathValidationError

Base exception for path validation errors.

#### TraversalAttemptError

Raised when directory traversal is detected.

#### InvalidPathError

Raised when path is invalid.

#### PathValidator

Validates and sanitizes file paths for security.

#### FileSystemConfig

Configuration for secure file system.

#### FileSystemError

Base exception for file system errors.

#### FileAccessDeniedError

Raised when file access is denied.

#### SecureFileSystem

Secure file system operations.

#### PermissionResult

Result of a permission check.

#### SandboxSecuritySettings

Security configuration used by the sandbox manager.

#### SandboxResourceLimits

Resource limits for sandboxed operations.

#### SandboxContext

Context for sandboxed operations.

#### PathSecurityValidator

Validates file paths against security policies.

#### SandboxManager

Main sandbox management system.

#### ScanResult

Complete scan result (Morph-compatible).

#### SecretScanner

Unified secret scanner for files and repositories.

Provides Morph-compatible API for secret scanning.

#### GitSecretScanner

Scanner for Git repositories (including history).

Note: This is a simplified implementation. For full Git history scanning,
consider using trufflehog directly via CLI.

#### SecretFinding



#### ScanSummary



#### SuppressionRules



#### IntegrationGates

Integration quality gates tool.

#### IntegrationGatesPlugin

Plugin for integration quality gates tool.

#### ArchitecturalValidator

Architectural pattern validation tool.

#### ArchitecturalValidatorPlugin

Plugin for architectural validation tool.

#### AtlasHealthAnalyzer

Atlas health analysis tool.

#### AtlasHealthPlugin

Plugin for atlas health analysis tool.

#### PerformanceDetector

Performance anti-pattern detection tool.

#### PerformanceDetectorPlugin

Plugin for performance detection tool.

#### PatternDetectorPlugin

Plugin for pattern detection tool.

#### SecurityScanner

Security pattern scanning tool.

#### SecurityScannerPlugin

Plugin for security scanning tool.

#### CodeSmellDetector

Code smell detection tool.

#### CodeSmellDetectorPlugin

Plugin for code smell detection tool.

#### UserBuilder

Builder for creating User entities with a fluent interface.

Example:
    user = (UserBuilder()
            .with_email("user@example.com")
            .with_name("John Doe")
            .build())

#### DeploymentBuilder

Builder for creating Deployment entities with a fluent interface.

Example:
    deployment = (DeploymentBuilder()
                  .with_environment("production")
                  .with_strategy("blue_green")
                  .build())

#### ServiceBuilder

Builder for creating Service entities with a fluent interface.

Example:
    service = (ServiceBuilder()
               .with_name("api-server")
               .with_port(8080)
               .with_http_protocol()
               .build())

#### ConfigurationBuilder

Builder for creating Configuration entities with a fluent interface.

Example:
    config = (ConfigurationBuilder()
              .with_key("app.debug")
              .with_value(True)
              .with_description("Debug mode")
              .build())

#### RepositoryType

Supported repository types.

#### RepositoryFactory

Factory for creating repository implementations.

This factory allows switching between different repository implementations (in-
memory, SQLAlchemy, MongoDB, etc.) based on configuration.

#### UseCaseFactory

Factory for creating use cases with their dependencies.

This factory centralizes use case creation and ensures all dependencies are properly
injected.

#### EntityFactory

Abstract factory for creating domain entities.

This provides a common interface for all entity factories.

#### UserFactory

Factory for creating User entities.

Encapsulates the creation logic and validation for users.

#### DeploymentFactory

Factory for creating Deployment entities.

Encapsulates the creation logic and validation for deployments.

#### ServiceFactory

Factory for creating Service entities.

Encapsulates the creation logic and validation for services.

#### ConfigurationFactory

Factory for creating Configuration entities.

Encapsulates the creation logic and validation for configurations.

#### DTOValidator

Abstract base class for DTO validation.

Provides standard patterns for:
- Field validation
- Business rule validation
- Cross-field validation
- Custom validation logic

#### BusinessRuleValidator

Abstract base class for business rule validation.

Provides standard patterns for:
- Complex business logic validation
- Cross-entity validation
- External system validation
- Conditional validation

#### ValidationErrorHandler

Handles validation errors and converts them to appropriate exceptions.

Provides standard error handling patterns for different validation scenarios.

#### CompositeValidator

Composite validator that combines multiple validation strategies.

Provides a single interface for all validation operations.

#### DTOMapper

Abstract base class for mapping between entities and DTOs.

Provides standard patterns for:
- Entity to DTO conversion
- DTO to entity conversion
- Field mapping and validation
- Nested object handling

#### EntityMapper

Generic entity mapper using reflection.

Automatically maps between entities and DTOs based on field names. Handles common
patterns like ID conversion and nested objects.

#### EventMapper

Mapper for converting entities to domain events.

Provides standard patterns for:
- Entity to event conversion
- Event data extraction
- Event type mapping

#### CompositeMapper

Composite mapper that combines DTO and event mapping.

Provides a single interface for all mapping operations.

#### CRUDScaffold

Complete CRUD scaffold for an entity.

Generates use cases, routes, and dependencies for a complete CRUD API with minimal
boilerplate.

#### UseCaseScaffold

Scaffold for generating use cases.

Creates standard use cases (create, update, get, list, delete) with minimal
configuration.

#### RouteScaffold

Scaffold for generating API routes.

Creates standard REST API routes with proper error handling, validation, and
documentation.

#### RepositoryScaffold

Scaffold for generating repository implementations.

Creates standard repository methods with common patterns.

#### CreateUseCase



#### BaseUseCase

Base use case with common functionality.

Provides standard patterns for:
- Entity retrieval and validation
- Event publishing
- Error handling
- DTO conversion

#### BaseCreateUseCase

Base use case for creating entities.

#### BaseUpdateUseCase

Base use case for updating entities.

#### BaseGetUseCase

Base use case for getting entities by ID.

#### BaseListUseCase

Base use case for listing entities.

#### BaseDeleteUseCase

Base use case for deleting entities.

#### BaseActionUseCase

Base use case for entity actions (start, stop, complete, etc.).

#### BaseCRUDUseCase

Complete CRUD use case with all operations.

Combines create, update, get, list, and delete operations into a single use case
class.

#### RepositoryFacade

Facade for all repositories.

Provides a single interface to access all repositories,
simplifying dependency management.

Example:
    facade = RepositoryFacade(user_repo, deployment_repo, service_repo, config_repo)
    user = await facade.users.find_by_id(user_id)

#### UseCaseFacade

Facade for all use cases.

Provides a single interface to access all use cases,
organized by domain.

Example:
    facade = UseCaseFacade(use_case_factory)
    user = await facade.users.create(dto)

#### UserUseCases

User use cases facade.

#### DeploymentUseCases

Deployment use cases facade.

#### ServiceUseCases

Service use cases facade.

#### ConfigurationUseCases

Configuration use cases facade.

#### RepositoryDecorator

Base decorator for repository implementations.

This provides a template for creating repository decorators that add cross-cutting
concerns.

#### CachingDecorator

Caching decorator for repositories.

Adds caching functionality to repository operations to reduce
database queries and improve performance.

Example:
    user_repo = InMemoryUserRepository()
    cached_repo = CachingDecorator(user_repo, ttl=300)

#### LoggingDecorator

Logging decorator for repositories.

Adds logging to all repository operations for debugging
and monitoring purposes.

Example:
    user_repo = InMemoryUserRepository()
    logged_repo = LoggingDecorator(user_repo)

#### RetryDecorator

Retry decorator for repositories.

Adds automatic retry logic for transient failures.

Example:
    user_repo = InMemoryUserRepository()
    retry_repo = RetryDecorator(user_repo, max_retries=3, delay=1.0)

#### MetricsDecorator

Metrics decorator for repositories.

Collects metrics about repository operations for monitoring
and performance analysis.

Example:
    user_repo = InMemoryUserRepository()
    metrics_repo = MetricsDecorator(user_repo)

#### ModelRestrictionService

Central authority for environment-driven model allowlists.

Role
    Interpret ``*_ALLOWED_MODELS`` environment variables, keep their
    entries normalised (lowercase), and answer whether a provider/model
    pairing is permitted.

Responsibilities
    * Parse, cache, and expose per-provider restriction sets
    * Validate configuration by cross-checking each entry against the
      provider's alias-aware model list
    * Offer helper methods such as ``is_allowed`` and ``filter_models`` to
      enforce policy everywhere model names appear (tool selection, CLI
      commands, etc.).

#### RegistryItem

Immutable wrapper that stores a registered object and its metadata.

#### AdapterType

Supported adapter categories.

#### SchemaBuilder

Utility to build input JSON schemas consistently across tools.

#### ToolOutput

Standardized tool output format.

#### ToolRequest

Canonical simple tool request model.

Tools can subclass this to add extra fields. This mirrors the example
structure (prompt/files/images/model/temperature/thinking_mode/continuation_id)
and is compatible with Pydantic v2 style usage.

#### BaseModel



#### ModelCapabilities

Describes a model's capabilities for tool routing and validation.

#### TemperatureConstraint

Contract for temperature validation used by model capabilities.

Concrete providers describe their temperature behaviour by creating
subclasses that expose three operations:
* `validate` – decide whether a requested temperature is acceptable.
* `get_corrected_value` – coerce out-of-range values into a safe default.
* `get_description` – provide a human readable error message for users.

Providers call these hooks before sending traffic to the underlying API so
that unsupported temperatures never reach the remote service.

#### FixedTemperatureConstraint

Constraint for models that only support a single temperature value.

Used by reasoning models (o1, o3, etc.) that require specific temperature settings
for proper functionality.

#### RangeTemperatureConstraint

Constraint for models that support a continuous range of temperature values.

Most GPT-style models use this constraint type.

#### DiscreteTemperatureConstraint

Constraint for models that only support specific discrete temperature values.

Some models might only support certain preset temperature settings.

#### ModelContext

Context object containing model information and capabilities.

#### BaseTool

Base class for all tools providing common functionality.

#### SimpleToolExecutionMixin



#### SimpleToolConversationMixin



#### SimpleToolPromptMixin



#### SimpleTool

Base class for simple (non-workflow) tools.

Simple tools are request/response tools that don't require multi-step workflows.
They benefit from:
- Automatic schema generation using SchemaBuilder
- Inherited conversation handling and file processing
- Standardized model integration
- Consistent error handling and response formatting

To create a simple tool:
1. Inherit from SimpleTool
2. Implement get_tool_fields() to define tool-specific fields
3. Implement prepare_prompt() for prompt preparation
4. Optionally override format_response() for custom formatting
5. Optionally override get_required_fields() for custom requirements

#### SimpleToolValidationMixin



#### UpstreamConfig

Configuration for an upstream service.

#### ProxyAdminClient



#### FallbackAdminClient



#### LoadingMiddleware

Shows loading page while service starts.

#### HealthCheckMiddleware

Route to healthy services or fallback based on registered checks.

#### ServiceState

Service lifecycle states.

#### MiddlewareConfig



#### TemplateRenderer



#### KInfraMiddleware



#### FallbackMiddleware

Render error pages based on status codes.

#### MaintenanceMiddleware

Show maintenance page while maintenance is enabled.

#### StatusPageGenerator



#### ControlCenterConfig

Main configuration for the Pheno Control Center.

#### MultiProjectMonitor

Monitor that provides unified display of multiple pheno-sdk projects.

Features:
- Project-grouped process and resource display
- Streaming logs with project categorization
- Global status overview
- Integration with existing KInfra monitors

#### CommandMetrics

Metrics for a single command execution.

#### CLITelemetry

Telemetry system for CLI command execution.

Collects metrics, tracks performance trends, and provides monitoring capabilities
for CLI operations.

#### ResourceState

Current state of a resource.

#### ProjectTunnelInfo

Tunnel information specific to a project.

#### ProjectFallbackInfo

Fallback configuration for a project.

#### ProjectProxyInfo

Proxy configuration for a project.

#### TenantManager

Manages multi-tenant tunnels, fallback services, and proxy routing.

Provides:
- Per-project port allocation for fallback/proxy services
- Shared tunnel management with project isolation
- Clean separation of project resources
- Coordinated cleanup to avoid affecting other projects

#### TunnelsMixin



#### PortsMixin



#### ServiceInfraManager

Unified ServiceInfra interface (composed from mixins).

#### CleanupMixin



#### WrappersMixin



#### InfoMixin



#### BaseServiceInfra

Core wiring and lifecycle primitives for ServiceInfra.

#### WildcardStatusHandler

Wildcard route handler for unmatched routes.

#### GrpcServerConfig

Configuration for gRPC server.

Can be used standalone or with config-kit integration.

#### GrpcServer

Lightweight gRPC server wrapper with DI and interceptor support.

Example:
    >>> config = GrpcServerConfig(host="0.0.0.0", port=50051)
    >>> server = GrpcServer(config)
    >>>
    >>> # Add interceptors
    >>> server.add_interceptor(ServerTelemetryInterceptor())
    >>>
    >>> # Register services
    >>> from my_pb2_grpc import add_MyServiceServicer_to_server
    >>> add_MyServiceServicer_to_server(MyServiceImpl(), server.server)
    >>>
    >>> # Start server
    >>> await server.start()
    >>> await server.wait_for_termination()

#### ClientTelemetryInterceptor

ClientInterceptor adding trace context to metadata.

#### ServerTelemetryInterceptor

ServerInterceptor extracting trace/correlation metadata for logging/OTEL.

#### MetadataAuthInterceptor

Server-side auth check via metadata (e.g., bearer tokens).

#### ServerSpanAttributesInterceptor

Server interceptor that adds request metadata as span attributes if OTel is present.

#### ClientSpanAttributesInterceptor

Client interceptor that adds request metadata as span attributes if OTel is present.

#### GrpcClientConfig

Configuration for gRPC client.

Can be used standalone or with config-kit integration.

#### GrpcChannel

Lightweight gRPC channel wrapper with interceptor support.

Example:
    >>> config = GrpcClientConfig(target="localhost:50051")
    >>> channel = GrpcChannel(config)
    >>>
    >>> # Add interceptors
    >>> channel.add_interceptor(ClientTelemetryInterceptor())
    >>>
    >>> # Create stub
    >>> from my_pb2_grpc import MyServiceStub
    >>> stub = MyServiceStub(channel.channel)
    >>>
    >>> # Make calls
    >>> response = await stub.MyMethod(request)
    >>>
    >>> # Close when done
    >>> await channel.close()

#### DefaultLogger

Default logger implementation using Python logging.

#### NetworkingOptions



#### NetworkStartResult



#### TunnelConfig

Runtime configuration for tunnel operations.

#### ProcessMetrics

Metrics for a monitored process.

#### ProcessMonitor

Monitor process resource usage and provide logging capabilities.

Provides:
- Real-time metrics collection
- Resource usage logging
- Performance alerts
- Historical data tracking

#### TunnelRegistry



#### AsyncTunnelManager



#### TunnelType



#### TunnelStatus



#### CloudflareTunnelError



#### TunnelNotFoundError



#### TunnelConfigurationError



#### TunnelOperationError



#### TunnelProtocol



#### TunnelInfo

Information about a tunnel configuration.

#### SyncTunnelManager



#### BaseTunnelManager



#### MonitorMixin



#### HealthMixin



#### ProcessMixin



#### ResourcesMixin



#### FileChangeHandler



#### FileSystemEvent



#### FileSystemEventHandler



#### FallbackMixin



#### _State



#### BaseServiceManager



#### CommandAdapter

Generic command-based resource adapter.

Configuration:
    start_command: List[str] - Command to start resource (required)
    stop_command: List[str] - Command to stop resource (required)
    status_command: List[str] - Command to check status (optional)
    health_check: Dict - Health check configuration
    run_in_background: bool - Run start command in background (default: True)

#### ResourceFactory

Factory for creating resource adapters from configuration.

Simplifies resource creation with automatic adapter selection.

#### DockerAdapter

Generic Docker container adapter.

Configuration options:
    image: str - Docker image (required)
    container_name: str - Container name (defaults to kinfra-{name})
    ports: Dict[int, int] - Port mappings {host: container}
    environment: Dict[str, str] - Environment variables
    volumes: Dict[str, str] - Volume mounts {host_path: container_path}
    command: List[str] - Container command override
    network: str - Docker network
    restart_policy: str - Restart policy (no, on-failure, always, unless-stopped)
    health_check: Dict - Health check configuration
        - type: tcp, http, docker, command
        - port: int (for tcp/http)
        - path: str (for http)
        - command: List[str] (for command)
    cleanup_on_stop: bool - Remove container on stop (default: True)

#### APIAdapter

Generic API-based resource adapter.

Manages resources via HTTP/REST APIs. Useful for:
- Cloud databases (RDS, Cloud SQL, etc.)
- SaaS services (Auth0, Stripe, etc.)
- Serverless functions (Lambda, Cloud Functions)
- Kubernetes resources via API
- Remote servers via API

Configuration:
    api_base_url: str - Base URL for API (required)
    auth: Dict - Authentication configuration
        - type: "bearer", "basic", "api_key", "custom"
        - token: str (for bearer)
        - username: str (for basic)
        - password: str (for basic)
        - api_key: str (for api_key)
        - header_name: str (for api_key, default: "X-API-Key")
        - headers: Dict[str, str] (for custom)
    start_endpoint: str - Endpoint to call to start resource
    start_method: str - HTTP method (default: POST)
    start_body: Dict - Request body for start
    stop_endpoint: str - Endpoint to call to stop resource
    stop_method: str - HTTP method (default: POST)
    stop_body: Dict - Request body for stop
    status_endpoint: str - Endpoint to check status
    health_endpoint: str - Endpoint for health checks
    health_check: Dict - Health check configuration
        - type: "http" (default), "custom"
        - expected_status: int (default: 200)
        - expected_response: Dict - Expected JSON response
        - poll_interval: float (default: 5.0)

#### HealthCheckStrategy

Health check strategies.

#### ResourceAdapter

Abstract base class for resource adapters.

Adapters handle the specifics of starting, stopping, and monitoring different types
of resources (Docker, systemd, processes, etc.).

#### SystemDaemonAdapter

Generic system daemon adapter for systemd/launchd.

Configuration:
    service_name: str - Service name (required)
    daemon_type: str - "systemd" or "launchd" (auto-detected if not specified)
    use_sudo: bool - Use sudo for commands (default: True for systemd)
    health_check: Dict - Health check configuration

#### KInfra

Unified KInfra interface (composed from mixins).

#### BaseKInfra

Core wiring and lifecycle primitives for KInfra.

#### PythonServiceOptions

Options for building a Python service configuration.

#### ProcessPanel

Panel showing process status.

#### ResourcePanel

Panel showing external resource availability.

#### EndpointPanel

Panel showing service endpoints.

#### PublicMixin



#### TunnelEvent



#### DNSMixin



#### UnifiedMixin



#### QuickMixin



#### TunnelManager



#### SeparateMixin



#### TunnelBase

Base tunnel orchestration shared by mixins.

#### MCPExtensions

MCP-specific extensions for infrastructure management.

#### ServiceMonitor

Rich-based service monitor with scrolling logs and fixed TUI panel.

#### MonitorConfig

Configuration for service monitoring.

#### LogStore

Manage rolling log buffers and stream readers for monitored services.

#### ProcessInspector

Encapsulate process status and resource probing logic.

#### NeonAdapter

Neon serverless PostgreSQL adapter.

#### VercelAdapter

Vercel deployment adapter with native SDK support.

Configuration:
    deployment_id: str - Deployment ID (optional if project_name provided)
    project_name: str - Project name (optional if deployment_id provided)
    team_id: str - Team ID (optional)
    access_token: str - Vercel access token (required)
    use_sdk: bool - Prefer SDK over CLI (default: True)
    target: str - Deployment target (production, preview, development)
    auto_promote: bool - Auto-promote deployments to production

Features:
- Deploy projects
- Promote/cancel deployments
- Check deployment status
- Get deployment URLs
- SDK with CLI fallback

#### SupabaseAdapter

Supabase adapter with RLS support.

#### ServiceStartupCoordinator

Coordinates service lifecycle operations for ServiceManager.

#### ServiceManager

Concrete service manager coordinating lifecycle operations.

#### AsyncWorker

Worker thread for async monitoring operations.

#### PhenoControlCenterGUI



#### ProjectTileWidget

Individual project tile with start/stop controls.

#### ProjectLauncherWidget



#### MonitoringWidget



#### TerminalWidget



#### StatusWidget

Base class for status monitoring widgets.

#### ProjectConfigDialog



#### SettingsDialog



#### AboutDialog



#### FallbackServer

Lightweight HTTP server for serving error, loading, and status pages.

#### TenantAdminHandlers

Expose tenant management handlers for the fallback server.

#### ServiceStatusRegistry

Maintain fallback page configuration and per-service status.

#### FallbackRoutes

HTTP handlers for fallback server routes.

#### UpstreamRegistry

Maintain upstream configurations and tenant associations.

#### ProxyServer

Health-aware reverse proxy with automatic fallback.

#### AdminAPI

Expose dynamic upstream management endpoints.

#### RequestRouter

Dispatch inbound requests to upstream services or the fallback server.

#### CodexJSONLParser

Parse stdout emitted by `codex exec --json`.

#### ClaudeJSONParser

Parse stdout produced by `claude --output-format json`.

#### GeminiJSONParser

Parse stdout produced by `gemini -o json`.

#### ParsedCLIResponse

Result of parsing CLI stdout/stderr.

#### ParserError

Raised when CLI output cannot be parsed into a structured response.

#### BaseParser

Base interface for CLI output parsers.

#### CLinkTool

Bridge MCP requests to configured CLI agents.

This is a placeholder class that zen-mcp-server can import and subclass. The actual
implementation details depend on zen's SimpleTool base classes and MCP-specific
integrations.

#### ClientConfig

Root configuration for all CLI clients.

#### CodexAgent

Codex CLI agent with JSONL recovery support.

#### ClaudeAgent

Claude CLI agent with system-prompt injection support.

#### GeminiAgent

Gemini-specific behaviour.

#### AgentOutput

Container returned by CLI agents after successful execution.

#### CLIAgentError

Raised when a CLI agent fails (non-zero exit, timeout, parse errors).

#### BaseCLIAgent

Execute a configured CLI command and parse its output.

#### MigrationEngine

Database migration engine with version tracking.

#### MigrationStatus

Migration status.

#### ConnectionPoolManager

Manages multiple connection pools for different providers/services.

Example:
    manager = ConnectionPoolManager()

    # Get or create a pool
    pool = manager.get_pool("my_service", async_pool=True)

    # Use the pool
    async with pool.get_session() as session:
        async with session.get("https://api.example.com") as response:
            data = await response.json()

    # Cleanup all pools
    await manager.cleanup_all()

#### ConnectionPoolConfig

Configuration for connection pools.

#### ConnectionStats

Statistics for a connection pool.

#### AsyncConnectionPool

Async HTTP connection pool with health monitoring.

#### SyncConnectionPool

Synchronous HTTP connection pool with health monitoring.

#### SupabaseStorageAdapter

Supabase-based storage adapter.

#### StorageAdapter

Abstract interface for file storage services.

#### SupabaseRealtimeAdapter

Supabase-based realtime adapter.

#### RealtimeAdapter

Abstract interface for real-time subscriptions.

#### PostgreSQLAdapter

PostgreSQL adapter with connection pooling.

#### GeneratedApp



#### Computed

Computed property with automatic dependency tracking and memoization.

Features:
- Automatic dependency detection
- Memoization for performance
- Invalidation on dependency change
- Type preservation
- Integration with ReactiveProperty

Example:
    >>> class MyWidget:
    ...     items = ReactiveProperty(default=[])
    ...     multiplier = ReactiveProperty(default=2)
    ...
    ...     @Computed
    ...     def total(self):
    ...         return sum(item['price'] for item in self.items) * self.multiplier
    ...
    ...     @Computed
    ...     def item_count(self):
    ...         return len(self.items)
    >>>
    >>> widget = MyWidget()
    >>> widget.items = [{'price': 10}, {'price': 20}]
    >>> print(widget.total)  # 60 (30 * 2)

#### DependencyTracker

Utility for tracking reactive dependencies during computation.

This is used internally by Computed to automatically detect which ReactiveProperty
instances are accessed.

#### ReactiveProxy



#### ConfigFileHandler

Debounces filesystem events and forwards YAML changes.

#### CacheConfig

Cache backend configuration.

#### LoggingConfig

Logging output configuration.

#### ConfigSchema

Root configuration schema.

#### ConfigMigration

Registry of upgrade routines between schema versions.

#### StateStore

Centralized state management with transactions, time-travel, and persistence.

Features:
- Hierarchical state storage (dot notation: "user.profile.name")
- Transaction support for atomic updates
- Time-travel debugging (undo/redo)
- State persistence (JSON)
- Observer pattern for state changes
- Wildcard subscriptions ("user.*")
- Change history tracking
- Weak references to prevent memory leaks

Example:
    >>> store = StateStore()
    >>> store.set_state("user.name", "Alice")
    >>> store.set_state("user.age", 30)
    >>> print(store.get_state("user.name"))  # "Alice"
    >>>
    >>> # Subscribe to changes
    >>> store.subscribe("user.name", lambda old, new: print(f"Name: {old} -> {new}"))
    >>>
    >>> # Transaction
    >>> with store.transaction() as tx:
    ...     store.set_state("user.name", "Bob")
    ...     store.set_state("user.age", 31)
    >>>
    >>> # Time-travel
    >>> store.undo()
    >>> store.redo()
    >>> store.get_history()

#### TransactionContext

Context manager for state store transactions.

#### ReactiveWidget

Base class for widgets that use reactive properties.

Integrates with Textual widgets and provides:
- Auto-refresh on property changes
- Automatic observer registration
- Performance optimizations

#### ConfigProfile

Supported configuration profiles.

#### ReactivePropertyInstance

Instance of a reactive property bound to a specific object.

#### ReactiveProperty

Reactive property descriptor with auto-refresh, debouncing, and validation.

Features:
- Automatic observer notification on change
- Debouncing support (coalesce rapid changes)
- Validation hooks
- Change history tracking
- Type preservation
- Integration with Textual's reactive system

Example:
    >>> class MyWidget:
    ...     count = ReactiveProperty(default=0, debounce=0.1)
    ...     name = ReactiveProperty(default="", validator=lambda x: len(x) > 0)
    ...
    ...     def __init__(self):
    ...         self.count.subscribe(self._on_count_changed)
    ...
    ...     def _on_count_changed(self, old_val, new_val):
    ...         print(f"Count: {old_val} -> {new_val}")
    >>>
    >>> widget = MyWidget()
    >>> widget.count = 5  # Triggers notification

#### BoxDrawing

Box drawing character sets.

#### ColorUtils

Color manipulation utilities.

#### Shortcut

Keyboard shortcut definition.

#### KeyboardShortcuts

Keyboard shortcut manager.

Features:
- Shortcut registration
- Category organization
- Conflict detection
- Help text generation

#### GridCell

Grid cell definition.

#### GridLayout

Responsive grid layout container.

Features:
- Flexible grid sizing
- Cell spanning
- Dynamic cell management
- Responsive breakpoints

#### Tab

Tab definition.

#### TabbedLayout

Tabbed layout container with tab management.

Features:
- Dynamic tab creation/removal
- Tab switching
- Closeable tabs
- Custom tab icons
- Tab callbacks

#### ThreeSectionDashboard

Three-section dashboard layout (header/main/footer).

Common pattern for monitoring dashboards with:
- Fixed header (status banner, title)
- Scrollable main content
- Fixed footer (controls, help)

Example:
    class MyDashboard(App):
        def compose(self) -> ComposeResult:
            with ThreeSectionDashboard():
                yield StatusBanner(...)  # Goes to header
                yield ProcessTable(...)  # Goes to main
                yield ControlPanel(...)  # Goes to footer

#### GridDashboard

Grid-based dashboard layout.

Flexible grid for status cards, metrics panels, etc.

Example:
    with GridDashboard(columns=3):
        yield StatusCard("Server 1")
        yield StatusCard("Server 2")
        yield StatusCard("Server 3")
        yield MetricsPanel("Metrics")

#### SidebarDashboard

Dashboard with sidebar layout.

Common pattern for:
- Left sidebar: navigation, controls
- Right main area: content, logs

Example:
    with SidebarDashboard(sidebar_width=40):
        # Sidebar content
        yield ControlPanel()
        # Main content
        yield LogViewer()

#### MonitoringDashboard

Complete monitoring dashboard layout.

Combines multiple patterns:
- Header with status banner
- Grid of status cards
- Metrics panel
- Log viewer
- Footer with controls

Example:
    class MyMonitor(App):
        def compose(self) -> ComposeResult:
            with MonitoringDashboard():
                yield StatusBanner(...)
                yield StatusCard(...)
                yield MetricsPanel(...)
                yield LogViewer(...)

#### TabbedDashboard

Tabbed dashboard layout.

Multiple views in tabs:
- Overview
- Processes
- Metrics
- Logs

Example:
    with TabbedDashboard(tabs=["Overview", "Processes", "Logs"]):
        yield OverviewPanel()
        yield ProcessTable()
        yield LogViewer()

#### SplitDashboard

Split dashboard layout (top/bottom or left/right).

Example:
    with SplitDashboard(direction="horizontal", ratio=0.6):
        yield ProcessTable()  # 60% width
        yield LogViewer()     # 40% width

#### SplitDirection

Split direction.

#### SplitLayout

Split layout container with resizable panes.

Features:
- Horizontal or vertical splits
- Resizable panes
- Nested splits
- Customizable ratios

#### WidgetTemplate

Widget template definition.

#### WidgetFactory

Factory for creating widgets from templates.

Features:
- Template-based creation
- Widget type registration
- Configuration presets
- Nested widget creation

#### ColorScheme

Color scheme definition.

#### Theme

Complete theme definition with palette and design tokens.

#### ThemeManager

Theme manager for TUI applications.

Features:
- Theme registration
- Dynamic theme switching
- Custom theme creation
- Theme persistence

#### OAuthCacheProvider

Protocol for OAuth cache providers.

This protocol defines the interface that OAuth cache implementations must
provide to work with OAuthStatusWidget. By using this protocol, widgets
can work with any cache implementation that provides the required methods.

Example implementations:
    >>> from pathlib import Path
    >>>
    >>> class SimpleOAuthCache:
    ...     def __init__(self, cache_dir: Path):
    ...         self.cache_dir = cache_dir
    ...
    ...     def _get_cache_path(self) -> Path:
    ...         return self.cache_dir / "oauth_token.json"
    >>>
    >>> # Use with widget
    >>> cache = SimpleOAuthCache(Path.home() / ".cache")
    >>> widget = OAuthStatusWidget(cache_provider=cache)

Required Methods:
    _get_cache_path() -> Path: Returns the path to the OAuth token cache file

#### ClientAdapter

Protocol for MCP client adapters used by the server status widget.

#### MetricsProvider

Protocol for metrics collection and reporting.

Implement this protocol to integrate with various widgets that
support external metrics systems (Prometheus, StatsD, etc.).

Example:
    class PrometheusMetricsProvider:
        async def record_metric(self, name: str, value: float, tags: Dict[str, str]):
            self.gauge.labels(**tags).set(value)

        async def get_metrics(self) -> Dict[str, float]:
            return {
                "requests_total": self.counter.collect(),
                "latency_seconds": self.histogram.collect()
            }

#### FieldType

Form field types.

#### FormField

Form field definition.

#### FormWidget

Dynamic form widget with validation.

Features:
- Multiple field types
- Built-in and custom validation
- Submit/cancel handlers
- Field state management
- Error display

#### Button



#### Pressed



#### TreeNode

Tree node data structure.

#### TreeView

Hierarchical tree view widget.

Features:
- Expandable/collapsible nodes
- Custom icons
- Node selection
- Search/filter
- Lazy loading support

#### StatusDashboard

Comprehensive status dashboard with multiple monitoring widgets.

Extracted from zen-mcp-server TUI - provides reusable status monitoring
interface that can be embedded in any application.

#### StatusDashboardApp

Complete status dashboard application.

Example usage of the StatusDashboard widget as a standalone app.

#### TaskProgress

Individual task progress tracking.

#### ResourceMetric

Represents a single resource metric with timestamp and value.

#### DefaultResourceMonitor

Default system resource monitor using psutil.

#### ResultsDisplay

Rich display for results with syntax highlighting.

Features:
- Syntax highlighting (JSON, Python, YAML, etc.)
- Line numbers
- Word wrap
- Multiple themes
- Auto-formatting

Example:
    display = ResultsDisplay(title="API Response")
    display.display_json({"status": "success", "data": {...}})
    display.display_log("Server started on port 8000")

#### DataTableDisplay

Display data in a formatted table.

Features:
- Auto-formatting columns
- Sortable (when used with DataTable widget)
- Customizable styling
- Row highlighting

Example:
    display = DataTableDisplay(title="Test Results")
    display.set_data(
        headers=["Test", "Status", "Time"],
        rows=[
            ["test_api", "✓ PASS", "0.5s"],
            ["test_db", "✗ FAIL", "1.2s"],
        ]
    )

#### Banner

ASCII art banner display.

Features:
- Centered ASCII art
- Customizable colors
- Optional subtitle
- Border styling

Example:
    banner = Banner(
        art='''
        ╔═══════════════╗
        ║   MY APP      ║
        ╚═══════════════╝
        ''',
        subtitle="Version 1.0.0"
    )

#### BrandedPanel

Branded panel with custom styling.

Features:
- Custom border styles
- Brand colors
- Logo/icon support
- Themed content

Example:
    panel = BrandedPanel(
        title="My Application",
        content="Welcome to the dashboard",
        brand_color="bright_blue"
    )

#### WelcomeScreen

Welcome screen with banner and info.

Features:
- Large ASCII banner
- Version info
- Quick start tips
- Branded styling

Example:
    welcome = WelcomeScreen(
        app_name="My App",
        version="1.0.0",
        description="Production monitoring dashboard"
    )

#### StatusBanner

Status banner for top of dashboard.

Features:
- App name and status
- Uptime display
- Quick stats
- Color-coded health

Example:
    banner = StatusBanner(
        app_name="Production Server",
        status="running",
        uptime="2h 15m",
        stats={"Requests": "1,234", "Errors": "0"}
    )

#### MetricRow

Single metric row data.

#### StatusPanel

Live status display with color-coded health indicators.

Features:
- Color-coded status (success, error, warning, info)
- Visual indicators (●, ✗, ○, ◐)
- Reactive updates
- Customizable styling

Example:
    panel = StatusPanel(title="API Server")
    panel.set_success("Server running on port 8000")
    panel.set_error("Connection failed")
    panel.set_warning("High memory usage")

#### StatusCard

Compact status card with health indicator.

Similar to StatusPanel but more compact, designed for dashboard grids.

Example:
    card = StatusCard("MCP Server")
    card.update_status("running", "PID 12345 | Port 8001")

#### MetricsPanel

Display system metrics and statistics.

Features:
- Key-value metric display
- Auto-formatting (percentages, bytes, time)
- Customizable metrics
- Real-time updates

Example:
    panel = MetricsPanel(title="System Metrics")
    panel.update_metrics({
        "CPU Usage": "45.2%",
        "Memory": "2.3GB / 8GB",
        "Uptime": "2h 15m",
        "Requests": "1,234"
    })

#### StatusViewModel



#### UnifiedProgressWidget

Unified progress widget supporting multiple rendering backends.

#### CategoryStats



#### Observer

Observer pattern implementation with priority-based notifications and weak
references to prevent memory leaks.

Features:
- Priority-based notification ordering
- Weak references to observers
- Automatic cleanup of dead references
- Support for async and sync callbacks
- Error isolation (one observer failure doesn't affect others)

Example:
    >>> observer = Observer()
    >>>
    >>> def on_change(old_val, new_val):
    ...     print(f"Changed: {old_val} -> {new_val}")
    >>>
    >>> # Subscribe with priority (higher = called first)
    >>> observer.subscribe(on_change, priority=10)
    >>>
    >>> # Notify all observers
    >>> await observer.notify(old_value=5, new_value=10)
    >>>
    >>> # Unsubscribe
    >>> observer.unsubscribe(on_change)

#### StateChange

Represents a single state change.

#### Transaction

Represents a batch of state changes.

#### LifecycleHooks

Optional mixin exposing granular lifecycle callbacks for UI components.

#### EventHandling

Mixin exposing default event handler entry points.

#### StateManagement

Mixin that augments components with observer-friendly state operations.

#### PluginIntegration

Mixin that provides a lightweight plugin registry.

#### TextualComponent

Fallback component used when Textual is unavailable.

#### TextualContainer

Fallback container component mirroring the Textual API.

#### ComponentLifecycleState

Enumerated lifecycle states emitted by components.

#### Component

Fully featured component bundling lifecycle, event, state, and plugins.

#### ContainerComponent

Container-specific component with the same feature set as :class:`Component`.

#### BaseComponent

Abstract foundation for all Pheno TUI components.

#### ComponentStateStore

Mutable container that tracks component-specific data and metadata.

#### TypographySettings

Typography settings for a theme.

#### SpacingSettings

Spacing settings for a theme.

#### AnimationSettings

Animation settings for a theme.

#### ColorPalette

Comprehensive color palette with semantic names.

#### ThemeEngine

Main theme engine with CSS-like cascade resolution.

#### ColorBlindType

Types of color blindness.

#### AccessibilityMode

Accessibility mode utilities for theme adaptation.

#### Specificity

CSS-like specificity calculation.

#### StyleRule

CSS-like style rule with specificity.

#### EventType

Logical event categories emitted within the TUI.

#### EventPhase

Propagation phase for event dispatch.

#### OutputFormatter



#### CapturedLine

A single captured line with metadata.

#### LoggingHandler



#### StreamWriter



#### StreamCapture



#### EventPropagation

Handle capture and bubble phase dispatch across a propagation path.

#### AsyncEventHandler

Asynchronous handler signature.

#### PrioritizedHandler

Wrap a handler with priority metadata for ordering.

#### WCAGLevel

WCAG contrast compliance levels.

#### RGBColor

RGB color representation with utility methods.

### Functions

#### get_correlation_id

Get the correlation ID for the current context/thread.

Returns:
    The current correlation ID or None if not set

#### set_correlation_id

Set the correlation ID for the current context/thread.

Args:
    correlation_id: The correlation ID to set

#### generate_correlation_id

Generate a new correlation ID.

#### __init__



#### get_connection

Retrieve the metadata stored for a connection.

Args:
    connection_id: Identifier to look up.

Returns:
    :class:`ConnectionInfo` describing the connection, or ``None`` if
    the connection has been removed.

#### get_channel_subscribers

List the connection identifiers subscribed to ``channel``.

Args:
    channel: Channel name to inspect.

Returns:
    List of connection identifiers currently subscribed.

#### supabase

Create Supabase backend.

#### postgres



#### neon

Create a database client with Neon adapter.

Neon is a serverless PostgreSQL platform with database branching support.

Args:
    connection_string: Neon connection string (from dashboard)
    api_key: Neon API key for management operations
    project_id: Neon project ID
    **kwargs: Additional connection options

Returns:
    Database instance

Example:
    ```python
    # Using environment variables
    db = Database.neon()

    # With explicit credentials
    db = Database.neon(
        connection_string="postgresql://...",
        api_key="neon_api_key",
        project_id="project_id"
    )
    ```

#### set_access_token

Set user's access token for RLS context.

#### _add_tenant_filter

Add tenant_id filter if in tenant context.

#### get_supabase

Return a cached Supabase client using the supplied access token.

#### reset_client_cache

Clear the cached Supabase clients.

#### cache_stats

Return simple statistics about the Supabase client cache.

#### _ensure_list



#### _ensure_args_list



#### list_roles



#### get_role



#### _read_json_file

Read JSON file with proper error handling.

#### get_clink_config_env_var

Get the environment variable name for CLI clients config based on availability.

#### get_registry

Get the clink registry for schema building.

#### _load



#### reload

Reload configurations from disk.

#### list_clients



#### get_client

Get a client from the pool.

#### _iter_config_files

Iterate over all configuration files in search paths.

#### _build_search_paths

Build list of search paths for configuration files.

#### _get_pheno_config_path

Get pheno-sdk configuration path if available.

#### _get_env_config_path

Get environment-specified configuration path.

#### _yield_config_files_from_path

Yield configuration files from a single path.

#### _resolve_config



#### _resolve_executable



#### _merge_env



#### _resolve_roles



#### _resolve_prompt_path



#### _resolve_optional_path



#### _resolve_path



#### _get_env



#### get_pheno_config



#### get

Fetch a stored value, returning ``default`` when missing.

#### _discover_project_root

Best-effort discovery of the consuming project's root directory.

#### __post_init__



#### is_stale

Determine if the service record has expired based on ``last_seen``.

Args:
    max_age_seconds: Maximum allowed inactivity window before the entry
        is considered stale.

Returns:
    ``True`` when the record exceeds the inactivity window.

#### update_seen

Refresh the ``last_seen`` timestamp to the current time.

Returns:
    Updated timestamp value, enabling fluent-style chaining when desired.

#### _load_registry

Hydrate the in-memory registry state from the persisted JSON file.

The method acquires a shared lock so concurrent readers avoid interfering with
writers, and gracefully skips malformed entries to keep the registry usable even
when partial corruption occurs.

#### _save_registry

Persist the registry to disk using an atomic rename strategy.

Steps:
    1. Remove stale entries to avoid propagating dead registrations.
    2. Serialize the registry into a temporary file under an exclusive lock.
    3. Atomically replace the target file with the fresh snapshot.

Raises:
    ConfigurationError: If writing to disk fails for any reason.

#### _cleanup_stale_entries

Expire services that have not updated their heartbeat within
``max_age_seconds``.

Args:
    max_age_seconds: Threshold in seconds after which entries are removed.

#### register_service

Ensure a buffer exists for the provided service.

#### get_service

Get service from container.

#### update_service

Apply partial updates to a service and persist the mutation.

Args:
    service_name: Registry key to update.
    **kwargs: Field/value pairs that should be applied to the existing record.

Returns:
    Updated :class:`ServiceInfo` instance or ``None`` if the service is missing.

#### unregister_service

Remove a service from the registry and persist the change.

Args:
    service_name: Identifier of the service to delete.

Returns:
    ``True`` when the service existed and was removed, otherwise ``False``.

#### get_all_services

Produce a shallow copy of all registered services.

Returns:
    Mapping from service names to their :class:`ServiceInfo` entries.

#### get_allocated_ports

Get all currently allocated ports.

Returns:
    Dictionary mapping port numbers to allocations

#### is_port_registered

Determine whether a port belongs to a known service.

Args:
    port: TCP port number to check.

Returns:
    Service name when the port is assigned, otherwise ``None``.

#### get_canonical_port

Return the previously assigned port for a service.

This helps services consistently reuse the same port across runs when possible.

#### validate_port_range

Check whether a port falls inside the allowed allocation window.

Args:
    port: TCP port number under consideration.

Returns:
    ``True`` if the port is permitted, otherwise ``False``.

#### allocate_port

Allocate a port for a service with intelligent conflict resolution.

#### _try_allocate_specific_port

Try to allocate a specific port, handling conflicts.

#### _allocate_dynamic_port

Allocate a port dynamically within the allowed range.

#### _get_os_assigned_port

Get a port assigned by the OS.

#### _is_our_service_instance

Check if a process is a stale instance of our service.

#### release_port

Release a port back to the pool.

Args:
    port: Port number to release
    agent_id: Optional agent ID (for verification)

Returns:
    True if port was released, False if not found

#### get_service_port



#### list_allocated_services

Get all currently allocated services and their ports.

#### python_asgi_service

Shorthand for creating Python ASGI service config.

Args:
    name: Service name
    app_path: ASGI application path ("module:app")
    port: Port number
    **kwargs: Additional ServiceTemplate fields

Returns:
    ServiceConfig ready to use

#### go_http_service

Shorthand for creating Go HTTP service config.

Args:
    name: Service name
    module_dir: Go module directory
    port: Port number
    **kwargs: Additional ServiceTemplate fields

Returns:
    ServiceConfig ready to use

#### nextjs_service

Shorthand for creating Next.js service config.

Args:
    name: Service name
    app_dir: Next.js app directory
    port: Port number
    **kwargs: Additional ServiceTemplate fields

Returns:
    ServiceConfig ready to use

#### to_service_config

Convert to ServiceInfra ServiceConfig.

#### add_resource



#### add_resource_adapter

Add a pre-configured resource adapter.

Args:
    adapter: ResourceAdapter instance

Example:
    >>> from pheno.infra.adapters.docker import DockerAdapter
    >>> adapter = DockerAdapter("my-db", {...})
    >>> manager.add_resource_adapter(adapter)

#### get_status

Get MCP extensions status.

#### get_all_status

Get status of all processes.

Returns:
    List of process statuses

#### _setup_signal_handlers



#### add_service



#### print_status

Print formatted status of all services.

#### _save_state

Save current orchestrator state to disk.

#### load_state

Load saved state from disk.

#### signal_handler



#### get_name

Return the tool's name.

#### get_description

Return the tool's description.

#### get_system_prompt

Get a system prompt by name, with fallback to built-in defaults.

Args:
    prompt_name: Name of the prompt (without .txt extension)
    prompts_dir: Directory containing prompt .txt files (optional)

Returns:
    The prompt content as a string

#### get_default_temperature

Return the default temperature for this tool.

#### requires_model

Return whether this tool requires AI model access.

#### get_model_category

Return the model category (fast, balanced, powerful).

#### get_request_model

Return the request model class.

Simple tools use the base ToolRequest by default. Override this if your tool
needs a custom request model.

#### get_tool_fields

Return tool-specific field definitions.

This method should return a dictionary mapping field names to their
JSON schema definitions. Common fields (model, temperature, etc.)
are added automatically by the base class.

Returns:
    Dict mapping field names to JSON schema objects

#### get_input_schema

Generate the complete input schema using SchemaBuilder.

This method automatically combines:
- Tool-specific fields from get_tool_fields()
- Common fields (temperature, thinking_mode, etc.)
- Model field with proper auto-mode handling
- Required fields from get_required_fields()

Tools can override this method for custom schema generation while
still benefiting from SimpleTool's convenience methods.

Returns:
    Complete JSON schema for the tool

#### _build_parser



#### main

Main entry point for desktop launcher.

#### from_row



#### as_dict

Return a dictionary representation suitable for persistence.

#### from_dict

Deserialize an event from a dictionary.

#### to_dict

Serialize the event to a dictionary.

#### hash



#### is_empty

Check if queue is empty.

#### render



#### fetch_remote_snapshot



#### load_local_snapshot



#### save_snapshot



#### diff_snapshots



#### check

Run all quality checks.

#### update

Merge multiple values into the state.

#### report

Generate detailed error reports for all failed tests.

Args:
    results: List of test result dictionaries
    metadata: Test run metadata

#### create_vercel_checks



#### _file_exists



#### _file_executable



#### _file_contains



#### _no_uncommitted_changes



#### run_check



#### run_all



#### run_backfill

Run backfill synchronously.

#### get_content_generator

Get the global content generator instance.

#### _register_default_providers

Register default LLM providers.

#### _create_system_prompt

Create system prompt based on content type.

#### _create_fallback_response

Create fallback response when generation fails.

#### _fallback_title

Generate fallback title.

#### _fallback_status

Generate fallback status message.

#### _fallback_generic

Generate fallback generic content.

#### _get_cache_key

Generate cache key for operation.

#### get_registry_manager

Get the global registry manager instance.

#### get_tool_registry



#### get_provider_registry



#### get_adapter_registry



#### get_plugin_registry



#### get_resource_registry

Get the resource registry.

#### get_component_registry

Get the component registry.

#### _initialize_default_registries

Initialize default registries.

#### create_registry

Create a new registry.

Args:
    name: Name of the registry
    registry_type: Type of registry to create
    config: Optional configuration for the registry

Returns:
    The created registry instance

#### list_registries

List all registry names.

#### get_registry_config

Get configuration for a registry.

#### register_item

Register an item in a specific registry.

Args:
    registry_name: Name of the registry
    key: Key for the item
    item: Item to register
    replace: Whether to replace existing item
    metadata: Optional metadata
    priority: Priority for the item

#### get_item

Get an item from a registry.

#### list_items

List items in a registry.

#### unregister_item

Unregister an item from a registry.

#### clear_registry

Clear all items from a registry.

#### auto_discover

Auto-discover items for a registry.

#### get_registry_summary

Get a summary of all registries.

#### migrate_from_dict

Migrate items from a dictionary.

#### migrate_from_old_registry

Migrate items from an old registry implementation.

#### _insert_path

Insert path into sys.path if it exists and isn't already present.

Returns True if inserted, False otherwise.

#### _find_upwards

Search upwards from start for any of the given directory names.

Returns a list of matching directories in closest-first order.

#### ensure_project_src_on_path

Ensure the caller project's src directory is importable.

Returns True if a src path was added or already present.

#### ensure_pheno_sdk_on_path

Ensure the pheno-sdk repository root and its src are importable.

Returns True if any path was added or already present.

#### ensure_kinfra_on_path

Ensure KInfra library directory is importable if present.

#### bootstrap

Perform standard path bootstrapping for repos that integrate Pheno-SDK.

Order of operations:
  1) Ensure project src is first (import your own code)
  2) Ensure KInfra (optional)
  3) Ensure pheno-sdk (tools/configs/etc.)

#### name



#### version



#### description



#### supported_extensions



#### create_analyzer



#### get_default_config



#### register_plugin

Register or replace a plugin implementation.

#### unregister_plugin

Remove a plugin from the component.

#### get_plugin

Retrieve a plugin instance by name.

#### get_analyzer_class

Get an analyzer class by name.

#### list_plugins

List all registered plugin names.

#### list_analyzers

List all registered analyzer names.

#### get_plugin_info

Get plugin information.

#### load_plugin_from_module

Load a plugin from a Python module.

#### load_plugins_from_package

Load all plugins from a package.

#### get_config

Get configuration value(s).

#### list_configs

List all loaded configuration files.

#### create_custom_config

Create a custom configuration based on a preset.

#### register_tool



#### unregister_tool

Unregister a tool from the registry.

#### get_tool_class

Get a tool class by name.

#### create_tool

Create a tool instance.

#### list_tools



#### get_tool_info

Get tool information.

#### get_tool_config

Get configuration for a specific tool.

#### update_tool_config

Update configuration for a specific tool.

#### get_tool_metadata

Get metadata for a tool.

#### update_tool_metadata

Update tool metadata.

#### get_tools_by_category

Get tools by category.

#### get_tools_by_extension

Get tools that support a file extension.

#### export_quality_framework

Export quality analysis framework.

#### import_quality_framework

Import quality analysis framework.

#### export_framework

Export the quality analysis framework.

#### _export_core_framework

Export core framework files.

#### _export_tools

Export quality analysis tools.

#### _export_configurations

Export configuration presets.

#### _export_examples

Export usage examples.

#### _create_manifest

Create package manifest.

#### _get_basic_usage_example

Get basic usage example.

#### _get_advanced_usage_example

Get advanced usage example.

#### _get_config_example

Get configuration example.

#### import_framework

Import the quality analysis framework.

#### _copy_framework_files

Copy framework files to project.

#### _install_requirements

Install Python requirements.

#### _create_integration_files

Create integration files for the target project.

#### _get_setup_script

Get setup script content.

#### _get_usage_guide

Get usage guide content.

#### add_issue

Add a quality issue to the report.

#### add_issues

Add multiple quality issues to the report.

#### add_tool_report

Add a tool-specific report.

#### finalize

Finalize metrics collection.

Args:
    success: Whether the operation succeeded
    error: Optional exception if operation failed

#### _calculate_quality_score

Calculate overall quality score (0-100)

#### get_issues_by_severity

Get issues filtered by severity.

#### get_issues_by_tool

Get issues filtered by tool.

#### get_issues_by_type

Get issues filtered by type.

#### get_issues_by_file

Get issues filtered by file.

#### to_json

Export metrics in JSON format.

#### analyze_file

Analyze a single file for code smells.

#### analyze_directory

Analyze a directory for code smells.

#### get_issues

Get all detected issues.

#### clear_issues

Clear all detected issues.

#### get_metrics



#### import_report

Import a quality report.

#### can_import

Check if file is XML.

#### _parse_json_data

Parse JSON data into QualityReport.

#### _parse_issue

Parse issue data.

#### _parse_csv_row

Parse CSV row into QualityIssue.

#### _parse_xml_issue

Parse XML issue element.

#### get_supported_formats

Get list of supported export formats.

#### get_text



#### integrate_quality_framework

Integrate quality framework into a project.

#### export_framework_for_project

Export framework specifically for a project type.

#### setup_for_project

Setup quality framework for a specific project.

#### _create_project_config

Create ProjectConfig object from parsed values.

#### _create_integration_scripts

Create integration scripts for the project.

#### _get_main_analysis_script

Get main analysis script content.

#### _get_makefile_integration

Get Makefile integration content.

#### _get_cli_integration

Get CLI integration content.

#### _get_ci_integration

Get CI/CD integration content.

#### generate_issue_id

Generate a unique issue ID.

#### generate_report_id

Generate a unique report ID.

#### normalize_file_path

Normalize file path for consistent comparison.

#### matches_pattern

Check if file path matches any of the given patterns.

#### should_exclude_file

Check if file should be excluded based on patterns.

#### get_file_extension



#### is_python_file

Check if file is a Python file.

#### is_source_file

Check if file is a source code file.

#### calculate_confidence_score

Calculate confidence score for an issue.

#### categorize_issue

Categorize an issue based on type and tool.

#### generate_tags

Generate tags for an issue.

#### format_duration

Format duration in human-readable format.

#### format_file_size

Format file size in human-readable format.

#### calculate_quality_trend

Calculate quality trend.

#### get_priority_score

Calculate priority score (1-10, higher is more important)

#### group_issues_by_file

Group issues by file path.

#### group_issues_by_type

Group issues by type.

#### group_issues_by_severity

Group issues by severity.

#### export



#### _generate_html

Generate HTML content.

#### _generate_markdown

Generate Markdown content.

#### _generate_xml

Generate XML content.

#### _register_default_tools

Register default quality analysis tools.

#### analyze_project

Analyze a project with all enabled tools.

#### _analyze_parallel

Run analysis in parallel.

#### _analyze_sequential

Run analysis sequentially.

#### _run_tool

Run a single tool.

#### export_report

Export a quality report.

#### get_available_tools

Get list of available tools.

#### get_available_configs

Get list of available configuration presets.

#### create_config

Create a configuration from preset with overrides.

#### generate_summary

Generate a summary of the quality report.

#### _determine_quality_status

Determine overall quality status.

#### _generate_recommendations

Generate architecture improvement recommendations.

#### _cached_embedding_service

Return the default embedding service (Vertex AI if available).

#### get_vector_embedding_service

Return the shared embedding service instance.

#### _cached_vector_search_service

Return a cached vector search service using the default Supabase client.

#### get_vector_search_service

Return a configured vector search service.

Args:
    supabase_client: Optional Supabase client to use. When omitted, a cached
        service bound to the default service-role client is returned.
    cache: If False, always create a new service even for the default client.

#### reset_vector_services

Reset cached embedding and vector search services.

#### vector_provider_status

Return availability flags for known embedding providers.

#### pop_env

Pop an environment variable.

#### collect_env

Collect environment variables that start with the given prefix (case-insensitive).

#### get_env_bool



#### config_manager

Retrieve the process-wide configuration manager singleton.

Returns:
    Shared :class:`ConfigManager` instance used across the SDK.

#### parse_dotenv

Parse .env file into dictionary.

Args:
    path: Path to .env file

Returns:
    Dictionary of environment variables

Example:
    >>> env_vars = parse_dotenv(".env.local")

#### load_env_cascade

Load environment variables with cascading priority.

Priority: env_files > .env.local > .env

Args:
    root_dirs: Directories to search for .env files
    env_files: Specific .env files to load

Returns:
    Merged environment variables

Example:
    >>> env = load_env_cascade(
    ...     root_dirs=[Path(".")],
    ...     env_files=[Path(".env.production")]
    ... )

#### from_env

Create factory from environment variables.

Returns:
    Configured repository factory

#### from_file

Load credentials from JSON file.

Args:
    path: File path

Returns:
    CredentialStore with loaded credentials

#### load

Return the template contents for the requested page.

#### load_from_dict

Overwrite the registry with values from ``data``.

Args:
    data: Nested mapping representing the target configuration state.

Raises:
    RuntimeError: If the manager has been frozen via :meth:`freeze`.

#### load_from_env

Populate the registry from environment variables honouring ``prefix``.

Args:
    prefix: Upper-case prefix (e.g., ``PHENO_``) used to filter variables.

Raises:
    RuntimeError: When invoked while the manager is frozen.

#### set

Persist a value and bump the version counter.

#### freeze

Prevent further mutations to the registry.

Ideal once application bootstrap completes to guard against accidental runtime
writes.

#### unfreeze

Re-enable mutations following a :meth:`freeze` call.

Primarily intended for administrative utilities or tests that require temporary
write access.

#### _load_legacy_morph_env



#### get_morph_settings



#### get_router_settings



#### get_integration_settings



#### load_provider_configs_from_env

Load provider configurations from environment variables.

#### generate_key

Generate encryption key.

Args:
    length: Key length in bytes

Returns:
    Base64-encoded key

#### encrypt

Encrypt sensitive data.

#### decrypt

Decrypt sensitive data.

#### encrypt_dict

Encrypt sensitive values in dictionary.

Args:
    data: Dictionary to encrypt
    key: Encryption key
    sensitive_keys: Keys to encrypt (if None, encrypts all string values)

Returns:
    Dictionary with encrypted values

#### decrypt_dict

Decrypt sensitive values in dictionary.

Args:
    data: Dictionary to decrypt
    key: Encryption key
    sensitive_keys: Keys to decrypt (if None, attempts to decrypt all string values)

Returns:
    Dictionary with decrypted values

#### _b64_encode

Base64url encode.

#### _b64_decode

Base64url decode.

#### create_jwt

Create JWT token.

Args:
    payload: Token payload (claims)
    secret: Secret key for signing
    algorithm: Signing algorithm (HS256, HS512)
    expires_in: Expiration time in seconds

Returns:
    JWT token string

Example:
    token = create_jwt({'user_id': 123}, secret='my-secret', expires_in=3600)

#### verify_jwt

Verify and decode JWT token.

Args:
    token: JWT token string
    secret: Secret key for verification
    algorithms: Allowed algorithms (default: ['HS256', 'HS512'])

Returns:
    Decoded payload

Raises:
    JWTError: If token is invalid or expired

#### decode_jwt

Decode JWT token and return claims.

Args:
    token: JWT token string
    verify_signature: Whether to verify signature
    secret: Secret key for verification (required if verify_signature=True)
    algorithms: List of accepted algorithms (default: ["HS256", "RS256"])

Returns:
    Dictionary of JWT claims

Raises:
    ValueError: If token is invalid
    RuntimeError: If PyJWT not installed

Example:
    claims = decode_jwt(token)
    user_id = claims.get("sub")
    email = claims.get("email")

#### hash_password

Hash a password securely.

#### verify_password

Verify a password against its hash.

#### hash_string

Hash string using specified algorithm.

Args:
    data: String to hash
    algorithm: Hash algorithm (md5, sha1, sha256, sha512)

Returns:
    Hex-encoded hash

#### hash_bytes

Hash bytes using specified algorithm.

#### generate_token

Generate a JWT token.

#### generate_url_safe_token

Generate URL-safe random token.

Args:
    length: Token length in bytes

Returns:
    URL-safe base64-encoded token

#### hmac_sign

Create HMAC signature for message.

Args:
    message: Message to sign
    secret: Secret key
    algorithm: Hash algorithm

Returns:
    Hex-encoded HMAC signature

#### hmac_verify

Verify HMAC signature.

Args:
    message: Original message
    signature: HMAC signature to verify
    secret: Secret key
    algorithm: Hash algorithm

Returns:
    True if signature is valid

#### generate_fingerprint

Generate short fingerprint for data.

Args:
    data: Data to fingerprint

Returns:
    Short hash suitable for display (12 chars)

#### detect_pii

Detect PII in text.

Args:
    text: Text to scan
    patterns: Custom patterns (None = use defaults)

Returns:
    List of PII detections

#### redact_pii

Redact PII from text.

Args:
    text: Text to redact
    show_type: Whether to show PII type

Returns:
    Redacted text

#### mask_email

Mask email address.

Example: john.doe@example.com -> j******e@example.com

#### mask_phone

Mask phone number.

Example: 555-123-4567 -> ***-***-4567

#### detect

Detect project context from disk.

#### _detect_with_presidio

Run Presidio analyzer if available.

#### redact

Redact sensitive information from text.

Args:
    text: Text to redact

Returns:
    Redacted text

#### mask

Mask PII (show partial information).

Args:
    text: Text to mask
    pattern_names: Specific patterns to mask (None = all)
    show_first: Number of characters to show at start
    show_last: Number of characters to show at end
    mask_char: Character to use for masking

Returns:
    Masked text

Example:
    mask("john@example.com", show_first=2, show_last=4)
    # "jo********.com"

#### provider_type



#### supports_refresh



#### get_auth_url



#### supports_method



#### register_adapter



#### create_adapter



#### get_adapter

Return the adapter class registered under the supplied name.

#### list_adapters



#### get_adapters_by_method



#### register_provider



#### create_provider



#### get_provider



#### list_providers



#### ensure_oauth_credentials

Ensure OAuth credentials exist, prompting if necessary.

Convenience function for one-time credential setup.

Args:
    app_name: Application name
    required_fields: Required credential fields
    config_dir: Custom config directory

Returns:
    Dictionary of credentials

Example:
    creds = ensure_oauth_credentials(
        "my_app",
        required_fields=["client_id", "client_secret"]
    )

#### prompt_for_value

Prompt user for a single value with validation.

Args:
    field_name: Name of the field
    prompt: Custom prompt text
    secure: Use secure input (hidden)
    default: Default value
    validator: Optional validation function

Returns:
    User-provided value

Example:
    email = prompt_for_value(
        "email",
        validator=lambda x: "@" in x
    )

#### get_credentials

Get credentials, prompting for missing values.

Args:
    required_fields: Required credential fields
    optional_fields: Optional credential fields
    prompts: Custom prompts for each field
    secure_fields: Fields to prompt for securely (hidden input)

Returns:
    Dictionary of credentials

Example:
    creds = manager.get_credentials(
        required_fields=["client_id", "client_secret"],
        secure_fields={"client_secret"}
    )

#### load_credentials

Load credentials from storage.

Returns:
    Dictionary of stored credentials

#### save_credentials

Save credentials to storage.

Args:
    credentials: Credentials to save

#### clear_credentials

Remove saved credentials.

#### has_credentials

Check if all required credentials are available.

Args:
    required_fields: Fields to check for

Returns:
    True if all required fields are present

#### is_expired

Check if session is expired.

#### delete



#### clear



#### cleanup_expired

Remove all expired tokens.

Returns:
    Number of tokens removed

#### _encrypt



#### _decrypt



#### save

Persist the merged configuration to disk.

#### _load_all

Load all tokens from storage.

#### _save_all

Save all tokens to storage.

#### from_auth_tokens



#### to_auth_tokens



#### load_all



#### save_all



#### generate_totp_secret

Generate a random base32-encoded TOTP secret.

Returns:
    Base32-encoded secret suitable for TOTP

Example:
    secret = generate_totp_secret()
    handler = TOTPHandler(secret)

#### _get_secret_bytes

Decode base32 secret to bytes.

#### _get_counter

Get time counter for timestamp.

#### _generate_otp

Generate OTP for given counter.

Args:
    counter: Time counter value

Returns:
    OTP code as string

#### generate

Generate a new deployment ID.

#### verify

Verify the acceptance criterion.

#### get_remaining_seconds

Get seconds remaining until next code.

Args:
    timestamp: Optional timestamp (defaults to current time)

Returns:
    Seconds until next interval

#### register_totp

Register TOTP secret for user.

Args:
    user_id: User identifier
    secret: Base32-encoded TOTP secret

#### verify_totp

Verify TOTP code for user.

Args:
    user_id: User identifier
    code: TOTP code to verify
    window: Time window for verification

Returns:
    True if code is valid

#### generate_totp

Generate current TOTP code for user.

Args:
    user_id: User identifier

Returns:
    Current TOTP code or None if not registered

#### register_sms_callback

Register SMS verification callback.

Args:
    callback: Function that takes (phone, code) and returns bool

#### verify_sms

Verify SMS code.

Args:
    phone: Phone number
    code: SMS code to verify

Returns:
    True if code is valid

#### is_refreshable

Return True if the token can be refreshed.

#### _ensure_playwright

Ensure playwright is available.

#### authenticate

Simulate authentication.

Args:
    auth_url: Authorization URL (not used)
    success_pattern: Success pattern (not used)
    credentials: Credentials (not used)
    fill_callback: Fill callback (not used)

Returns:
    Mock response

#### start_browser

Mock browser start.

#### stop_browser

Mock browser stop.

#### __enter__



#### __exit__



#### register_mfa_adapter

Alias mirroring the legacy function name.

#### set_token_manager

Install the token manager used for session persistence.

#### set_credential_manager

Install the credential manager used for secure secret storage.

#### get_available_providers

Return all registered provider names.

#### get_available_mfa_adapters

Return all registered MFA adapter names.

#### get_mfa_adapters_for_method

Return adapters that support the supplied MFA method.

#### _make_storage_key

Derive a consistent storage key for token persistence.

#### create_auth_header

Create authorization header from token.

Args:
    token: Access token
    token_type: Token type (default: Bearer)

Returns:
    Authorization header dict

Example:
    headers = create_auth_header("abc123")
    # {'Authorization': 'Bearer abc123'}

#### set_tokens

Store tokens for a key.

Args:
    key: Storage key (e.g. user ID)
    tokens: Token set to store

#### get_tokens

Get tokens for session.

#### get_access_token

Get valid access token, refreshing if necessary.

Args:
    auto_refresh: Automatically refresh if expired

Returns:
    Valid access token or None

#### exchange_code_for_tokens

Exchange authorization code for tokens.

Args:
    code: Authorization code
    redirect_uri: Redirect URI used in authorization
    code_verifier: PKCE code verifier

Returns:
    OAuth tokens

Raises:
    NotImplementedError: Requires HTTP client implementation

#### refresh_tokens

Refresh access token using refresh token.

Args:
    refresh_token: Refresh token

Returns:
    New OAuth tokens

Raises:
    NotImplementedError: Requires HTTP client implementation or custom callback

#### revoke_tokens

Revoke and clear current tokens.

#### is_authenticated



#### load_plugin

Dynamically import a plugin module by dotted path.

#### _patch_streamable_manager



#### make_serverless_http_app

Return an ASGI application configured for serverless environments.

#### get_model_registry



#### get_all_model_capabilities



#### resolve_model



#### list_models

Return all registered model names.

#### get_model_info

Get information about a specific model from the catalog.

Args:
    provider_type: The provider type
    model_name: Name of the model to look up

Returns:
    Model information dictionary, potentially empty

#### validate_model_name

Validate if this provider can handle the given model name.

#### get_preferred_model

Get preferred model for a given tool category from allowed models.

#### get_provider_type

Get the provider type for this instance.

#### __new__

Singleton pattern.

#### _get_api_key

Get API key for a provider from environment.

#### list_available_providers

List all available providers (with API keys).

#### list_all_models

List all models from all available providers.

#### find_provider_for_model

Find which provider can handle a given model name.

#### reset

Reset form to default values.

#### get_env

Get environment variable with optional default.

#### estimate_tokens

Rough token estimator (1 token ≈ 4 characters).

#### estimate_completion_cost

Estimate USD cost using litellm cost tables.

#### get_allocator

Get allocator instance for a given strategy.

Args:
    strategy: Allocation strategy
    **kwargs: Additional arguments for allocator initialization

Returns:
    Allocator instance

#### calculate_allocation

Calculate adaptive allocation based on historical patterns.

#### render_budget_status

Render budget status using renderer.

#### render_allocation_report

Render allocation report using renderer.

#### render_utilization_summary

Render utilization summary combining budgets and allocations.

Args:
    budgets: Dictionary of budgets
    allocations: List of allocations
    format_type: Output format ('text', 'json', 'html')

Returns:
    Formatted utilization summary

#### render_budgets

Render budgets as HTML table.

#### render_allocations

Render allocations as HTML table.

#### render_utilization

Render utilization summary as HTML.

#### _calculate_utilization_metrics

Calculate utilization metrics.

#### render_budget_alerts

Generate alerts for budget thresholds.

#### render_recommendations

Generate recommendations based on usage patterns.

#### available_units

Calculate available resource units.

#### utilization_rate

Calculate utilization rate.

#### allocation_rate

Calculate allocation rate.

#### is_exhausted

Check if budget is exhausted.

#### is_near_limit

Check if near budget limit.

#### remaining_units

Calculate remaining resource units.

#### usage_rate

Calculate usage rate.

#### efficiency_score

Calculate allocation efficiency score.

Returns 1.0 for perfect efficiency (used exactly what was allocated), lower
values indicate waste, higher values indicate exceeded allocation.

#### load_from_file

Load budgets from configuration file.

Supports JSON, YAML, and TOML formats.

#### load_from_config

Load budgets from configuration dictionary.

#### _create_budget_from_config

Create ResourceBudget from configuration.

#### _calculate_period_end

Calculate period end time based on period type.

#### _validate_budget

Validate budget parameters.

#### _validate_hourly_budget

Validate hourly budget constraints.

#### _validate_daily_budget

Validate daily budget constraints.

#### _validate_weekly_budget

Validate weekly budget constraints.

#### _validate_monthly_budget

Validate monthly budget constraints.

#### _load_json

Load JSON configuration.

#### _load_yaml

Load YAML configuration.

#### _load_toml

Load TOML configuration file.

#### create_allocation

Create a new resource allocation with validation.

#### _validate_allocation_params

Validate allocation parameters.

#### load_from_history

Load allocations from history data.

#### _create_allocation_from_history

Create ResourceAllocation from history data.

#### _parse_datetime

Parse datetime string to datetime object.

#### load_limits_from_config

Load resource limits from configuration file.

#### _parse_limits_config

Parse limits configuration dictionary.

#### _parse_single_limit

Parse a single limit configuration.

#### record_usage

Record a usage event.

Args:
    resource_type: Type of resource
    units: Amount of units used
    cost_usd: Cost in USD
    metadata: Additional metadata

#### get_usage



#### get_total_usage

Get total usage for a time period.

Args:
    resource_type: Filter by resource type
    start_time: Start of time range
    end_time: End of time range

Returns:
    Dictionary with total units and cost

#### _cleanup_old_events

Remove events older than retention period.

#### analyze_trends

Analyze usage trends over time.

Args:
    resource_type: Type of resource to analyze
    days: Number of days to analyze

Returns:
    Dictionary with trend analysis

#### get_peak_usage_times

Identify peak usage times.

Args:
    resource_type: Type of resource to analyze
    days: Number of days to analyze

Returns:
    Dictionary with peak usage information

#### analyze_allocation_efficiency

Analyze allocation efficiency.

Args:
    allocation_history: List of completed allocations

Returns:
    Dictionary with efficiency metrics

#### predict_budget_exhaustion

Predict when a budget will be exhausted.

Args:
    budget: Budget to analyze
    resource_type: Type of resource

Returns:
    Predicted exhaustion datetime or None

#### recommend_budget

Recommend budget based on historical usage.

Args:
    resource_type: Type of resource
    period: Budget period
    historical_days: Days of history to consider
    buffer_multiplier: Safety buffer multiplier

Returns:
    Dictionary with budget recommendation

#### forecast_usage

Forecast future usage.

Args:
    resource_type: Type of resource
    days_ahead: Number of days to forecast
    historical_days: Days of history to use

Returns:
    Dictionary with usage forecast

#### save_budget

Save budget to both cache and storage.

#### load_budget

Load a budget.

#### save_allocation

Save allocation to both cache and storage.

#### load_allocation

Load an allocation.

#### get_all_allocations

Get all allocations.

#### save_usage_event

Save a usage event.

#### get_usage_events

Get usage events.

#### _make_key

Make a unique key for a metric.

#### _serialize_budget

Serialize budget to dict.

#### _deserialize_budget

Deserialize budget from dict.

#### _serialize_allocation

Serialize allocation to dict.

#### _deserialize_allocation

Deserialize allocation from dict.

#### get_budget

Get budget from cache, loading from storage if needed.

#### get_allocation

Get allocation information for a port.

Args:
    port: Port number

Returns:
    PortAllocation or None if not allocated

#### list_budgets

List all cached budgets, optionally filtered by resource type.

#### list_allocations

List cached allocations with optional filters.

#### invalidate_cache

Invalidate cache entries matching pattern.

#### sync_to_storage

Force sync all cached data to storage.

#### get_cache_stats



#### migrate_data

Migrate data from another storage backend.

#### backup_data

Create backup of storage data.

#### restore_data

Restore storage data from backup.

#### compact_storage

Compact storage to remove old/unused data.

#### get_storage_info

Get storage backend information.

#### set_budget

Set or update a budget for a resource and period.

#### allocate_resource

Allocate resources for a request.

#### _validate_and_adjust_request

Validate request and adjust units based on limits.

#### _determine_allocation_strategy

Determine the allocation strategy to use.

#### _get_resource_budgets

Get relevant budgets for the resource type.

#### _calculate_allocation

Calculate allocation using the specified strategy.

#### _validate_budget_constraints

Validate that all budgets can accommodate the allocation.

#### _create_and_store_allocation

Create and store the resource allocation.

#### _update_budgets

Update budgets with the allocated resources.

#### update_usage

Update resource usage for an allocation.

#### complete_allocation

Mark an allocation as completed.

#### get_budget_status

Get budget status.

#### get_allocation_statistics

Get allocation statistics.

#### set_resource_limit

Set resource limit for process management.

Args:
    resource: Resource name (e.g., 'concurrent_processes', 'memory_mb')
    limit: Maximum limit value

#### set_operation_strategy

Set allocation strategy for an operation type.

#### shutdown

Shutdown CLI bridge and terminate all processes.

#### get_stats

Return diagnostic information about the bus.

#### _setup_executors

Setup different types of executors.

#### get_executor_stats

Get statistics for all executors and worker pools.

#### choose_executor_type

Choose the best executor type for a task.

#### update_with_task

Update metrics with a task.

#### get_success_rate

Get task success rate.

#### get_failure_rate

Get task failure rate.

#### get_retry_rate

Get task retry rate.

#### start_task_tracking

Start tracking progress for a task.

#### update_task_progress

Update progress for a task.

#### complete_task_tracking

Complete tracking for a task.

#### start_workflow_tracking

Start tracking progress for a workflow.

#### update_workflow_progress

Update progress for a workflow.

#### complete_workflow_tracking

Complete tracking for a workflow.

#### get_task_progress

Get progress for a task.

#### get_workflow_progress

Get progress for a workflow.

#### add_progress_callback

Add a progress callback.

#### _notify_progress

Notify progress callbacks.

#### record_task

Record a task execution.

#### get_metrics_dict

Get metrics as dictionary.

#### get_recent_tasks

Get recent task executions.

#### get_throughput_metrics

Get throughput metrics.

#### start_task_progress

Start tracking progress for a task.

#### complete_task_progress

Complete progress tracking for a task.

#### start_workflow_progress

Start tracking progress for a workflow.

#### complete_workflow_progress

Complete progress tracking for a workflow.

#### add_alert_callback

Add an alert callback.

#### set_threshold

Set alert threshold for a metric.

#### _check_alerts

Check if metrics exceed alert thresholds.

#### _trigger_alert

Trigger an alert.

#### get_health_status

Get overall health status.

#### is_successful

Check if task completed successfully.

#### is_failed

Check if task failed.

#### is_running

Determine whether a monitored process (or override) is running.

#### _get_task_file

Get the file path for a task.

#### _serialize_task

Serialize a task to a dictionary.

#### _deserialize_task

Deserialize a task from a dictionary.

#### _serialize_result

Serialize a task result.

#### _deserialize_result

Deserialize a task result.

#### _init_database

Initialize the database schema.

#### _row_to_task

Convert a database row to a Task object.

#### dummy_func



#### is_active

Whether process appears to be active.

#### update_activity

Update last activity timestamp.

#### __hash__



#### __eq__



#### start



#### complete



#### fail



#### duration_seconds

Get deployment duration in seconds.

#### is_success

Check if result is successful.

#### complete_step

Complete a workflow step.

#### setup_mcp

Setup MCP with default in-memory adapters.

Registers all MCP providers in the DI container and returns
a configured MCP manager.

Args:
    container: Optional DI container (uses global if None)
    with_monitoring: Whether to register monitoring provider
    with_default_schemes: Whether to register default resource schemes (config://, memory://)
    with_extended_schemes: Whether to register extended schemes (env://, file://, http://, logs://, metrics://)

Returns:
    Configured MCP manager

Example:
    >>> manager = setup_mcp()
    >>> session = await manager.connect(server)
    >>> result = await manager.execute_tool("search", {"query": "hello"})

#### setup_mcp_with_config

Setup MCP with configuration data.

Registers adapters and pre-loads configuration into config:// scheme.

Args:
    config: Configuration dictionary

Returns:
    Configured MCP manager

Example:
    >>> config = {
    ...     "app": {"name": "myapp", "debug": True},
    ...     "database": {"host": "localhost", "port": 5432}
    ... }
    >>> manager = setup_mcp_with_config(config)
    >>> db_config = await manager.get_resource("config://database")

#### register_custom_scheme

Register a custom resource scheme handler.

Args:
    scheme: Scheme name (e.g., "db", "storage")
    handler: Scheme handler implementation
    container: Optional DI container (uses global if None)

Example:
    >>> class DbSchemeHandler:
    ...     async def get_resource(self, uri: str):
    ...         # Fetch from database
    ...         pass
    >>>
    >>> register_custom_scheme("db", DbSchemeHandler())

#### get_mcp_manager

Get the global MCP manager.

Returns:
    Global MCP manager instance

Example:
    >>> manager = get_mcp_manager()
    >>> result = await manager.execute_tool("search", {"query": "hello"})

#### set_mcp_manager

Set the global MCP manager.

Args:
    manager: MCP manager instance

Example:
    >>> custom_manager = McpManager(custom_container)
    >>> set_mcp_manager(custom_manager)

#### _get_provider

Get MCP provider from container.

#### _get_resource_provider

Get resource provider from container.

#### _get_tool_registry

Get tool registry from container.

#### _get_session_manager

Get session manager from container.

#### _get_monitoring_provider

Get monitoring provider from container (optional).

#### register_resource_scheme

Register a resource scheme handler.

Args:
    scheme: Scheme name (e.g., "db", "storage")
    handler: Scheme handler implementation

Example:
    >>> manager.register_resource_scheme("db", DbSchemeHandler())

#### make_app

Create a Typer app with standard global options.

Automatically adds common CLI options:
- --verbose/-v: Verbose output
- --debug: Debug mode
- --workspace/-w: Workspace path
- --config/-c: Config file path

These options are available in ctx.obj for all subcommands.

Args:
    name: Application name
    help: Help text for the application

Returns:
    Configured Typer application

Example:
    from pheno.cli.typer import make_app

    app = make_app("myapp", "My CLI application")

    @app.command()
    def hello(ctx: typer.Context):
        if ctx.obj["verbose"]:
            print("Verbose mode enabled")
        print("Hello!")

    if __name__ == "__main__":
        app()

#### create_command_group

Create a Typer command group.

Args:
    name: Group name
    help: Help text for the group

Returns:
    Typer instance for the command group

Example:
    from pheno.cli.typer import make_app, create_command_group

    app = make_app("myapp")
    db_group = create_command_group("db", "Database commands")

    @db_group.command()
    def migrate():
        print("Running migrations...")

    app.add_typer(db_group, name="db")

#### _root

Root callback to set up context.

#### register_command

Register a command handler.

Args:
    name: Command name
    description: Command description
    handler: Function to handle the command
    parser_config: Optional function to configure the argument parser
    help_text: Optional help text for the command

#### get_command

Get command by name or alias.

#### get_commands_for_project

Get all commands available for a project type.

#### get_commands_by_category

Get all commands in a category.

#### list_commands

List all available commands.

Returns:
    List of command names

#### search_commands

Search commands by name or description.

#### create_cli

Create Argparse CLI instance.

#### add_command

Add command to CLI.

#### run_cli

Run Argparse CLI with arguments.

#### _detect_project_type

Detect project type from path.

#### _load_commands

Load available commands.

#### _register_core_commands

Register core commands available everywhere.

#### _register_pheno_commands

Register Pheno-SDK specific commands.

#### _register_zen_commands

Register Zen-MCP-Server specific commands.

#### _register_atoms_commands

Register Atoms-MCP-Old specific commands.

#### _register_cicd_commands

Register CI/CD commands.

#### _register_quality_commands

Register quality commands.

#### _register_atlas_commands

Register Atlas commands.

#### get_available_commands

Get list of available commands.

#### help_handler



#### build_handler



#### test_handler



#### start_handler



#### stop_handler



#### check_handler



#### pattern_detection_handler



#### create_pheno_cli

Create and run Pheno CLI.

#### create_project_cli

Create and run project-specific CLI.

#### create_simple_cli

Create and run simple CLI.

#### run

Run async monitoring loop.

#### _help_handler

Show help information.

#### _version_handler

Show version information.

#### _status_handler

Show project status.

#### _build_handler

Build the project.

#### _test_handler

Run tests.

#### _quality_handler

Run quality checks.

#### _zen_start_handler

Start Zen MCP server.

#### _zen_stop_handler

Stop Zen MCP server.

#### _atoms_check_handler

Run Atoms check.

#### _cicd_generate_handler

Generate CI/CD pipeline.

#### _cicd_sync_handler

Synchronize CI/CD configuration.

#### _cicd_update_handler

Update soft dependencies.

#### _cicd_status_handler

Show CI/CD status.

#### _cicd_validate_handler

Validate CI/CD configuration.

#### _cicd_manage_handler

Manage CI/CD across all projects.

#### _atlas_health_handler

Generate atlas health report.

#### _atlas_status_handler

Show atlas status.

#### _pattern_detection_handler

Run advanced pattern detection.

#### _architectural_validation_handler

Run architectural pattern validation.

#### create_cli_adapter

Create CLI adapter for specified framework.

#### get_available_frameworks

Get list of available CLI frameworks.

#### show_help

Show help information.

#### command_wrapper



#### init_otel

Initialize OTel tracing (and metrics provider via configure_otel) and optionally
instrument FastAPI.

#### add_prometheus_endpoint

Add a Prometheus metrics endpoint to an ASGI application.

Args:
    app: ASGI application instance.
    path: URL path hosting the metrics endpoint.

#### configure_structlog



#### get_logger

Get a logger instance for the given name.

#### configure_otel

Configure OpenTelemetry tracing and metrics providers.

Minimal wrapper that prefers OTLP exporters when available and can optionally export
to console for local development.

#### get_tracer_provider



#### get_meter_provider



#### local

Create local embedding provider using sentence-transformers.

#### s3

Create a storage client with S3 backend.

Args:
    aws_access_key_id: AWS access key (optional, uses env var)
    aws_secret_access_key: AWS secret key (optional, uses env var)
    region_name: AWS region (default: us-east-1)
    endpoint_url: Custom S3 endpoint for S3-compatible services
    default_bucket: Default bucket name

Returns:
    Storage instance

#### _get_bucket

Get bucket name, falling back to default.

#### get_public_url

Get public URL for a file.

Args:
    bucket: Storage bucket name
    path: File path within bucket

Returns:
    Public URL

#### sync_project

Synchronize CI/CD configuration between projects.

#### sync_all_projects

Synchronize source to multiple target projects.

#### update_soft_dependencies

Update soft dependencies for a project.

#### get_sync_status

Get synchronization status.

#### list_sync_history

List synchronization history.

#### _detect_conflicts

Detect conflicts between source and target.

#### _sync_overwrite

Overwrite target with source.

#### _sync_merge

Merge source and target configurations.

#### _sync_backup_and_overwrite

Backup target and overwrite with source.

#### _sync_manual_review

Prepare for manual review.

#### _update_dependencies

Update specific dependency types.

#### _update_workflows

Update GitHub Actions workflows.

#### _update_docker_files

Update Docker files.

#### _update_makefile

Update Makefile.

#### _update_config_files

Update configuration files.

#### _files_differ

Check if two files differ.

#### _dirs_differ

Check if two directories differ.

#### _has_local_modifications

Check if file has local modifications (simplified)

#### _create_diff_file

Create diff file for manual review.

#### _record_sync

Record synchronization in history.

#### _load_dependency_map

Load dependency mapping from configuration.

#### get_dependencies

Get tracked dependencies for a computation.

#### add_dependency

Add a dependency between two nodes.

#### remove_dependency

Remove a dependency between two nodes.

#### sync_dependencies

Sync dependencies for a project.

#### save_config

Save configuration to disk.

#### load_config

Load configuration from ``path`` and optionally override the profile.

#### save_pipeline

Save generated pipeline.

#### load_pipeline

Load generated pipeline.

#### list_projects

List all registered project names.

#### delete_config

Delete CI/CD configuration.

#### get_project_config

Get project configuration from dialog fields.

#### update_config

Update project configuration.

#### validate_config

Validate Vercel deployment configuration.

#### merge_configs

Merge two configurations.

#### sync_pipeline

Sync pipeline from source to target.

#### detect_changes

Detect changes between source and target.

#### backup_pipeline

Backup current pipeline.

#### restore_pipeline

Restore pipeline from backup.

#### get_template

Get template by name.

#### list_templates



#### register_template

Register a widget template.

#### update_template

Update existing template.

#### delete_template

Delete template.

#### integrate_quality_checks

Integrate quality checks into pipeline.

#### get_quality_config

Get quality configuration for project type.

#### validate_quality_integration

Validate quality integration.

#### update_quality_thresholds

Update quality thresholds in pipeline.

#### send_notification

Send notification.

#### configure_notifications

Configure notifications for project.

#### get_notification_config

Get notification configuration.

#### store_artifact

Store artifact and return ID.

#### retrieve_artifact

Retrieve artifact by ID.

#### list_artifacts

List artifacts for project.

#### delete_artifact

Delete artifact.

#### deploy

Execute Vercel deployment.

#### rollback

Get inverted changes for rollback.

#### get_deployment_status

Get deployment status.

#### list_environments

List available environments.

#### add_file

Add a file to the pipeline.

#### get_file

Get file content.

#### list_files

List all files in the pipeline.

#### generate_pipeline

Generate a complete CI/CD pipeline.

#### generate_workflow

Generate a specific workflow file.

#### generate_dockerfile

Generate Dockerfile for specified platform.

Args:
    platform: Target platform (auto = detect from project)

Returns:
    Dockerfile content

#### generate_docker_compose

Generate docker-compose.yml.

#### generate_makefile

Generate Makefile.

#### generate_all

Generate CI/CD for all projects.

#### _should_generate_stage

Determine if a stage should be generated.

#### get_generated_pipelines

Get all generated pipelines.

#### clear_generated_pipelines

Clear generated pipelines.

#### get_source

Get template source.

#### render_template

Quick template rendering function.

Example:
    render_template("Hello, {name}!", {"name": "World"})
    # "Hello, World!"

Args:
    template: Template string
    variables: Template variables

Returns:
    Rendered string

#### render_string

Render a template string with context.

#### validate_template

Validate template with context.

#### get_template_variables

Get variables used in template.

#### _yaml_dump

YAML dump filter.

#### _json_dump

JSON dump filter.

#### _join_lines

Join lines filter.

#### _indent

Indent text filter.

#### _load_default_templates

Load default templates.

#### get_engine

Get template engine by name.

#### from_string

Create LogLevel from string.

#### _load_templates

Load all available templates.

#### _generate_github_workflows

Generate GitHub Actions workflows.

#### _generate_pheno_sdk_workflows

Generate Pheno-SDK specific workflows.

#### _generate_zen_mcp_workflows

Generate Zen-MCP-Server specific workflows.

#### _generate_atoms_mcp_workflows

Generate Atoms-MCP-Old specific workflows.

#### _generate_docker_files

Generate Docker files.

#### _generate_makefile

Generate Makefile.

#### _generate_config_files

Generate configuration files.

#### _create_template_context

Create template context.

#### create_generator

Create a CI/CD generator for a project type.

#### create_generator_from_config

Create a CI/CD generator from configuration.

#### sync

Synchronize CI/CD configuration.

#### status

Get status based on thresholds.

#### validate

Validate field value.

#### _load_config_from_file

Load configuration from file.

#### _load_quality_configs

Load quality configurations for each project type.

#### _add_quality_stage_to_workflow

Add quality stage to GitHub Actions workflow.

#### _add_quality_targets_to_makefile

Add quality targets to Makefile.

#### _create_quality_config_file

Create quality configuration file.

#### _update_thresholds_in_workflow

Update quality thresholds in workflow.

#### _load_project_registry

Load project registry from configuration.

#### sync_all

Synchronize CI/CD across all projects.

#### update_all_dependencies

Update soft dependencies for all projects.

#### validate_all

Validate CI/CD configuration for all projects.

#### status_all

Get status for all projects.

#### add_project

Add a new project to the registry.

#### remove_project

Remove a project from the registry.

#### update_project_config

Update project configuration.

#### _save_project_registry

Save project registry to file.

#### run_quality_checks

Run quality checks for projects.

#### _load_default_configs

Load default configurations for each project type.

#### configure_logging

Configure logging for the application.

Args:
    level: Logging level (default: INFO)
    format_string: Custom format string (default: standardized format)
    date_format: Custom date format (default: YYYY-MM-DD HH:MM:SS)
    log_file: Optional file to log to
    quiet_libraries: Suppress noisy third-party library logs

#### parse_env_file

Parse environment file and yield key-value pairs.

#### load_env_files

Load environment variables from configured .env files.

#### temporary_env

Temporarily set environment variables within the context.

#### get_env_var

Return environment variable value with optional default and validation.

#### configure



#### record



#### remaining



#### _ensure_usage



#### _reset_if_needed



#### _check_alert_threshold



#### _next_day



#### _next_month



#### capacity



#### refill_rate



#### refill



#### consume



#### refund



#### wait_time



#### _normalize_key



#### configure_rule



#### get_retry_after



#### get_remaining



#### configure_defaults



#### _ensure_bucket



#### create_factory

Create a factory for a model dynamically.

Args:
    model: Model class to create factory for
    **field_overrides: Field value overrides

Returns:
    Factory class

Example:
    from dataclasses import dataclass

    @dataclass
    class User:
        id: int
        name: str

    UserFactory = create_factory(User, name=lambda: "Test User")
    user = UserFactory.build()

#### factory_faker

Provide Faker instance for tests.

Example:
    def test_with_faker(factory_faker):
        email = factory_faker.email()
        name = factory_faker.name()

#### random_email



#### random_name



#### random_username

Generate random username.

#### random_password

Generate random password.

#### random_url

Generate random URL.

#### random_uuid

Generate random UUID.

#### random_phone

Generate random phone number.

#### random_address

Generate random address.

#### random_company

Generate random company name.

#### random_text

Generate random text.

Args:
    max_chars: Maximum number of characters

#### random_sentence

Generate random sentence.

#### random_paragraph

Generate random paragraph.

#### build

Build the configuration entity.

Returns:
    Created configuration entity

Raises:
    ValueError: If required fields are missing

#### batch



#### wait_for

Wait for a condition to become true (sync version).

Args:
    condition: Function that returns True when condition is met
    timeout: Maximum time to wait in seconds
    interval: Time between checks in seconds
    message: Error message if timeout occurs

Example:
    def test_file_creation():
        create_file("test.txt")

        wait_for(
            lambda: os.path.exists("test.txt"),
            timeout=5.0,
            message="File not created"
        )

#### capture_logs

Capture log messages for testing.

Args:
    logger_name: Name of logger to capture (None for root logger)
    level: Minimum log level to capture

Yields:
    StringIO object containing captured logs

Example:
    def test_logging():
        with capture_logs("myapp") as log_output:
            logger = logging.getLogger("myapp")
            logger.info("Test message")

            assert "Test message" in log_output.getvalue()

#### temp_env

Temporarily set environment variables.

Args:
    **kwargs: Environment variables to set

Example:
    def test_with_env():
        with temp_env(DATABASE_URL="sqlite:///:memory:", DEBUG="true"):
            # Environment variables set
            assert os.getenv("DATABASE_URL") == "sqlite:///:memory:"

        # Environment variables restored

#### assert_dict_contains

Assert that actual dict contains all keys/values from expected dict.

Args:
    actual: Actual dictionary
    expected: Expected dictionary (subset)
    path: Current path (for error messages)

Example:
    def test_response():
        response = {"user": {"id": 1, "name": "Test", "extra": "data"}}

        assert_dict_contains(
            response,
            {"user": {"id": 1, "name": "Test"}}
        )

#### assert_list_contains

Assert that actual list contains all items from expected list.

Args:
    actual: Actual list
    expected: Expected items (subset)

Example:
    def test_list():
        actual = [1, 2, 3, 4, 5]
        assert_list_contains(actual, [2, 4])

#### retry_on_exception

Simple retry decorator for specific exceptions.

#### decorator



#### wrapper



#### skip_if_not_installed

Skip test if package is not installed.

Args:
    package_name: Name of the package to check

Example:
    @skip_if_not_installed("redis")
    def test_redis_cache():
        # Test that requires redis
        pass

#### requires_python

Require specific Python version.

Args:
    version: Minimum Python version (e.g., "3.10")

Example:
    @requires_python("3.10")
    def test_new_syntax():
        # Test using Python 3.10+ syntax
        pass

#### configure_in_memory_container

Configure container with in-memory implementations.

This is useful for testing and development.

Returns:
    Configured container with in-memory implementations

#### configure_production_container

Configure container with production implementations.

Args:
    user_repo: User repository implementation (defaults to in-memory)
    deployment_repo: Deployment repository implementation (defaults to in-memory)
    service_repo: Service repository implementation (defaults to in-memory)
    config_repo: Configuration repository implementation (defaults to in-memory)
    event_publisher: Event publisher implementation (defaults to in-memory)

Returns:
    Configured container with production implementations

#### get_container

Get the global DI container.

#### set_container

Set the global dependency container (useful for testing).

Args:
    container: Container instance to set as global

Example:
    >>> test_container = Container()
    >>> set_container(test_container)

#### reset_container

Reset the global container to a fresh instance.

#### register

Register a keyboard shortcut.

#### unregister

Unregister a shortcut.

#### has

Check if credential exists.

#### list



#### list_names

List all registered item names.

Returns:
    List of item names

Example:
    >>> names = registry.list_names()
    >>> # ["search", "analyze", "transform"]

#### count

Count events, optionally filtered by type.

#### search



#### filter

Add correlation ID to log record if available.

#### on_register

Register callback for item registration.

Args:
    callback: Function called when item is registered

Example:
    >>> registry.on_register(lambda name, item: logger.info(f"Registered {name}"))

#### on_unregister

Register callback for item unregistration.

Args:
    callback: Function called when item is unregistered

Example:
    >>> registry.on_unregister(lambda name: logger.info(f"Unregistered {name}"))

#### list_by_category

List items in a category.

Args:
    category: Category name

Returns:
    Items in category

Example:
    >>> data_tools = registry.list_by_category("data")

#### list_categories

List all tool categories.

#### get_category

Get all shortcuts in a category.

#### set_metadata

Set metadata for an item.

Args:
    name: Item name
    metadata: Metadata dictionary

Example:
    >>> registry.set_metadata("search", {"version": "1.0"})

#### get_metadata



#### update_metadata

Update metadata for an item.

Args:
    name: Item name
    updates: Metadata updates

Example:
    >>> registry.update_metadata("search", {"version": "1.1"})

#### _apply_filters

Apply filters to a Supabase query.

#### _item_matches_filters

Check if an item matches the given filters.

#### _get_item_name

Get the name of an item by finding it in the registry.

#### _metadata_matches_filters

Check if metadata matches all filter criteria.

#### get_instance

Get service instance based on lifecycle.

#### get_or_create

Get or create instance for this scope.

#### _create_auto_wiring_factory

Create a factory that auto-wires constructor dependencies.

#### register_singleton

Register a pre-created singleton instance.

Args:
    service_type: The type/interface
    instance: Pre-created instance

Example:
    >>> db = PostgresDatabase(connection_string)
    >>> container.register_singleton(IDatabase, db)

#### resolve

Resolve styles for an element using cascade.

Args:
    element: Element name/selector
    **context: Additional context (id, classes, etc.)

Returns:
    dict: Resolved style properties

#### has_service

Check if a service is registered.

Args:
    service_type: The type/interface to check
    name: Optional name

Returns:
    True if service is registered

#### list_services

Return a mapping of service status, optionally filtered by prefix.

#### create_scope

Create a new scope with fresh instances.

#### set_scope

Set the current scope for scoped service resolution.

#### factory



#### __call__

Handle a dispatched event.

#### adapt

Adapt external interface to port.

#### execute

Execute shortcut action.

#### process

Process domain logic.

#### handle

Handle webhook event.

#### register_instance

Register a service instance.

#### get_by_name

Get service by name.

#### get_by_tag

Get services by tag.

#### _create_instance

Create service instance.

#### _get_dependencies

Get dependencies from list widget.

#### is_registered

Check if service is registered.

#### _auto_wire_dependencies

Auto-wire dependencies for a service.

#### _validate_service

Validate service and its dependencies.

#### _check_circular_dependencies

Check for circular dependencies.

#### get_by_port

Get adapters by port name.

#### connect

Connect a port to an adapter.

#### disconnect

Disconnect a port from its adapter.

#### get_adapter_for_port

Get adapter connected to a port.

#### call_port

Call port through adapter.

#### get_port



#### get_adapters_for_port

Get all adapters for a port.

#### add_checker

Add health checker.

#### remove_checker

Remove health checker.

#### set_timeout

Set timeout for specific operation.

#### get_timeout

Get timeout for operation.

#### execute_with_timeout_sync

Execute sync function with timeout.

#### timeout_context_sync

Synchronous context manager for timeout.

#### _setup_default_patterns

Setup default error patterns.

#### _setup_default_mappings

Setup default exception type mappings.

#### add_pattern

Add a pattern for error categorization.

#### add_exception_mapping

Add exception type to category mapping.

#### add_custom_categorizer

Add custom categorizer function.

#### categorize

Categorize an exception.

#### get_retryable_categories

Get categories that are typically retryable.

#### is_retryable

Check if an error is retryable.

#### set_handler

Set handler for specific error category.

#### set_default_handler

Set default error handler.

#### set_error_tracker

Set error tracker.

#### handle_error

Handle errors from async worker.

#### _determine_severity

Determine error severity.

#### _extract_tags

Extract tags from exception.

#### _default_error_response

Default error response when no handler is available.

#### track_error

Track an error.

#### get_error_count

Get total error count.

#### get_errors_by_category

Get errors by category.

#### get_errors_by_severity

Get errors by severity.

#### get_recent_errors

Get recent errors.

#### get_error_rate



#### get_top_error_categories

Get top error categories by count.

#### get_top_error_patterns

Get top error patterns by count.

#### get_error_distribution_by_hour

Get error distribution by hour of day.

#### clear_errors

Clear all tracked errors.

#### analyze_errors

Analyze errors and return metrics.

#### detect_error_spikes

Detect error spikes in the data.

#### _get_top_categories_for_errors

Get top categories for a list of errors.

#### with_retry

Decorator to add retry logic with exponential backoff.

#### calculate_delay

Calculate delay for given attempt number.

#### should_retry

Determine if an error should be retried.

#### apply_jitter

Apply jitter to the delay.

#### _execute_call

Execute a call through the circuit breaker.

#### _fibonacci

Calculate Fibonacci number.

#### add_strategy

Add a retry strategy.

#### get_strategy

Get a retry strategy by name.

#### set_default_strategy

Set the default retry strategy.

#### execute_with_strategy

Execute function with specific strategy.

#### list_strategies

List all strategy names.

#### sync_wrapper



#### active_calls

Get number of active calls.

#### available_calls

Get number of available calls.

#### acquire_resource_sync

Synchronous context manager for acquiring bulkhead resources.

#### create_bulkhead

Create a new bulkhead.

#### get_bulkhead

Get bulkhead by name.

#### remove_bulkhead

Remove bulkhead.

#### list_bulkheads

List all bulkhead names.

#### get_all_stats

Get statistics for all pools.

#### state

Get current state.

#### failure_count

Get current failure count.

#### success_count

Get current success count.

#### is_open

Check if circuit breaker is open.

#### is_closed

Check if circuit is closed.

#### is_half_open

Check if circuit is half-open.

#### call

Execute function with circuit breaker protection.

#### _should_attempt_reset

Check if we should attempt to reset the circuit.

#### _record_success

Record a successful call.

#### _record_failure

Record a failed call.

#### _should_open_circuit

Check if circuit should be opened.

#### _transition_to_open

Transition to open state.

#### _transition_to_half_open

Transition to half-open state.

#### _transition_to_closed

Transition to closed state.

#### _notify_state_change

Notify about state change.

#### create_circuit

Create a new circuit breaker.

#### get_circuit

Get a circuit breaker by name.

#### remove_circuit

Remove a circuit breaker.

#### list_circuits

List all circuit breaker names.

#### register_handler

Register a handler for a specific event type.

#### categorize_error

Automatically categorize an error based on type and message.

Args:
    exception: The exception to categorize
    context: Optional error context

Returns:
    ErrorCategory enum value

#### determine_severity

Determine error severity based on exception and category.

Args:
    exception: The exception
    category: Error category

Returns:
    ErrorSeverity enum value

#### create_error_info

Create detailed error information.

Args:
    exception: The exception
    context: Optional error context

Returns:
    ErrorInfo object with categorization and severity

#### reset_metrics



#### add_fallback

Add fallback strategy for operation.

#### set_default_fallback

Set default fallback strategy.

#### get_project_root

Find the project root from git repository.

#### get_changed_files

Get list of files changed since remote branch.

Returns:
    List of changed file paths

#### requirements_changed

Check if requirements.txt was changed.

Args:
    changed_files: List of changed files (default: auto-detect)

Returns:
    True if requirements.txt changed

#### stage_vendored_files

Stage vendored files and requirements-prod.txt.

Args:
    project_root: Project root directory

Returns:
    True if staging succeeded

#### pre_push_check

Pre-push hook check for vendoring.

This function checks if requirements.txt changed and ensures vendoring
is up-to-date before allowing the push.

Args:
    quiet: Suppress output messages
    auto_stage: Automatically stage vendored files if updated

Returns:
    Exit code (0 = success, non-zero = failure)

#### should_skip_vendor_check

Determine if vendor check should be skipped.

Returns:
    True if check should be skipped

#### check_vendor_on_startup

Check vendored packages before startup.

Args:
    project_root: Project root directory (default: auto-detect)
    quiet: Suppress output messages
    exit_on_failure: Exit process if vendoring fails (default: True)

Returns:
    True if vendoring is up-to-date or was fixed, False on failure

#### detect_all

Use all detection strategies.

#### get_supported_platforms

Get list of all supported platforms.

Returns:
    List of platform names

#### has_platform_config

Check if project has configuration for specific platform.

Args:
    platform: Platform name to check

Returns:
    True if configuration files exist

#### get_platform_files

Get existing configuration files for a platform.

Args:
    platform: Platform name

Returns:
    List of existing file paths

#### _detect_dependencies

Detect project dependencies from requirements.txt.

#### _detect_python_version

Detect Python version from pyproject.toml or runtime.txt.

#### _detect_entry_point

Detect main entry point for the application.

#### to_vercel_config

Generate Vercel deployment configuration.

Returns:
    Dict suitable for vercel.json

#### to_docker_config

Generate Dockerfile.

Returns:
    Dockerfile content as string

#### to_lambda_config

Generate AWS Lambda configuration.

Returns:
    Dict suitable for serverless.yml or SAM template

#### to_railway_config

Generate Railway deployment configuration.

Returns:
    Dict suitable for railway.json

#### generate_build_script

Generate build script for platform.

Args:
    platform: Target platform (vercel, docker, lambda, railway)

Returns:
    Shell script content

#### save_configs

Save all platform configurations to files.

Args:
    output_dir: Directory to save configs (default: project root)

Returns:
    List of created file paths

#### detect_from_requirements

Detect packages from requirements.txt.

#### detect_from_imports

Detect packages by scanning Python imports.

#### find_git_hooks_dir

Find the .git/hooks directory for a project.

Args:
    project_root: Project root directory (default: current directory)

Returns:
    Path to .git/hooks or None if not found

#### install_pre_push_hook

Install pre-push hook in a project.

Args:
    project_root: Project root directory (default: current directory)
    force: Overwrite existing hook (default: False)
    backup: Backup existing hook before overwriting (default: True)

Returns:
    True if hook was installed successfully

#### uninstall_pre_push_hook

Uninstall pre-push hook from a project.

Args:
    project_root: Project root directory (default: current directory)
    restore_backup: Restore backup if available (default: True)

Returns:
    True if hook was uninstalled successfully

#### verify_hook_installation

Verify that the pre-push hook is installed and working.

Args:
    project_root: Project root directory (default: current directory)

Returns:
    True if hook is installed and valid

#### from_yaml

Create a configuration instance from a YAML file.

#### create_ui

Interactive project creation.

#### format_time



#### print

Print to stdout.

#### rule

Print a rule.

#### spinner

Context manager for a spinner with timing.

Usage:
    with ui.spinner("Loading packages") as step:
        # Do work
        step['count'] = 15
    # Automatically shows: ✓ Loading packages [dim](0.5s)[/dim]

Args:
    description: Description of the step

Yields:
    Dict that can be updated with additional info

#### step_progress

Create a step with a progress bar.

Usage:
    with ui.step_progress("Vendoring packages", total=15, unit="packages") as step:
        for i in range(15):
            step.update(i + 1, f"package_{i}")

Args:
    description: Description of the step
    total: Total number of items
    unit: Unit name for items

Returns:
    StepProgressContext manager

#### success

Whether command completed successfully.

#### error



#### warning

Log warning message.

#### info



#### panel

Print a panel with content.

#### summary_panel

Print a summary panel at the end of operations.

Args:
    title: Panel title
    stats: Dictionary of statistics to display
    status: Overall status (success/failed)
    total_time: Total elapsed time

#### _print_rich_summary_panel

Print summary panel using Rich formatting.

#### _print_fallback_summary_panel

Print summary panel using fallback formatting.

#### _build_summary_lines

Build list of lines for summary panel.

#### _print_rich_panel

Print Rich-formatted panel with box drawing.

#### table

Print a table.

#### _to_env



#### deploy_vercel

One-call deploy to Vercel with optional health check.

Returns a DeploymentResult. On success, attaches simple health metadata if a URL is
available.

#### get_deployments

Get list of recent deployments.

#### check_freshness

Check vendor freshness (CLI-friendly interface).

Args:
    project_root: Project root directory (default: auto-detect)
    auto_vendor: Automatically vendor if stale
    force: Force re-vendor even if up-to-date
    quiet: Quiet mode - only return exit code

Returns:
    Exit code (0 = up-to-date, 1 = stale, 2 = error)

#### _find_project_root

Find the project root directory.

#### _log

Log message if not in quiet mode.

Args:
    message: Message to log
    level: Log level (info, warning, error, success)

#### check_vendor_exists

Check if vendor directory exists.

#### check_requirements_exist

Check if requirements files exist.

#### get_vendor_mtime

Get modification time of vendor directory.

#### get_requirements_mtime

Get modification time of requirements.txt.

#### is_vendoring_stale

Check if vendoring is stale.

Returns:
    Tuple of (is_stale, reason)

#### run_vendor_setup

Run pheno-vendor setup.

Args:
    force: Force re-vendor even if up-to-date

Returns:
    True if vendoring succeeded, False otherwise

#### check_and_report

Check vendoring status and optionally auto-vendor.

Args:
    auto_vendor: Automatically vendor if stale
    force: Force re-vendor even if up-to-date

Returns:
    Exit code (0 = up-to-date, 1 = stale, 2 = error)

#### _generate_vercel

Generate Vercel build configuration.

#### _generate_docker

Generate Dockerfile with vendored packages.

#### _generate_lambda

Generate AWS Lambda build script.

#### _generate_railway

Generate Railway build configuration.

#### _generate_heroku

Generate Heroku build script.

#### _generate_fly

Generate Fly.io Dockerfile.

#### _generate_cloudflare

Generate Cloudflare Workers build script.

#### _generate_generic

Generate generic build script.

#### _generate_docker_content

Generate Dockerfile content for platform.

#### create_build_script

Create a build script file for the platform.

Args:
    platform: Target platform
    output_path: Where to save the script (default: build_<platform>.sh)

Returns:
    Path to the created script file

#### validate_artifact

Validate a specific artifact.

Args:
    artifact_path: Path to the artifact file
    artifact_type: Type of artifact (script, config, dockerfile)

Returns:
    Validation results dictionary

#### _validate_script

Validate shell script content.

#### _validate_dockerfile

Validate Dockerfile content.

#### _load_configs

Load all available configuration files.

#### _load_config_file

Load a single configuration file.

#### has_config

Check if configuration file exists.

#### get_value

Get a value from config using dot notation (e.g., 'build.command').

#### _load_env_vars

Load environment variables from various sources.

#### get_required

Get required environment variable, raise if missing.

#### list_required_vars

Get list of required variables for a platform.

#### validate_platform_vars

Validate required environment variables for a platform.

#### export_vars

Export specified environment variables.

#### task

Decorator to define a workflow task.

#### record_success

Record a successful call.

#### record_failure

Record a failed call.

#### classify_error

Classify an error into a category.

#### create_context

Create error context.

#### get_circuit_breaker

Get or create a circuit breaker.

#### to_http_response

Convert to HTTP error response format.

#### backend

Create with backend URL.

#### subscribe

Subscribe to notifications.

Args:
    callback: Function to call on notification (signature: callback(old_val, new_val))
    priority: Priority level (higher values called first)
    weak: Use weak reference to prevent memory leaks

Returns:
    Subscription ID for later unsubscription

#### jetstream

Return a JetStream context from a connected NATS client.

#### log

Log a message at the specified level.

#### debug

Enable debug mode.

#### critical

Log critical message.

#### set_attribute

Attach a scalar attribute to the span.

Args:
    key: Attribute name.
    value: Attribute value accepted by tracing backends.

#### set_attributes

Attach multiple attributes to the span in a single call.

Args:
    attributes: Mapping of attribute names to values.

#### add_event

Add domain event.

#### record_exception

Record an exception, optionally annotating additional context.

Args:
    exception: Exception instance to record.
    attributes: Optional structured metadata describing the error.

#### end

Finalise the span, signalling completion to the tracing backend.

Returns:
    None.

#### start_span

Start a new span as a child of ``context`` if supplied.

Args:
    name: Human-readable span name.
    context: Optional parent span context.
    **attributes: Attributes applied to the span on creation.

Returns:
    Active span handle.

#### get_current_span

Retrieve the span currently bound to execution context, if any.

Returns:
    Active span or ``None`` when no span is bound.

#### get_tracer

Retrieve a tracer bound to the supplied instrumentation scope.

Args:
    name: Instrumentation library or subsystem name.
    version: Optional version string used for telemetry attribution.

Returns:
    Tracer implementation ready to create spans.

#### add

Add item to bloom filter.

Args:
    item: Item to add

#### increment

Increment a counter.

Args:
    name: Counter name
    amount: Amount to increment
    tags: Optional tags

#### create_counter

Create a counter metric instrument.

Args:
    name: Metric name.
    description: Human-readable description.
    unit: Metric unit (e.g., ``ms``).

Returns:
    Counter instrument instance.

#### create_histogram

Create a histogram metric instrument.

Args:
    name: Metric name.
    description: Human-readable description.
    unit: Metric unit.

Returns:
    Histogram instrument instance.

#### create_gauge

Create a gauge metric instrument.

Args:
    name: Metric name.
    description: Human-readable description.
    unit: Metric unit.

Returns:
    Gauge instrument instance.

#### get_meter

Retrieve a meter associated with a particular instrumentation scope.

Args:
    name: Instrumentation scope name.
    version: Optional version string.

Returns:
    Meter implementation ready to create metrics.

#### add_check

Add a health check.

Args:
    name: Check name
    check_function: Function to run for the check
    description: Check description
    timeout: Check timeout
    interval: Check interval (0 to disable periodic checks)
    enabled: Whether the check is enabled
    critical: Whether the check is critical

Returns:
    Check ID

#### remove_check

Remove a health check.

#### check_all

Run all health checks.

Returns:
    Dict with 'status' and 'checks' containing individual check results.

#### severity

Severity level associated with the alert (e.g., ``warning`` or ``critical``).

Returns:
    Severity string recognised by the alerting backend.

#### message

Message content describing the alert condition.

Returns:
    Rendered alert message.

#### send_alert

Dispatch an alert notification.

Args:
    _alert: Alert payload to send.

#### setup_logging

Set up logging for a Pheno SDK project.

Args:
    name: Logger name
    level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    use_structured: Whether to use structured logging if available
    service_name: Service name for structured logging
    environment: Environment name

Returns:
    Configured logger instance

#### setup_tracing

Configure tracing exporters and instrumentation.

Args:
    config: Tracing configuration dictionary.

#### setup_metrics

Configure metrics collection and exporters.

Args:
    config: Metrics configuration dictionary.

#### setup_health_checks

Register health checks based on configuration.

Args:
    config: Health check configuration dictionary.

#### to_sse_format



#### create

Create an endpoints panel.

Args:
    endpoints: List of endpoint dicts with keys: label, url, healthy

Returns:
    Rich Panel or None if Rich not available

#### is_connected

Check if session is connected.

#### domain_events

Return collected domain events.

#### clear_events

Clear the in-memory event history.

Useful at the start of a new command execution when historical events are no
longer relevant.

#### vertex

Create Vertex AI embedding provider.

#### openai

Create OpenAI embedding provider.

#### pgvector

Create pgvector backend.

#### faiss

Create FAISS backend.

#### lancedb

Create LanceDB backend.

#### create_vector_store

Create a vector store by backend name.

Currently supported: memory (default) - in-memory store for development/testing.
Additional providers can be implemented following the base VectorStore interface.

#### configure_logging_from_settings

Apply logging configuration based on integration settings.

#### _normalise_sinks



#### setup_logging_library

Register all handlers with the global registries.

#### is_port_available

Check if a port is available.

Args:
    port: Port number to check

Returns:
    True if port is available

#### find_free_port

Find a free port in range.

Args:
    start: Start of port range
    end: End of port range

Returns:
    Free port number or None if none available

#### get_process_on_port

Get process using a port.

Args:
    port: Port number

Returns:
    Process information or None

#### kill_process_on_port

Kill process using a port.

Args:
    port: Port number

Returns:
    True if killed successfully

#### add_http_check

Add HTTP health check.

Args:
    url: Health check URL
    timeout: Request timeout
    interval: Check interval

#### add_port_check

Add port health check.

Args:
    port: Port number
    interval: Check interval

#### add_custom_check

Add custom health check.

Args:
    check: Health check implementation

#### stop_monitoring

Stop monitoring a process and return final metrics.

Args:
    pid: Process ID to stop monitoring

Returns:
    Final ProcessMetrics object

#### stop



#### restart

Restart the process.

Implementation should:
1. Stop existing process
2. Reset state
3. Start new process

#### start_process

Start a new process.

Args:
    name: Process name
    command: Command to execute
    **kwargs: Additional process options

Returns:
    Process instance

#### stop_process

Stop a process.

Args:
    name: Process name

Returns:
    True if stopped

#### restart_process

Restart a process.

Args:
    name: Process name

Returns:
    True if restarted

#### stop_all

Stop all processes.

#### get_process

Get process information.

#### count_running

Count running processes.

Returns:
    Number of running processes

#### create_server

Create a gRPC server with interceptors.

Args:
    config: Server configuration
    interceptors: List of server interceptors
    container: Optional DI container for service dependencies

Returns:
    GrpcServer instance ready to register services

Example:
    >>> from grpc_kit import create_server, GrpcServerConfig
    >>> from grpc_kit.interceptors import ServerTelemetryInterceptor
    >>>
    >>> config = GrpcServerConfig(port=50051)
    >>> server = create_server(
    ...     config,
    ...     interceptors=[ServerTelemetryInterceptor()],
    ... )
    >>>
    >>> # Register your services
    >>> # add_YourServiceServicer_to_server(YourService(), server.server)
    >>>
    >>> await server.start()

#### create_worker

Create a worker process with auto-restart.

Args:
    name: Process name
    command: Command to execute
    auto_restart: Enable auto-restart on failure
    max_restarts: Maximum restart attempts
    **kwargs: Additional options

Returns:
    Process instance with auto-restart enabled

#### create_batch

Create multiple configurations from a list of dictionaries.

Args:
    configs_data: List of configuration data dictionaries

Returns:
    List of created configuration entities

#### from_config

Create factory from configuration dictionary.

Args:
    config: Configuration dictionary with 'repository_type' key

Returns:
    Configured repository factory

#### _integrate_service_infra

Integrate with ServiceInfra for port allocation and tunnels.

Args:
    processes: Process configurations
    infrastructure: ServiceInfraManager-like instance

Returns:
    Updated process configurations

#### run_health_monitoring



#### _handle_signal

Handle shutdown signals.

#### run_with_tui

Run monitor with rich TUI dashboard.

Uses rich library for interactive monitoring with live updates.

#### run_headless

Run monitor in headless mode (no TUI).

Suitable for production/background execution.

#### generate_dashboard

Generate enhanced dashboard with process, health, and metrics.

#### health_check



#### handle_failure

Handle process failure.

Implements auto-restart logic if enabled.

#### _ensure_directory



#### build_go_service

Construct a ``ServiceConfig`` for a Go binary or module.

#### _register_services



#### show_status

Print orchestrator status for the project.

#### build_nextjs_service

Construct a ``ServiceConfig`` for a Next.js application.

#### _generate_insights



#### _empty_complexity_metrics



#### _empty_dependency_info



#### _collect_files



#### _analyze_file



#### _calculate_maintainability

Calculate maintainability index (simplified version).

Based on Microsoft's maintainability index formula (simplified):
MI = max(0, (171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)) * 100 / 171)

Where:
- V = Halstead Volume (approximated)
- G = Cyclomatic Complexity
- LOC = Lines of Code

Simplified version for quick calculation.

#### _module_name



#### run_wily_report

Run wily build/report and return the captured stdout.

#### _scan_directories

Scan directory structure for analysis.

#### _identify_patterns



#### _has_layer_separation



#### _detect_design_patterns

Detect design patterns in the codebase.

#### run_import_linter

Run import-linter against the provided config file.

#### inspect_direct_imports

Return direct import targets for a module (via import-linter helper).

#### _build_graph



#### _build_graph_via_ast



#### _compute_graph_metrics



#### _record_edge



#### _find_cycles



#### _extract_imports

Extract all import statements from a file.

#### _is_external_package

Check if an import is an external package.

#### _resolve_dependencies

Resolve imports to actual file paths.

#### _find_circular_dependencies

Find circular dependencies in the dependency graph.

#### visit



#### dfs



#### validate_file

Validate a single file for architecture compliance.

#### validate_directory

Validate a directory for architecture compliance.

#### _should_validate_file

Check if a file should be validated.

#### _validate_layer_boundaries

Validate that layer boundaries are respected.

#### _validate_dependency_direction

Validate dependency direction follows architectural principles.

#### _validate_solid_principles

Validate SOLID principles.

#### _validate_hexagonal_architecture

Validate Hexagonal Architecture patterns.

#### _validate_clean_architecture

Validate Clean Architecture principles.

#### _validate_code_quality

Validate general code quality metrics.

#### _determine_file_layer

Determine the architectural layer of a file.

#### _determine_module_layer

Determine the architectural layer of a module.

#### _violates_layer_boundary

Check if import violates layer boundary.

#### _is_domain_class

Check if class belongs to domain layer.

#### _is_domain_layer

Check if class belongs to domain layer.

#### _imports_from_infrastructure

Check if class imports from infrastructure layer.

#### _count_responsibilities

Count the number of responsibilities in a class.

#### _violates_open_closed_principle

Check if class violates Open/Closed principle.

#### _has_long_conditional_chain

Check if function has long conditional chains.

#### _implements_interface

Check if class implements an interface.

#### _is_proper_port_definition

Check if class is a proper port definition.

#### _has_domain_identity

Check if domain entity has identity.

#### _calculate_cyclomatic_complexity

Calculate cyclomatic complexity of a function.

#### _get_imported_module

Get the imported module name.

#### _initialize_builtin_patterns

Initialize built-in architectural patterns.

#### _detect_architectural_patterns

Detect architectural patterns based on directory structure.

#### _analyze_file_for_patterns

Analyze a single file for design patterns.

#### _analyze_layer_structure

Analyze the layer structure of the codebase.

#### _build_dependency_graph

Build dependency graph from imports.

#### _detect_cycles

Detect cycles in the dependency graph.

#### _calculate_complexity_score

Calculate complexity score for the dependency graph.

#### _calculate_metrics

Calculate aggregated metrics.

#### _generate_pattern_matches

Generate detailed pattern matches.

#### _file_matches_pattern

Check if a file matches a specific architectural pattern.

#### _count_files_and_lines

Count analyzed files and total lines of code.

#### _should_analyze_file

Check if file should be analyzed.

#### register_pattern

Register a custom architectural pattern.

#### register_design_pattern

Register a design pattern.

#### add_custom_detector

Add a custom pattern detector.

#### _detect_singleton

Detect singleton pattern.

#### _detect_factory

Detect factory pattern.

#### _detect_observer

Detect observer pattern.

#### _detect_strategy

Detect strategy pattern.

#### _detect_adapter

Detect adapter pattern.

#### _detect_decorator

Detect decorator pattern.

#### _detect_repository

Detect repository pattern.

#### _detect_service

Detect service pattern.

#### _detect_controller

Detect controller pattern.

#### _detect_middleware

Detect middleware pattern.

#### register_detector

Register a pattern detector.

#### register_architectural_pattern

Register an architectural pattern.

#### get_detector

Get a pattern detector by name.

#### get_architectural_pattern

Get an architectural pattern by name.

#### get_design_pattern

Get a design pattern by name.

#### list_detectors

List all registered detector names.

#### list_architectural_patterns

List all registered architectural pattern names.

#### list_design_patterns

List all registered design pattern names.

#### detect_patterns

Detect DDD patterns.

#### create_anti_pattern_detector

Create a detector for common anti-patterns.

#### create_security_pattern_detector

Create a detector for security-related patterns.

#### get_version

Get the current version of pheno-cli.

#### get_patterns



#### get_design_patterns



#### _detect_api_gateway

Detect API Gateway pattern.

#### _detect_circuit_breaker

Detect Circuit Breaker pattern.

#### _detect_event_sourcing

Detect Event Sourcing pattern.

#### _detect_aggregate

Detect Aggregate pattern.

#### _detect_value_object

Detect Value Object pattern.

#### register_extension

Register a pattern extension.

#### register_custom_detector

Register a custom pattern detector.

#### get_extension

Get an extension by name.

#### get_custom_detector

Get a custom detector by name.

#### list_extensions

List all registered extension names.

#### list_custom_detectors

List all registered custom detector names.

#### get_all_patterns

Get all architectural patterns from all extensions.

#### get_all_design_patterns

Get all design patterns from all extensions.

#### detect_all_patterns

Run all extensions and custom detectors on a file.

#### detect_god_object



#### detect_feature_envy



#### detect_sql_injection



#### detect_hardcoded_secrets



#### _ensure_bytes



#### _convert_node



#### _query_nodes



#### _walk_tree



#### _slice_source



#### get_parser_for_file

Get appropriate parser for file type.

Args:
    file_path: Path to file

Returns:
    Parser instance or None if unsupported

#### parse_file

Extract code entities from JS/TS file.

Args:
    file_path: Path to JavaScript/TypeScript file

Returns:
    List of extracted code entities

#### _is_top_level

Check if a function is top-level (not inside a class).

#### _extract_function

Extract function entity.

#### _extract_class

Extract class entity.

#### _extract_method

Extract method entity.

#### _get_signature

Get function signature from source.

#### _get_base_names

Get base class names.

#### _extract_with_tree_sitter



#### _extract_functions

Extract function declarations.

#### _extract_classes

Extract class declarations.

#### _extract_arrow_functions

Extract arrow function assignments.

#### _extract_jsdoc

Extract JSDoc comment before position.

#### add_security_filter

Add a security filter to a logger.

Args:
    logger: Logger to add filter to
    redact_emails: Whether to redact email addresses
    redact_ips: Whether to redact IP addresses

Returns:
    The security filter instance

Example:
    import logging
    from pheno_logging.filters import add_security_filter

    logger = logging.getLogger("app")
    add_security_filter(logger, redact_emails=True)

#### redact_dict

Redact sensitive information from a dictionary.

Args:
    data: Dictionary to redact

Returns:
    Redacted dictionary (new copy)

#### __getattr__



#### bind

Bind context to this logger.

#### set_level

Set the logging level.

#### add_handler

Add an event handler.

#### remove_handler

Remove an event handler.

#### is_enabled_for

Check if logging is enabled for the given level.

#### emit

Emit an event synchronously.

#### flush



#### close

Close the connection pool.

#### should_emit

Check if the record should be emitted.

#### format



#### format_exception



#### is_healthy



#### observe

Record a histogram observation.

Args:
    name: Histogram name
    value: Observed value
    tags: Optional tags

#### check_health



#### __str__



#### merge

Merge with another context.

#### shutdown_logging

Shutdown all loggers and handlers.

#### _create_record

Create a log record.

#### configure_morph_logging

Configure Python logging according to Morph integration settings.

Returns the configured root Morph logger for convenience.

#### get_morph_logger

Return a namespaced Morph logger (config must be applied separately).

#### morph_log_context

Context manager that yields a logging adapter attaching Morph-specific fields.

#### get_pheno_structured_logger

Convenience helper to access pheno's core structured logger with Morph namespace.

#### configure_structlog_for_pheno

Configure structlog with environment-appropriate settings for pheno-logging.

This function sets up structlog with sensible defaults for different
environments (dev, staging, prod) and integrates with pheno-logging's
context management.

Args:
    service_name: Name of the service (added to all log entries)
    environment: Environment name (dev, staging, prod)
    log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    json_logs: Use JSON format (auto-detected based on environment if None)
    add_correlation_id: Add correlation_id and request_id from context
    add_callsite: Add callsite information (file, line, function)

Example:
    configure_structlog_for_pheno(
        service_name="my-api",
        environment="prod",
        log_level="INFO",
        json_logs=True
    )

    logger = get_structlog_logger("my_module")
    logger.info("Server started", port=8000)

#### get_structlog_logger

Get a structlog logger.

This is a convenience function that returns a structlog logger directly.
For pheno-logging interface compatibility, use StructlogAdapter instead.

Args:
    name: Logger name (optional)

Returns:
    Structlog logger instance

Example:
    logger = get_structlog_logger("my_module")
    logger.info("Processing request", request_id="abc123")

#### _add_context

Add correlation IDs and service context to log entries.

#### _format_record

Format a log record for syslog.

#### create_handler

Create a handler instance.

Args:
    name: Handler name
    config: Handler configuration

Returns:
    Handler instance

Raises:
    ConfigurationError: If handler not found or creation fails

#### get_handler_class

Get a handler class by name.

Args:
    name: Handler name

Returns:
    Handler class or None if not found

#### get_or_create_handler

Get existing handler instance or create new one.

Args:
    name: Handler name
    config: Handler configuration

Returns:
    Handler instance

#### list_handlers

List all registered handler names.

Returns:
    List of handler names

#### unregister_handler

Remove a handler previously registered.

#### _open_file

Open the log file.

#### _rotate_file

Rotate the log file.

#### _connect

Connect to syslog server.

#### _record_to_dict

Convert log record to dictionary.

#### create_embedding_provider

Factory to create embedding providers by name.

Supported providers:
    - ``openai``: Uses OpenAI embeddings (default).
    - ``openrouter``: OpenAI-compatible API hosted by OpenRouter.
    - ``sentence_transformers``: Local sentence-transformers models.
    - ``inmemory``: Deterministic random vectors (testing).

#### build_embedding_service

Build an ``EmbeddingService`` instance using factory configuration.

#### _split_text

Split text into chunks.

#### _cache_key



#### dimension

Return the dimension of the embedding vectors.

#### _ensure_vertexai_loaded

Import vertexai lazily to avoid import-time crashes in constrained environments.

#### _load_persistent_cache

Load cache from disk if it exists.

#### _save_persistent_cache

Save cache to disk.

#### _manage_cache_size

Remove oldest entries if cache exceeds size limit.

#### clear_cache

Clear the style cache.

#### get_embedding_service

Get an embedding service instance.

If ``provider_type`` is omitted, auto-detect providers in preference order:
Vertex AI → sentence-transformers → litellm.

#### _create_vertex_service

Instantiate the Vertex AI embedding service.

#### _create_litellm_service

Instantiate a LiteLLM embedding provider, applying sensible defaults per provider.

#### _check_vertex_ai_available

Check if Vertex AI is available and properly configured.

#### _check_gcloud_auth



#### _extract_embeddings

Extract embeddings from litellm response payload.

Supports both dictionary-style responses and typed objects.

#### provider_name

Return the name of the provider.

#### _to_list



#### _ensure_collection



#### _ensure_vector



#### _cosine_similarity

Compute cosine similarity between two vectors.

#### _extract_content

Extract content text from record for embedding.

#### _get_table_name

Map entity type to table name.

#### get_processing_stats

Get current background processing statistics.

#### __repr__



#### _get_search_entities

Get the list of entity types to search.

#### _process_fts_results

Process FTS search results.

#### _build_ilike_query

Build ILIKE query with filters and search conditions.

#### _build_search_conditions

Build search conditions based on table type.

#### _process_ilike_results

Process ILIKE search results.

#### _handle_search_error

Handle search errors with logging.

#### _log_search_results

Log search results for debugging.

#### is_terminal

Check if deployment is in a terminal state.

#### can_transition_to

Check if transition to new status is valid.

#### is_production

Check if environment is production.

#### requires_approval

Check if environment requires approval.

#### supports_rollback

Check if strategy supports rollback.

#### requires_health_checks

Check if strategy requires health checks.

#### is_transitioning

Check if service is in a transition state.

#### is_http

Check if port uses HTTP protocol.

#### is_secure

Check if URL uses secure protocol.

#### to_dns_label

Convert to valid DNS label (replace underscores with hyphens).

#### to_env_var_prefix

Convert to environment variable prefix (uppercase, underscores).

#### domain

Set the domain for tunneling.

#### local_part

Get email local part.

#### __int__



#### is_privileged

Check if port is privileged (< 1024).

#### is_ephemeral

Check if port is ephemeral (>= 49152).

#### scheme

Get URL scheme.

#### host

Get URL host.

#### path

Get URL path.

#### parts

Get config key parts (split by dot).

#### namespace

Get config key namespace (first part).

#### as_string

Get value as string.

#### as_int

Get value as integer.

#### as_bool

Get value as boolean.

#### register_project

Register a project for multi-tenant management.

#### unregister_project

Unregister a project.

#### get_project

Get project configuration by name.

#### add_process

Add a process to monitoring.

#### remove_process

Remove a process from monitoring.

#### remove_resource

Remove a resource from a project.

#### update_value

Update configuration value.

Args:
    new_value: New configuration value

Returns:
    Updated configuration entity

#### update_description

Update configuration description.

Args:
    new_description: New description

Returns:
    Updated configuration entity

Raises:
    ValidationError: If description is empty

#### has_changed

Check if configuration has been updated.

#### get_namespace

Get configuration namespace from key.

#### uptime_seconds

Get service uptime in seconds.

#### update_name

Update user name.

Args:
    new_name: New user name

Returns:
    Updated user entity

Raises:
    ValidationError: If name is empty
    UserInactiveError: If user is inactive

#### update_email

Update user email.

Args:
    new_email: New email address

Returns:
    Updated user entity

Raises:
    UserInactiveError: If user is inactive

#### deactivate



#### activate

Activate user.

Returns:
    Activated user entity

Raises:
    ValidationError: If user is already active

#### get_tool



#### has_tool

Check if a tool is registered.

#### get_tool_handler

Get the handler function for a tool.

#### search_tools

Search for tools by name or description.

#### get_session

Get a session by ID.

#### list_sessions

List sessions.

#### get_session_metadata

Get metadata for a session.

#### set_session_metadata

Set metadata for a session.

#### get_session_count

Get count of sessions.

#### supports_scheme

Check if scheme is supported.

#### register_scheme

Register a scheme handler.

#### unregister_scheme

Unregister a scheme handler.

#### get_scheme_handler

Get the handler for a scheme.

#### list_schemes

List all registered schemes.

#### register_default_adapters

Register default infrastructure adapters (idempotent).

#### on

Register event handler decorator.

#### unsubscribe

Unsubscribe from notifications.

Args:
    callback_or_id: Either the callback function or subscription ID

#### _matches_pattern

Simple pattern matching with * wildcard support.

#### get_handlers

Return a copy of handlers for the provided event.

#### publish

Publish event to all subscribers synchronously.

Args:
    event_name: Event name
    data: Event data
    source: Event source identifier
    correlation_id: Correlation ID for tracing

Returns:
    Published event

#### _load_from_disk

Load events from disk.

#### _get_stream_file

Get file path for aggregate stream.

#### next_retry_time

Calculate next retry time using exponential backoff.

#### on_success

Register success callback.

#### on_failure

Register failure callback.

#### get_delivery

Get delivery record by ID.

#### sign

Generate HMAC signature for payload.

#### to_domain_params

Convert to domain entity creation parameters.

#### get_config_key

Get the config key as a domain value object.

#### get_config_value

Get the config value as a domain value object.

#### from_entity

Create DTO from domain entity.

#### get_service_id

Get the service ID as a domain value object.

#### _value



#### get_user_id



#### get_email

Get the email as a domain value object.

#### get_deployment_id

Get the deployment ID as a domain value object.

#### get_subscriber_count

Get number of subscribers for an event type.

Args:
    event_type: Type of event

Returns:
    Number of subscribers

#### get_help

Get help text for a command.

Args:
    command: Command name (optional, returns general help if None)

Returns:
    Help text

#### get_openapi_spec

Get OpenAPI specification.

Returns:
    OpenAPI spec dictionary

#### list_resources

List available resources.

Returns:
    List of resource metadata

#### list_prompts

List available prompts.

Returns:
    List of prompt metadata

#### register_webhook

Register a webhook.

Args:
    source: Event source
    event_type: Event type to subscribe to
    url: Webhook URL
    secret: Webhook secret for verification (optional)

Returns:
    Webhook ID

Raises:
    WebhookRegistrationError: If registration fails

#### register_task

Register a scheduled task.

Args:
    task_name: Task name
    schedule: Cron schedule expression
    enabled: Whether task is enabled (default: True)

Returns:
    Task ID

Raises:
    TaskRegistrationError: If registration fails

#### list_tasks

List all scheduled tasks.

Returns:
    List of task metadata

#### get_task_status

Get task execution status.

Args:
    task_id: Task ID

Returns:
    Task status dictionary

Raises:
    TaskNotFoundError: If task doesn't exist

#### get_or_create_correlation_id

Get the current correlation ID or create a new one if none exists.

Returns:
    The current or newly created correlation ID

#### clear_correlation_id

Clear the correlation ID for the current context/thread.

#### setup_correlation_logging

Setup correlation ID logging for the root logger.

#### size

Get queue size.

#### hit_rate

Calculate cache hit rate.

Returns:
    Hit rate as percentage (0.0 to 1.0)

#### stats

Get cache statistics.

Returns:
    Dictionary with cache stats

#### __len__



#### __contains__



#### _hashes

Generate multiple hash values for item.

#### estimated_fp_rate

Estimate false positive rate.

Returns:
    Estimated false positive probability

#### append

Append item to buffer.

Args:
    item: Item to append

#### is_full

Check if buffer is full.

#### to_list

Convert parsed command back to list format.

#### __iter__



#### insert



#### starts_with

Check if any word starts with prefix.

Args:
    prefix: Prefix to search

Returns:
    True if prefix exists

#### find_all_with_prefix

Find all words with given prefix.

Args:
    prefix: Prefix to search

Returns:
    List of words with prefix

#### _find_node

Find node for given prefix.

#### _collect_words

Recursively collect all words from node.

#### _delete_helper



#### push

Add item to queue.

Args:
    item: Item to add
    priority: Priority (lower = higher priority)

#### pop

Remove and return highest priority item.

Returns:
    Highest priority item

Raises:
    IndexError: If queue is empty

#### peek

Get highest priority item without removing.

Returns:
    Highest priority item

Raises:
    IndexError: If queue is empty

#### __bool__

Check if queue is non-empty.

#### truncate

Truncate text to maximum length.

Example:
    truncate("Hello World", 8)  # "Hello..."
    truncate("Hello World", 8, word_boundary=True)  # "Hello..."

Args:
    text: Text to truncate
    max_length: Maximum length (including suffix)
    suffix: Suffix to append when truncated
    word_boundary: Truncate at word boundaries

Returns:
    Truncated text

#### wrap_text

Wrap text to specified width.

Example:
    wrap_text("Long text here", width=10)

Args:
    text: Text to wrap
    width: Maximum line width
    indent: Indent for first line
    subsequent_indent: Indent for subsequent lines

Returns:
    Wrapped text

#### pad_string

Pad string to specified length.

Example:
    pad_string("hello", 10, char='*', align='center')  # "**hello***"

Args:
    text: Text to pad
    length: Target length
    char: Padding character
    align: Alignment (left, right, center)

Returns:
    Padded string

#### remove_whitespace

Remove whitespace from text.

Args:
    text: Text to process
    keep: Whitespace characters to keep (e.g., ' ' to keep spaces)

Returns:
    Text with whitespace removed

#### indent_text

Indent all lines in text.

Args:
    text: Text to indent
    indent: Indent string

Returns:
    Indented text

#### slugify

Convert text to URL-friendly slug.

Example:
    slugify("Hello World!")  # "hello-world"
    slugify("C'est génial!")  # "cest-genial"

Args:
    text: Text to slugify
    separator: Character to use as separator
    lowercase: Convert to lowercase
    max_length: Maximum slug length (0 = no limit)
    word_boundary: Truncate at word boundaries

Returns:
    Slugified string

#### slugify_filename

Slugify filename while preserving extension.

Example:
    slugify_filename("My Document (2024).pdf")  # "my-document-2024.pdf"

Args:
    filename: Filename to slugify
    max_length: Maximum length

Returns:
    Slugified filename

#### camel_to_snake

Convert camelCase to snake_case.

Example:
    camel_to_snake("myVariableName")  # "my_variable_name"

#### snake_to_camel

Convert snake_case to camelCase.

Example:
    snake_to_camel("my_variable_name")  # "myVariableName"
    snake_to_camel("my_variable_name", True)  # "MyVariableName"

#### kebab_to_snake

Convert kebab-case to snake_case.

#### snake_to_kebab

Convert snake_case to kebab-case.

#### interpolate

Interpolate variables into string.

Example:
    interpolate("Value: {x}", x=10)  # "Value: 10"

Args:
    text: Text with placeholders
    **kwargs: Variables to interpolate

Returns:
    Interpolated string

#### sanitize_html

Sanitize HTML by escaping or removing tags.

Example:
    sanitize_html("<script>alert('xss')</script>")  # Escaped
    sanitize_html("<p>Hello</p>", {'p'})  # "<p>Hello</p>"

Args:
    text: Text to sanitize
    allowed_tags: Set of allowed HTML tags

Returns:
    Sanitized text

#### strip_tags

Remove all HTML tags from text.

Example:
    strip_tags("<p>Hello <b>World</b></p>")  # "Hello World"

Args:
    text: Text with HTML tags

Returns:
    Text without tags

#### sanitize_filename

Sanitize filename by removing/replacing invalid characters.

Example:
    sanitize_filename("file:name?.txt")  # "file_name_.txt"

Args:
    filename: Filename to sanitize
    replacement: Character to replace invalid chars with

Returns:
    Sanitized filename

#### remove_control_characters

Remove control characters from text.

Args:
    text: Text to clean

Returns:
    Text without control characters

#### normalize_whitespace

Normalize whitespace (convert multiple spaces to single).

Example:
    normalize_whitespace("Hello    World")  # "Hello World"

Args:
    text: Text to normalize

Returns:
    Normalized text

#### escape_for_regex

Escape special regex characters.

Args:
    text: Text to escape

Returns:
    Escaped text safe for regex

#### replace_tag



#### parse_datetime

Parse datetime from various formats.

Example:
    parse_datetime("2024-01-15 10:30:00")
    parse_datetime("2024-01-15T10:30:00Z")
    parse_datetime(1705318200)  # Unix timestamp

Args:
    value: Value to parse (string or timestamp)
    formats: List of datetime formats to try

Returns:
    Parsed datetime or None

#### parse_date

Parse date from string.

Example:
    parse_date("2024-01-15")
    parse_date("15/01/2024")

Args:
    value: Date string

Returns:
    Parsed date or None

#### parse_time

Parse time from string.

Example:
    parse_time("10:30:00")
    parse_time("10:30")

Args:
    value: Time string

Returns:
    Parsed time or None

#### parse_duration

Parse duration string to timedelta.

Example:
    parse_duration("1h 30m")  # 1 hour 30 minutes
    parse_duration("2d")  # 2 days
    parse_duration("45s")  # 45 seconds

Args:
    value: Duration string

Returns:
    Parsed timedelta or None

#### format_datetime

Format datetime for display.

#### format_relative

Format datetime as relative time.

Example:
    format_relative(datetime.now() - timedelta(minutes=5))  # "5 minutes ago"

#### humanize_duration

Convert seconds to human-readable duration.

Example:
    humanize_duration(3665)  # "1h 1m 5s"

#### now_utc

Get current UTC datetime.

#### to_utc

Convert datetime to UTC.

#### to_timezone

Convert datetime to specified timezone.

#### get_timezone

Get timezone for UTC offset.

Example:
    get_timezone(-5)  # UTC-5

#### extract_user_from_jwt

Extract user information from JWT token.

Args:
    token: JWT token string

Returns:
    Dictionary with user info (id, email, etc.)

Example:
    user = extract_user_from_jwt(token)
    print(user["email"])

#### is_token_expired

Check if JWT token is expired.

Args:
    token: JWT token string
    buffer_seconds: Consider expired if expires within this time

Returns:
    True if expired or expiring soon

Example:
    if is_token_expired(access_token):
        # Refresh token
        pass

#### remove_tokens

Remove tokens for a key.

Args:
    key: Storage key

#### save_to_file

Save credentials to JSON file.

WARNING: Credentials are stored in plaintext!
Only use for local development/testing.

Args:
    path: File path

#### remove

Remove a credential.

#### create_session

Create a new session.

Args:
    session_id: Session identifier
    tokens: OAuth tokens
    credentials: Optional credentials

#### get_credential

Get credential for session.

#### end_session

End a session and clean up.

#### clear_all

Clear all tasks.

#### quiet_library_loggers

Suppress logging from noisy libraries.

Args:
    libraries: List of library names to quiet
    level: Level to set (default: WARNING)

#### set_verbose_mode

Enable or disable verbose logging (DEBUG level).

Args:
    enabled: True to enable verbose mode, False to disable

#### create_file_handler

Create a file handler for logging.

Args:
    log_file: Path to log file
    level: Logging level for this handler
    format_string: Custom format (default: standardized format)

Returns:
    Configured FileHandler

#### add_file_logging

Add file logging to the root logger.

Args:
    log_file: Path to log file
    level: Logging level for file output

#### log_exception

Log an exception with consistent formatting.

Args:
    logger: Logger instance
    message: Error message
    exc_info: Include exception traceback (default: True)

#### get_env_config

Return a mapping of environment variables filtered by ``prefix``.

#### load_env_file

Parse a ``.env`` file and optionally apply the values to ``os.environ``.

#### load_yaml

Load structured configuration from YAML, relying on :class:`Config`.

#### save_yaml

Persist a mapping to disk as YAML.

#### to_yaml

Write the configuration to a YAML file.

#### apply

Load values and apply them to the current process environment.

#### format_text

Format metrics as plain text.

Returns:
    Formatted metrics string

#### format_json



#### log_metrics

Log metrics using logger.

#### decrement

Decrement a counter.

Args:
    name: Counter name
    amount: Amount to decrement
    tags: Optional tags

#### value

Get the current value.

#### statistics



#### set_gauge

Set a gauge value.

Args:
    name: Gauge name
    value: Gauge value
    tags: Optional tags

#### timer

Context manager for timing operations.

Args:
    name: Timer name
    tags: Optional tags

Example:
    with collector.timer("database_query"):
        result = db.query()

#### aggregate

Aggregate metrics for a name.

Args:
    name: Metric name

Returns:
    Aggregated statistics

#### _clean_old_metrics

Remove metrics outside time window.

#### add_streaming_routes

Add streaming routes to a FastAPI/Starlette application.

Args:
    app: FastAPI or Starlette application
    manager: StreamManager instance
    sse_path: Path for SSE endpoint
    websocket_path: Path for WebSocket endpoint

Example:
    from fastapi import FastAPI
    from pheno.events.streaming import StreamManager
    from pheno.events.streaming_helpers import add_streaming_routes

    app = FastAPI()
    manager = StreamManager()

    add_streaming_routes(app, manager)

    # Now you can broadcast:
    await manager.broadcast("updates", {"message": "Hello"})

#### should_bypass_auth

Check if a path should bypass authentication.

Args:
    path: Request path

Returns:
    True if path is a KInfra route that should bypass auth

Example:
    >>> should_bypass_auth('/kinfra')
    True
    >>> should_bypass_auth('/dashboard')
    False

#### get_nextjs_authkit_config

Get Next.js AuthKit middleware configuration with KInfra paths excluded.

Returns:
    Config dict ready for authkitMiddleware()

Example:
    >>> from pheno.dev.utils.middleware import get_nextjs_authkit_config
    >>> export default authkitMiddleware(get_nextjs_authkit_config())

#### get_nextjs_matcher_pattern

Get Next.js middleware matcher pattern excluding KInfra routes.

Returns:
    Regex pattern for Next.js config.matcher

Example:
    >>> export const config = { matcher: [get_nextjs_matcher_pattern()] }

#### get_express_middleware

Get Express.js middleware function that bypasses auth for KInfra routes.

Returns:
    Express middleware function

Example:
    >>> app.use(get_express_middleware())

#### get_django_exempt_urls

Get Django URL patterns to exempt from authentication.

Returns:
    List of regex patterns for Django

Example:
    >>> AUTHENTICATION_EXEMPT_URLS = get_django_exempt_urls()

#### print_integration_guide

Print integration guide for a specific framework.

Args:
    framework: 'nextjs', 'express', 'django', 'flask'

Example:
    >>> from pheno.dev.utils.middleware import print_integration_guide
    >>> print_integration_guide('nextjs')

#### kinfra_auth_bypass

Express middleware to bypass auth for KInfra routes.

#### _norm



#### _get_redis



#### _acquire_mem



#### _release_mem



#### acquire_wd_lock



#### release_wd_lock



#### acquire_repo_lock



#### release_repo_lock



#### exponential_backoff

Decorator for automatic retry with exponential backoff.

Example:
    @exponential_backoff(max_attempts=3, backoff_factor=2.0)
    def fetch_data():
        return requests.get(url)

#### with_retries

Simple retry helper function.

Example:
    result = with_retries(lambda: make_request(), max_attempts=3)

#### validate_bearer_token

Validate and extract bearer token from Authorization header.

Args:
    authorization: Authorization header value

Returns:
    Extracted token or None if invalid

#### validate_basic_auth

Validate and extract credentials from Basic Authorization header.

Args:
    authorization: Authorization header value

Returns:
    Tuple of (username, password) or None if invalid

#### has_scope

Check if scopes string contains required scopes.

Args:
    scopes_str: Space-separated scopes string
    required_scopes: Set of required scopes

Returns:
    True if all required scopes are present

#### has_any_scope

Check if scopes string contains any of the allowed scopes.

Args:
    scopes_str: Space-separated scopes string
    allowed_scopes: Set of allowed scopes

Returns:
    True if any allowed scope is present

#### get_headers

Get empty headers (auth is in query params).

#### get_params

Get query parameters.

#### create_client

Create a configured httpx.Client with sane defaults.

Args:
    base_url: Optional base URL
    headers: Default headers
    timeout: Overall timeout (seconds) if set, overrides individual components
    connect_timeout, read_timeout, write_timeout, pool_timeout: components
    event_hooks: Mapping with optional "request"/"response" hooks

#### create_async_client

Create a configured httpx.AsyncClient with sane defaults.

#### request_with_retries

Sync request with simple exponential backoff retries for idempotent calls.

Note: Prefer to keep retries small and idempotent-only (GET/HEAD).

#### normalize_headers

Normalize header names and values.

Args:
    headers: Dictionary of headers

Returns:
    Normalized headers with title-case names and string values

#### add_user_agent

Add User-Agent header with system information.

#### create_user_agent

Create comprehensive User-Agent string.

Args:
    app_name: Application name
    version: Application version

Returns:
    User-Agent string with system information

Example:
    'MyApp/1.0.0 (Python/3.11.0; Darwin/23.0.0)'

#### extract_bearer_token

Extract bearer token from Authorization header.

Args:
    authorization: Authorization header value

Returns:
    Extracted token or None if not found

#### extract_basic_auth

Extract username and password from Basic Authorization header.

Args:
    authorization: Authorization header value

Returns:
    Tuple of (username, password) or None if invalid

#### build_cache_control

Build Cache-Control header value.

Args:
    max_age: Maximum age in seconds
    no_cache: Disable caching
    no_store: Prevent storage
    public: Allow public caching
    private: Allow only private caching

Returns:
    Cache-Control header value

#### add_json_content_type

Add JSON content type header.

#### add_form_content_type

Add form content type header.

#### add_authorization

Add Authorization header.

#### add_api_key

Add API key header.

#### add_correlation_id

Add correlation ID for request tracing.

#### add_accept_json

Add Accept header for JSON responses.

#### build_httpx_otel_hooks

Return httpx event_hooks for sync Client.

#### build_async_httpx_otel_hooks

Return httpx event_hooks for AsyncClient.

#### on_request



#### on_response



#### _has_httpx



#### build_httpx_correlation_hooks

Return httpx event_hooks for sync Client that inject correlation header.

#### build_async_httpx_correlation_hooks

Return httpx event_hooks for AsyncClient that inject correlation header.

#### off

Remove event handler.

#### get_pending

Get all pending deliveries.

#### get_failed

Get all failed deliveries.

#### get_performance_monitor

Get the global performance monitor instance.

Returns:
    Shared PerformanceMonitor instance

#### get_system_metrics

Get current system performance metrics.

Returns:
    Dictionary containing process and system metrics, or empty dict if psutil unavailable

#### measure_operation

Context manager for measuring operation performance.

Args:
    operation_name: Name of the operation being measured
    provider_name: Optional provider name (for LLM operations)
    model_name: Optional model name (for LLM operations)

Yields:
    PerformanceMetrics object that can be updated during operation

Example:
    >>> monitor = PerformanceMonitor()
    >>> with monitor.measure_operation("api_call") as metrics:
    ...     # perform operation
    ...     metrics.input_tokens = 100

#### get_operation_stats

Get statistical analysis for an operation.

Args:
    operation_name: Name of the operation to analyze

Returns:
    OperationStats object with statistical measures

#### get_performance_summary

Get comprehensive MCP performance summary.

#### track_object

Track an object for memory leak detection using weak references.

Args:
    obj: Object to track
    name: Optional name for logging

#### clear_metrics

Clear all metrics.

#### get_memory_usage_trend

Get memory usage trend over time.

Args:
    window_minutes: Time window to analyze

Returns:
    List of memory usage data points grouped by minute

#### detect_memory_leaks

Detect potential memory leaks using linear regression.

Args:
    threshold_mb: Memory growth threshold in MB to trigger leak detection

Returns:
    Dictionary with leak detection results and diagnostics

#### get_leak_recommendations

Get recommendations for addressing potential memory leaks.

Returns:
    List of recommendation strings

#### benchmark_function

Benchmark a function or callable.

Args:
    func: Function to benchmark
    num_iterations: Number of times to run the function
    operation_name: Name for the benchmark operation
    *args: Positional arguments for the function
    **kwargs: Keyword arguments for the function

Returns:
    Dictionary with benchmark results

#### benchmark_provider

Benchmark a provider/model combination.

Args:
    provider_func: Function that calls the provider
    provider_name: Name of the provider
    model_name: Name of the model
    num_requests: Number of requests to make
    **kwargs: Additional arguments for the provider function

Returns:
    ProviderBenchmark object with results

#### compare_providers

Compare benchmark results across providers.

Args:
    benchmark_keys: Optional list of specific benchmarks to compare

Returns:
    Dictionary with comparison results

#### get_fastest_provider

Get the fastest provider based on benchmarks.

Args:
    min_success_rate: Minimum success rate threshold

Returns:
    Provider name or None if no suitable provider found

#### get_benchmark_summary

Get summary of all benchmarks.

Returns:
    Dictionary with benchmark summary

#### measure_performance

Decorator for measuring function performance.

Automatically measures execution time, memory usage, and other metrics
for both synchronous and asynchronous functions.

Args:
    operation_name: Optional custom operation name (defaults to function name)
    provider_name: Optional provider name (for LLM operations)
    model_name: Optional model name (for LLM operations)

Returns:
    Decorated function that measures performance

Example:
    >>> @measure_performance("api_call")
    ... def call_api():
    ...     # perform API call
    ...     return result

    >>> @measure_performance("llm_call", provider_name="openai", model_name="gpt-4")
    ... async def call_llm():
    ...     # perform LLM call
    ...     return response

#### measure_method

Decorator for measuring class method performance.

Similar to measure_performance but designed for class methods.
Automatically includes class name in operation name.

Args:
    operation_name: Optional custom operation name
    provider_name: Optional provider name (for LLM operations)
    model_name: Optional model name (for LLM operations)

Returns:
    Decorated method that measures performance

Example:
    >>> class MyService:
    ...     @measure_method("process_data")
    ...     def process(self, data):
    ...         # process data
    ...         return result

#### add_rule

Add a style rule.

#### is_email

Validate email address.

#### is_url

Validate URL.

#### is_phone

Validate phone number (basic US format).

#### is_ipv4

Validate IPv4 address.

#### is_ipv6

Validate IPv6 address (simplified).

#### validate_email

Validate email format.

#### validate_url

Validate URL, return cleaned or None.

#### validate_phone

Validate phone, return cleaned or None.

#### optimize_memory

Execute a full optimisation pass and return results.

#### get_optimization_recommendations

Return current optimisation recommendations.

#### get_memory_health_report

Summarise current memory health with a score.

#### _calculate_health_score

Compute a crude health score from memory metrics.

#### read_file_chunked

Yield file contents chunk by chunk.

#### read_file_mmap

Read a file via memory mapping with a plain read fallback.

#### get_file_size_mb

Return file size in megabytes.

#### should_use_streaming

Decide if the file should be read via streaming.

#### get_current_memory_stats

Return the latest memory statistics.

#### check_memory_pressure

Evaluate whether the process is under memory pressure.

#### suggest_optimizations

Return practical hints based on current metrics.

#### create_context_id

Generate a deterministic identifier for a context payload.

#### compress_text

Compress text into a `CompressionResult`.

#### should_compress

Heuristically determine whether compression is worthwhile.

#### chunk_context

Split large contexts into smaller chunks.

#### compress_context

Compress and store a context if it exceeds the threshold.

#### get_context

Get a specific context configuration.

#### remove_context

Remove a context from memory.

#### get_memory_usage

Get memory usage information.

#### get_memory_optimizer

Return the shared memory optimizer instance.

#### optimize_memory_now

Trigger an immediate memory optimization run.

#### get_memory_recommendations

Return recommendations from the shared memory optimizer.

#### compress_large_context

Compress text when beneficial and return its context identifier.

#### get_compressed_context

Retrieve a previously compressed context.

#### decompress

Restore the original text.

#### force_gc

Run garbage collection for a given generation (or all).

#### find_circular_references

Locate objects that may participate in circular references.

#### get_gc_stats

Return a structured view of GC statistics.

#### optimize_gc_thresholds

Adjust GC thresholds based on current memory pressure.

#### eq



#### neq



#### gt



#### gte



#### lt



#### lte



#### like



#### ilike



#### in_



#### is_null



#### invalidate

Invalidate cached value for an object.

#### make_key



#### has_fields

Check if the response has all required fields.

#### has_any_fields

Check if the response has any of the specified fields.

#### validate_pagination

Validate pagination structure.

#### validate_list_response

Validate list response structure.

#### validate_success_response

Validate standard success response.

#### extract_id

Extract an identifier field from common response shapes.

#### is_uuid

Check if value is a valid UUID string.

#### is_iso_timestamp

Check if value is an ISO 8601 timestamp.

#### is_in_range

Check if value is within a numeric range.

#### is_valid_slug

Check if value matches a slug pattern.

#### timestamp

Generate timestamp string for unique identifiers.

#### unique_id

Generate unique identifier with optional prefix.

#### uuid

Generate a random UUID string.

#### slug_from_uuid

Generate a slug-safe unique identifier.

#### organization_data

Generate organization test data with valid slug.

#### project_data

Generate project test data.

#### document_data

Generate document test data.

#### requirement_data

Generate requirement test data.

#### test_data

Generate test case data.

#### batch_data

Generate batch test data for a given entity type.

#### timeout_wrapper

Decorator adding a timeout to async test functions.

#### detect_slow_tests

Return tests whose recorded durations exceed the threshold.

#### is_connection_error

Check if an error message indicates a connection failure.

#### immediate

No wait.

#### linear

Linear backoff: delay × attempt.

#### exponential

Exponential backoff capped at max_delay.

#### fibonacci

Fibonacci backoff sequence.

#### fib



#### _get_client

Get Supabase client with user's JWT for RLS.

#### _build_cache_key



#### _apply_ordering



#### _apply_pagination



#### list_active_workflows

List all active workflows.

#### workflow

Decorator to mark a class as a workflow.

#### step

Decorator to mark a method as a workflow step.

#### _discover_steps

Discover workflow steps from methods.

#### add_step

Add a step to the workflow.

#### get_steps

Get all saga steps.

#### register_saga

Register a saga.

#### add_state

Add a state.

#### add_transition

Add a transition.

#### trigger

Trigger an event.

#### _find_transition

Find transition for event from current state.

#### can_trigger

Check if event can be triggered.

#### schedule_interval

Schedule job at fixed interval.

Args:
    name: Job name
    handler: Async function to execute
    seconds: Interval in seconds
    minutes: Interval in minutes
    hours: Interval in hours

Returns:
    Job ID

#### schedule_cron

Schedule job with cron expression (basic support).

Args:
    name: Job name
    handler: Async function
    cron: Cron expression (e.g., "0 * * * *" for hourly)

Returns:
    Job ID

#### _parse_cron_next

Parse cron expression to next run time (simplified).

#### get_job

Get job by ID.

#### enable_job

Enable a job.

#### disable_job

Disable a job.

#### remove_job

Remove a job.

#### list_jobs

List all jobs.

#### register_agent

Register an agent.

#### record_start

Record workflow start.

#### record_complete

Record workflow completion.

#### get_execution

Get execution record.

#### _update_metrics



#### load_swe_bench_patterns

Load proven patterns from SWE-bench results.

Returns:
    Dictionary of patterns keyed by pattern name

#### _get_patterns_by_task_type

Get count of patterns by task type.

#### get_cache_hit_rate

Calculate cache hit rate.

#### get_average_cost_per_request

Calculate average cost per request.

#### determine_optimal_routing

Determine optimal routing strategy for a task.

Args:
    task_type: Type of development task
    complexity: Task complexity level
    usage: Current usage metrics
    remaining_budget: Remaining API budget
    context: Additional task context

Returns:
    Optimal cost strategy

#### _cost_first_routing

Select cheapest model that meets minimum requirements.

#### _performance_first_routing

Select highest performance model within budget.

#### _balanced_routing

Balance cost and performance based on task requirements.

#### _budget_aware_routing

Select model based on current budget situation.

#### _calculate_performance_score

Calculate performance score for a model based on its characteristics.

#### _calculate_speed_score

Calculate speed score based on model characteristics.

#### _calculate_max_iterations

Calculate maximum iterations based on complexity and model.

#### _get_routing_reason

Generate human-readable routing decision reason.

#### _get_fallback_models

Get fallback models when none are suitable for the task.

#### set_routing_strategy

Set the routing strategy to use.

#### get_routing_statistics

Get statistics about routing decisions.

#### optimize_usage

Generate optimization recommendations based on usage patterns.

Args:
    usage: Current usage metrics
    recommendations_limit: Maximum number of recommendations

Returns:
    List of optimization recommendations

#### _analyze_complexity_usage

Analyze usage by task complexity and recommend optimizations.

#### _optimize_caching

Generate cache optimization recommendations.

#### _optimize_batch_processing

Generate batch processing recommendations.

#### _optimize_task_prioritization

Generate task prioritization recommendations.

#### calculate_optimization_impact

Calculate the potential impact of implementing optimizations.

Args:
    current_usage: Current usage metrics
    optimizations: List of optimization recommendations

Returns:
    Impact analysis

#### _init_redis_client

Initialize Redis client with fallback to in-memory cache.

Args:
    config: Configuration dictionary

Returns:
    Redis client or None

#### _generate_cache_key

Generate cache key from task description and context.

Args:
    description: Task description
    context: Task context

Returns:
    Cache key string

#### _calculate_savings

Calculate estimated monthly savings from optimization.

Returns:
    Estimated savings amount

#### add_pre_execution_hook

Add a hook to be called before task execution.

#### add_post_execution_hook

Add a hook to be called after task execution.

#### add_decision_hook

Add a hook to be called during routing decisions.

#### _check_cost_intervention

Check if cost intervention is needed.

#### _analyze_cost_variance

Analyze cost variance in execution history.

#### _analyze_cost_trend

Analyze cost trends over time.

#### _calculate_std_dev

Calculate standard deviation.

#### set_scheduling_strategy

Set task scheduling strategy.

#### _complexity_level

Get numeric level for complexity comparison.

#### get_available_count

Get number of available ports.

Returns:
    Number of ports available for allocation

#### release_all_for_agent

Release all ports allocated to a specific agent.

Args:
    agent_id: Agent identifier

Returns:
    Number of ports released

#### cleanup_stale_allocations

Clean up port allocations older than max_age.

Args:
    max_age_seconds: Maximum age in seconds (default: 1 hour)

Returns:
    Number of ports released

#### record_task_metric

Record an agent task status event into the event store.

Captures timestamps and duration alongside agent/model metadata to feed
duration estimators and operational metrics. No-op if event store disabled.

Args:
    task_context: Task execution context with task details
    event: Event type (e.g., "task_started", "task_completed", "task_failed")

#### record_task_performance

Record task performance metrics.

Args:
    task_id: Task identifier
    execution_time: Execution time in seconds
    memory_usage: Memory usage in bytes (optional)
    cpu_usage: CPU usage percentage (optional)
    **kwargs: Additional performance metrics

#### get_task_metrics

Get aggregated metrics for a task.

Args:
    task_id: Task identifier

Returns:
    Dictionary of metrics

#### record_task_completion

Record task completion for metrics.

#### get_summary

Get validation summary.

#### create_task_storage

Factory function to create appropriate task storage.

Args:
    redis_client: Optional Redis client. If None, checks environment.

Returns:
    TaskStorage instance (either Redis or in-memory)

#### get_temporal_client

Get the global Temporal workflow client.

#### _prepare_retry_policy

Prepare retry policy with default values if needed.

#### _create_error_result

Create an error result for failed orchestration.

#### set_signal

Set a signal value.

#### get_signal

Get a signal value.

#### mark_activity_completed

Mark an activity as completed.

#### get_event_bus



#### get_storage_backend



#### setup_context

Setup workflow context.

#### workflow_activity

Mark a function as a workflow activity.

#### workflow_signal

Mark a function as a workflow signal handler.

#### check_prerequisites

Check if Vercel CLI is installed and user is authenticated.

#### get_deployment_url

Get deployment URL.

#### get_logs

Retrieve log entries for a service.

#### get_environment_domain

Get default domain for environment.

This is platform-specific and should be overridden by application.

#### get_environment_file

Get environment file path for environment.

#### create_vercel_config

Create vercel.json configuration.

#### log_info

Log informational messages.

#### log_warning

Log warning messages.

#### check_with_retries

Check URL health with retries.

Args:
    url: URL to check
    max_retries: Maximum number of retry attempts
    retry_delay: Delay between retries in seconds
    timeout: Timeout per attempt in seconds

Returns:
    True if healthy within retry limit, False otherwise

#### check_endpoint

Check specific endpoint.

Args:
    base_url: Base URL (e.g., https://example.com)
    endpoint: Endpoint path (e.g., /health)
    expected_status: Expected HTTP status code
    timeout: Timeout in seconds

Returns:
    True if endpoint returns expected status

#### check_multiple_endpoints

Check multiple endpoints.

Args:
    base_url: Base URL
    endpoints: List of endpoint paths
    timeout: Timeout per endpoint

Returns:
    Dictionary mapping endpoints to their status (True/False)

#### check_with_validator

Check URL with custom validator function.

Args:
    url: URL to check
    validator: Function that takes response and returns bool
    timeout: Timeout in seconds

Returns:
    True if validator returns True

#### check_json_response

Check if JSON response contains expected keys.

Args:
    url: URL to check
    expected_keys: List of keys that should be in response
    timeout: Timeout in seconds

Returns:
    True if all expected keys present

#### check_response_time

Check response time.

Args:
    url: URL to check
    max_response_time: Maximum acceptable response time in seconds
    timeout: Timeout in seconds

Returns:
    Tuple of (success: bool, response_time: float)

#### cli

Pheno-SDK CLI - Framework for the pheno-sdk ecosystem.

#### stream_logs

Stream combined stdout/stderr for all processes synchronously.

#### _build_env



#### parse



#### compile_to_vercel

Compile to vercel.json.

#### unregister_provider

Unregister a health check provider.

#### provider_supports

Check if a provider supports a resource type.

#### get_provider_metadata

Get metadata for a specific provider.

#### get_supported_providers

Get list of providers that support a resource type.

#### provider_exists

Check if a provider is registered.

#### get_provider_info

Get detailed information about a provider.

#### must_register

Register a provider and raise exception on error.

This is useful for init-time registration where you want to fail fast.

#### supports



#### calculate_backoff

Calculate next retry delay with exponential backoff.

#### retry_sync

Retry a sync function with exponential backoff.

#### wrap_error

Wrap a generic error as a CloudError.

#### _format_message



#### log_error

Log error messages.

#### start_tunnel



#### stop_tunnel



#### get_tunnel_url

Get tunnel URL for port.

Args:
    port: Port to get URL for

Returns:
    URL or None if no tunnel

#### candidate_pheno_sdk_paths

Return potential pheno-sdk locations relative to a project.

#### resolve_pheno_sdk_root

Determine the pheno-sdk root directory.

#### scan_packages

Inspect the pheno-sdk tree and gather package availability.

#### detect_used_packages

Detect which packages are referenced by the project.

#### write_vendor_init

Create an __init__.py for the vendor directory.

#### generate_prod_requirements

Generate production requirements file.

#### create_sitecustomize

Create sitecustomize.py that points to the vendor directory.

#### generate_manifest

Generate a manifest of vendored packages.

#### copy_package

Copy a package into the vendor directory.

#### handle_kinfra

Copy the special KInfra package if present.

#### _selected_packages



#### vendor_packages

Vendor the requested packages into the vendor directory.

#### validate_vendored

Validate vendored packages by checking for core files.

#### test_imports

Test importing each vendored package.

#### clean

Remove vendored packages directory.

#### vendor_all

Complete vendoring workflow.

#### __next__



#### supports_resource



#### get_capabilities

Return the capabilities for a model identifier.

#### generate_hooks

Generate build hooks for deployment platforms.

#### install_hooks

Install git pre-push hook for automatic vendoring.

#### uninstall_hooks

Uninstall git pre-push hook.

#### verify_hooks

Verify git hook installation.

#### check_freshness_cmd

Check if vendored packages are up-to-date.

#### startup_check_cmd

Check vendored packages before production startup.

#### setup

Vendor pheno-sdk packages for production deployment.

#### progress_callback



#### generate_content

Generate content for a prompt.

#### chat

Have a chat conversation.

#### client

Get or initialize the Claude client.

#### generate_response

Generate a response to a prompt.

#### chat_completion

Complete a chat conversation.

#### get_supported_models



#### validate_api_key

Validate that the API key works.

#### get_token_count

Estimate token count for text.

#### _should_use_real_api

Check if real API calls are enabled.

#### _build_api_payload

Build the API request payload.

#### _process_api_response

Process the API response and create a GenerateResponse.

#### _create_echo_response

Create an echo response when real API is not available.

#### _error_response

Create error response.

#### print_success

Print success message.

#### print_error

Print error message.

#### print_info

Print info message.

#### print_warning

Print warning message.

#### print_table

Print a formatted table.

#### create_app

Create and configure the FastAPI application.

Args:
    title: API title
    version: API version
    description: API description
    enable_cors: Whether to enable CORS

Returns:
    Configured FastAPI application

#### get_user_repository

Get user repository from container.

#### get_deployment_repository

Get deployment repository from container.

#### get_service_repository

Get service repository from container.

#### get_configuration_repository

Get configuration repository from container.

#### get_event_publisher

Get event publisher from container.

#### get_create_user_use_case

Get create user use case.

#### get_update_user_use_case

Get update user use case.

#### get_get_user_use_case

Get get user use case.

#### get_list_users_use_case

Get list users use case.

#### get_deactivate_user_use_case

Get deactivate user use case.

#### get_create_deployment_use_case

Get create deployment use case.

#### get_start_deployment_use_case

Get start deployment use case.

#### get_complete_deployment_use_case

Get complete deployment use case.

#### get_fail_deployment_use_case

Get fail deployment use case.

#### get_rollback_deployment_use_case

Get rollback deployment use case.

#### get_get_deployment_use_case

Get get deployment use case.

#### get_list_deployments_use_case

Get list deployments use case.

#### get_deployment_statistics_use_case

Create a GetDeploymentStatisticsUseCase instance.

#### get_create_service_use_case

Get create service use case.

#### get_start_service_use_case

Get start service use case.

#### get_stop_service_use_case

Get stop service use case.

#### get_get_service_use_case

Get get service use case.

#### get_list_services_use_case

Get list services use case.

#### get_service_health_use_case

Create a GetServiceHealthUseCase instance.

#### get_create_configuration_use_case

Get create configuration use case.

#### get_update_configuration_use_case

Get update configuration use case.

#### get_get_configuration_use_case

Get get configuration use case.

#### get_list_configurations_use_case

Get list configurations use case.

#### publish_sync

Synchronous version of publish.

#### get_published_events

Get list of all published events (useful for testing).

#### clear_published_events

Clear the published events list.

#### clear_subscribers

Clear all subscribers.

#### create_engine_from_config

Create SQLAlchemy async engine from configuration.

Args:
    database_url: Database connection URL
    echo: Whether to echo SQL statements
    pool_size: Connection pool size
    max_overflow: Maximum overflow connections

Returns:
    Configured async engine

#### create_session_factory

Create session factory from engine.

Args:
    engine: SQLAlchemy async engine

Returns:
    Session factory

#### to_model

Convert Configuration entity to ConfigurationModel.

Args:
    entity: Configuration domain entity

Returns:
    ConfigurationModel ORM model

#### to_entity

Convert ConfigurationModel to Configuration entity.

Args:
    model: ConfigurationModel ORM model

Returns:
    Configuration domain entity

#### create_sync



#### update_sync

Synchronous wrapper for update.

#### get_sync



#### list_sync



#### start_sync



#### stop_sync



#### health_sync



#### deactivate_sync

Synchronous wrapper for deactivate.

#### complete_sync



#### fail_sync



#### rollback_sync



#### statistics_sync



#### get_provider_class



#### get_or_create_provider



#### get_providers_by_type



#### get_mfa_registry

Convenience alias for DI wiring.

#### get_adapter_class



#### get_or_create_adapter



#### unregister_adapter



#### _parse_token_response



#### event_loop

Create an event loop for the test session.

This fixture provides a single event loop for all async tests in the session.

Example:
    def test_async_function(event_loop):
        result = event_loop.run_until_complete(async_function())
        assert result == expected

#### async_timeout

Factory fixture for creating async timeouts.

Example:
    async def test_with_timeout(async_timeout):
        async with async_timeout(5.0):
            # This will timeout after 5 seconds
            await slow_operation()

#### add_cleanup

Add a cleanup callback.

Args:
    callback: Cleanup function
    *args: Positional arguments for callback
    **kwargs: Keyword arguments for callback

#### db_engine

Create a database engine for testing.

By default, creates an in-memory SQLite database.
Override by setting DATABASE_URL environment variable.

Example:
    def test_with_db(db_engine):
        # Use engine
        with db_engine.connect() as conn:
            result = conn.execute("SELECT 1")

#### db_session

Create a database session for testing.

Automatically rolls back changes after each test.

Example:
    def test_with_session(db_session):
        user = User(name="Test")
        db_session.add(user)
        db_session.commit()
        # Changes rolled back after test

#### db_transaction

Create a database session with transaction rollback.

Uses nested transactions for complete isolation.
All changes are rolled back after the test.

Example:
    def test_with_transaction(db_transaction):
        # All changes rolled back automatically
        user = User(name="Test")
        db_transaction.add(user)
        db_transaction.commit()

#### temp_db_session

Context manager for temporary database session.

Example:
    with temp_db_session(engine) as session:
        user = User(name="Test")
        session.add(user)
        session.commit()

#### restart_savepoint



#### container



#### clean_container



#### user_repository



#### deployment_repository



#### service_repository



#### configuration_repository



#### event_publisher



#### create_user_use_case

Create a CreateUserUseCase instance.

#### update_user_use_case

Create an UpdateUserUseCase instance.

#### get_user_use_case

Create a GetUserUseCase instance.

#### list_users_use_case

Create a ListUsersUseCase instance.

#### deactivate_user_use_case

Create a DeactivateUserUseCase instance.

#### cli_adapter



#### user_commands



#### deployment_commands



#### service_commands



#### configuration_commands



#### sample_user_data



#### sample_deployment_data



#### sample_service_data



#### sample_configuration_data



#### pytest_configure



#### pytest_collection_modifyitems



#### pytest_fixtures

Example pytest fixtures using the factory pattern.

Add these to your conftest.py:

#### get_events

Retrieve a snapshot of recorded events.

Args:
    event_type: Optional filter limiting results to a specific type.

Returns:
    List of matching :class:`CallbackEvent` records.

#### set_response

Set the response for a method call.

#### get_calls

Get recorded calls, optionally filtered by method.

#### clear_calls

Clear recorded calls.

#### repo_factory

Factory for creating in-memory repositories.

#### event_bus

In-memory event bus for testing.

#### mock_service_factory

Factory for creating mock services.

#### mock_http_response

Factory fixture for creating mock HTTP responses.

Example:
    def test_api(mock_http_response):
        response = mock_http_response(
            status_code=200,
            json_data={"user": "test"}
        )
        assert response.json()["user"] == "test"

#### http_client

Create an HTTP client for testing.

Uses httpx.Client with sensible defaults for testing.

Example:
    def test_api(http_client):
        response = http_client.get("https://api.example.com")
        assert response.status_code == 200

#### mock_http_server

Create a mock HTTP server for testing.

Example:
    def test_api_client(mock_http_server):
        mock_http_server.add_response(
            "GET", "/users",
            json_data={"users": [{"id": 1, "name": "Test"}]}
        )

        response = mock_http_server.request("GET", "/users")
        assert len(response.json()["users"]) == 1

#### mock_httpx_response

Create a mock httpx.Response object.

Example:
    from unittest.mock import patch

    with patch('httpx.get') as mock_get:
        mock_get.return_value = mock_httpx_response(
            json_data={"message": "success"}
        )
        # Test code here

#### json



#### ok

Check if response is successful.

#### raise_for_status

Raise exception for error status codes.

#### _create_response



#### add_response

Add a mock response for a specific method and path.

Args:
    method: HTTP method (GET, POST, etc.)
    path: URL path
    status_code: Response status code
    text: Response text
    json_data: Response JSON data
    headers: Response headers

#### request

Make a mock request.

Args:
    method: HTTP method
    path: URL path
    **kwargs: Additional request parameters (stored for inspection)

Returns:
    MockHTTPResponse

#### get_requests

Get recorded requests, optionally filtered.

Args:
    method: Filter by HTTP method
    path: Filter by path

Returns:
    List of matching requests

#### mock_cache_dir



#### valid_token_data



#### expired_token_data



#### expiring_soon_token_data



#### mock_oauth_client



#### mock_oauth_client_with_valid_token



#### mock_oauth_client_with_expired_token



#### mock_oauth_client_with_expiring_token



#### mock_oauth_client_no_token



#### mock_server_client



#### mock_progress_widget



#### mock_metrics_tracker



#### mock_textual_app



#### corrupt_token_file



#### token_without_expiry



#### assert_widget_renders



#### get_cache_path



#### save_token



#### load_token



#### clear_token



#### add_task



#### record_api_call



#### record_error



#### get_avg_latency



#### _compute_expiry



#### _trim_locked



#### record_hit



#### record_miss



#### record_set



#### record_eviction



#### _get_path

Get full file path.

#### _get_full_path

Get full filesystem path for a bucket/path combination.

#### build_metrics_record

Construct a `MetricsRecord` from partial metrics information.

#### from_sqlite

Create a collector wired to an SQLite database.

#### record_request_start

Mark the beginning of a request.

#### record_model_selection

Attach model selection information to an in-flight request.

#### record_model_performance

Record quantitative metrics once the model responds.

#### record_quality_assessment

Attach quality metrics collected post-response.

#### finalize_request

Finalize an in-flight request and cache the resulting record.

#### flush_cache

Persist all cached records using the configured storage backend.

#### get_cached_records

Return a copy of cached records (useful for testing).

#### inflight_request_ids

Iterate over in-flight request IDs.

#### _require_request



#### write_records



#### _ensure_schema



#### _ensure_additional_columns

Add newly introduced columns if the table was created previously.

#### add_point

Add a metric point to the series.

#### get_latest

Get the latest metric point.

#### get_average

Get average value over time window.

#### gauge

Record a gauge metric.

#### counter

Record a counter metric.

#### histogram

Record a histogram metric.

#### summary

Record a summary metric.

#### _ensure_series

Ensure a metric series exists.

#### _trim_series

Trim series to buffer size.

#### get_metric

Get metric by name.

#### get_all_metrics

Get all metrics.

#### get_metric_summary

Get a summary of all metrics.

#### _create_base_summary

Create the base summary structure.

#### _build_series_summary

Build summary for all metric series.

#### _build_single_series_summary

Build summary for a single metric series.

#### register_collector

Register a metrics collector.

#### unregister_collector

Unregister a metrics collector.

#### get_collector

Get a metrics collector by name.

#### get_global_summary

Get a global summary of all metrics.

#### _find_provider_for_panel

Find a provider for a panel based on panel type or configuration.

#### create_dashboard

Create a new dashboard.

#### get_dashboard

Get a dashboard by ID.

#### get_dashboard_by_name

Get a dashboard by name.

#### list_dashboards

List all dashboards.

#### update_dashboard

Update a dashboard.

#### delete_dashboard

Delete a dashboard.

#### add_panel

Add a monitoring panel.

#### remove_panel

Remove a monitoring panel.

#### get_dashboard_data

Get dashboard data for external use.

#### enable_check

Enable a health check.

#### disable_check

Disable a health check.

#### get_check_result

Get the last result for a health check.

#### get_all_results

Get all last results.

#### get_overall_health

Get overall health status.

#### get_recent_events

Return up to ``limit`` most recently recorded events.

#### get_events_by_type

Get events by type.

#### get_events_by_severity

Get events by severity.

#### clear_buffer

Clear event buffer.

#### add_emitter

Add an event emitter to collect from.

#### remove_emitter

Remove an event emitter.

#### _add_new_events

Add new events to the collection.

#### get_all_events

Get all collected events.

#### get_events_by_source

Get events by source.

#### get_event_summary

Get a summary of collected events.

#### _build_subprocess_kwargs

Build subprocess keyword arguments.

#### _create_command_result

Create a CommandResult object.

#### _validate_result

Validate command result if output validation is enabled.

#### _finalize_command_execution

Finalize command execution by updating state.

#### _handle_command_error

Handle command execution errors.

#### _add_to_history



#### get_running_commands

Get list of running command IDs.

#### get_command_result

Get result for a command.

#### get_command_history

Get command execution history.

#### get_successful_commands

Get successful command results.

#### get_failed_commands

Get failed command results.

#### clear_history



#### get_scheduled_commands

Get list of scheduled command IDs.

#### _setup_logging

Setup logging configuration.

#### add_provider

Add a monitoring provider.

#### remove_provider

Remove a monitoring provider.

#### get_metrics_collector

Get the global metrics collector instance.

#### get_event_emitter

Get the event emitter.

#### add_dashboard_component

Add a dashboard component.

#### add_ui_component

Add a UI component.

#### add_tui_component

Add a TUI component.

#### add_health_check

Add a health check component.

#### remove_health_check

Remove a health check component.

#### add_progress_display

Add a progress display component.

#### add_status_indicator

Add a status indicator component.

#### add_cli_component

Add a CLI component.

#### remove_progress_display

Remove a progress display component.

#### remove_status_indicator

Remove a status indicator component.

#### remove_cli_component

Remove a CLI component.

#### create_default_contexts

Create default context configurations.

#### save_project_config

Save project-specific configuration.

#### expand_workspace_path

Expand user paths in workspace configuration.

#### add_context

Add or update a context configuration.

#### list_contexts

List all available contexts.

#### expand_paths

Expand user paths in configuration.

#### detect_from_entry_point

Detect context from command name (atoms, zen, byteport).

#### detect_from_project

Detect context from project files and patterns.

#### detect_from_environment

Detect context from environment variables.

#### detect_from_config

Detect context from configuration files.

#### detect_context

Detect the appropriate context for a project.

#### workspace

Set the workspace directory.

#### templates_dir

Get the templates directory.

#### context_templates_dir

Get the context-specific templates directory.

#### shared_templates_dir

Get the shared templates directory.

#### get_current_project_path

Get the current project path if we're inside one.

#### is_pheno_project

Check if a path is a pheno project.

#### _has_pheno_markers

Check for common pheno project markers.

#### switch_context

Switch to a different context.

#### get_available_contexts

Get all available contexts with descriptions.

#### get_context_info

Get information about the current context.

#### launch_wireframe

Factory function to create and launch wireframes.

#### run_wireframe_app

Run a wireframe in a Textual app.

#### add_content

Add content widget to wireframe.

#### add_action

Add an action button.

#### get_header_content

Get header content with context info.

#### get_footer_content

Get footer with available actions.

#### compose

Produce the widget tree rendered by the component.

#### get_progress_display

Get progress indicator panel.

#### get_status_panel

Get deployment status panel.

#### get_project_info

Get project information panel.

#### get_quick_stats

Get quick statistics panel.

#### get_section_header

Get current section header.

#### get_system_status

Get system status panel.

#### get_service_status



#### get_resource_usage

Get resource usage panel.

#### get_network_status

Get network status panel.

#### on_mount

Lifecycle hook invoked after the component has been mounted.

#### _load_configuration

Load configuration from file or defaults.

#### _handle_command_output

Handle streaming command output.

#### _setup_tables

Setup data tables.

#### action_execute_command

Execute command from input.

#### action_show_help

Show help information.

#### action_show_status

Show detailed status.

#### action_show_logs

Switch to logs view.

#### update_status

Update status display.

#### _update_processes_table

Update the processes table.

#### _update_projects_table

Update projects table with status data.

#### _update_logs

Update logs tab with recent activity.

#### action_quit

Quit the application.

#### add_output_callback

Add callback for streaming output.

Args:
    callback: Function called with (command_id, stream_type, line)
             where stream_type is 'stdout' or 'stderr'

#### _emit_output

Emit output to all registered callbacks.

#### execute_command

Execute the entered command.

#### _detect_project_context

Detect project context from command or working directory.

#### _build_command



#### _execute_command_thread

Execute command in a separate thread.

#### cancel_command

Cancel a running command.

#### route_command

Route a command input to appropriate project context.

Args:
    command_input: Raw command input from user
    default_project: Default project if not specified

Returns:
    Command ID if successfully routed, None otherwise

#### _handle_help_command

Handle help command.

#### _handle_history_command

Handle history command.

#### _handle_clear_command

Handle clear command.

#### get_command_suggestions

Get command suggestions for autocomplete.

Args:
    partial_input: Partial command input

Returns:
    List of suggested completions

#### validate_command

Validate a command and return (is_valid, error_message).

#### get_suggestions

Get command completion suggestions.

#### get_result

Get result for a command.

#### cancel

Cancel a running command.

#### get_history

Get the history of state changes.

Args:
    limit: Maximum number of changes to return

Returns:
    List of state changes

#### init_git_repo

Initialize a git repository in the project directory.

#### is_git_repo

Check if path is a git repository.

#### get_git_root

Get the root of the git repository.

#### get_user_config_dir

Get user configuration directory.

#### get_user_data_dir

Get user data directory.

#### get_user_cache_dir

Get user cache directory.

#### handle_exception

Handle and display exceptions in a user-friendly way.

#### load_setup_project_module

Dynamically load the setup_project.py module.

#### setup_full_project

Setup complete standardized CI/CD for a project.

#### copy_template

Copy a template file to target location.

#### set_replacements

Set template replacement variables.

#### generate_project

Generate a project from a template (legacy method).

#### create_project

Create a project from template with context support.

Returns:
    List of created files

#### _create_basic_structure

Create basic project structure.

Returns:
    List of created files

#### add_template

Add a custom template.

#### package

Build package for distribution.

#### set_config

Set the configuration data.

#### reset_config

Reset configuration to defaults.

#### add_nested_config



#### deploy_package

Deploy/publish project packages.

#### deploy_pypi

Deploy Python package to PyPI.

#### deploy_status

Check deployment status.

#### _detect_deployment_type

Auto-detect appropriate deployment type.

#### _is_python_project

Check if path contains a Python project.

#### _is_npm_project

Check if path contains an NPM project.

#### _has_dockerfile

Check if path contains a Dockerfile.

#### _show_dry_run_info

Show dry run information.

#### _run_basic_deployment

Run basic deployment without TUI.

#### _deploy_python_basic

Basic Python deployment.

#### _deploy_npm_basic

Basic NPM deployment.

#### _deploy_docker_basic

Basic Docker deployment.

#### _run_tui_deployment

Run deployment with TUI interface.

#### on_progress_update



#### start_monitor

Start the Pheno Control Center TUI monitor.

#### _get_context_integrations

Get context-specific integration configuration.

#### _show_context_next_steps

Show context-specific next steps.

#### project

Create a new project.

#### template

Add a custom project template.

#### dashboard

Launch main dashboard.

#### monitor

Launch the Pheno Control Center TUI monitor.

#### infer_proxy_port



#### print_banner

Print application banner.

#### check_dependencies

Check for optional dependencies and provide installation instructions.

#### print_help

Print help information.

#### cicd

Apply standardized CI/CD setup to a project.

#### dev

Setup development environment for a project.

#### migrate

Apply a chain of migrations to reach ``to_version``.

#### hooks

Setup pre-commit hooks for a project.

#### testing

Setup testing infrastructure for a project.

#### current

Show current context information.

#### use_context

Switch to a different context.

#### context_info

Show detailed information about a context.

#### test

Run tests.

#### lint

Run linting checks.

#### format_code

Format code.

#### infer_fallback_port



#### add_log_entry

Add a log entry to the monitor.

#### subscribe_to_events

Subscribe to monitoring events.

Args:
    callback: Function called with (event_type, event_data)
             Event types: 'process_state_changed', 'resource_state_changed',
                         'log_entry', 'process_added', 'process_removed'

#### _emit_event

Emit an event to all subscribers.

#### log_entry

Add a log entry to the monitoring system.

#### update_process_state

Update process state.

#### update_resource_state

Update resource state.

#### get_global_status

Get status of all multi-tenant resources.

#### get_project_status

Get comprehensive status for a project.

#### get_project_processes

Get all processes for a project.

#### get_project_resources

Get all resources for a project.

#### _print_status

Print current status.

#### _require_rich



#### _make_monitor_panel

Create the Rich monitor panel.

#### _make_project_panel

Create a panel for a specific project.

#### _make_logs_panel

Create logs panel with recent entries.

#### set_metric

Set a single metric.

#### remove_metric

Remove a metric.

#### set_data

Set table data.

#### add_column

Add a column to the grid.

#### add_log

Add a new log entry.

#### clear_logs

Clear all logs.

#### create_status_panel

Create a context-themed status panel.

#### create_monitoring_dashboard

Create a context-specific monitoring dashboard.

#### add_field

Add a field to the form.

#### get_values

Get current form values.

#### add_notification

Add a notification.

#### _dismiss_notification

Dismiss a notification by ID.

#### clear_notifications

Clear all notifications.

#### update_progress

Update progress value and optional label.

#### reactive



#### __get__



#### __set__



#### set_status

Update status and optional label.

#### _on_deployment_update

Handle deployment progress updates from the pipeline.

Args:
    deployment: Deployment pipeline instance emitting the update.

#### create_deployment

Factory function to create deployment pipelines.

Args:
    deployment_type: Key identifying the deployment pipeline ('pypi',
        'npm', 'docker', or 'system-service').
    project_path: Path to the project root.
    config: Deployment configuration dictionary forwarded to the pipeline.

Returns:
    Instance of :class:`BaseDeployment` subclass.

#### _init_stages

Define the stages executed for a PyPI deployment.

The stage list controls both execution order and relative weight used for
progress calculations.

#### add_callback

Add callback for metric updates.

#### _notify_callbacks

Notify all registered callbacks about the new entry.

#### get_overall_progress

Calculate overall progress as a percentage across all stages.

Returns:
    Floating-point percentage between 0 and 100.

#### get_current_stage

Retrieve the stage currently being executed.

Returns:
    The active :class:`DeploymentStage` or ``None`` when idle.

#### get_command_engine

Get the global command engine instance.

#### set_env

Set environment variable.

#### get_path

Get node at path.

#### add_to_path

Add path to PATH environment variable.

#### get_python_path

Get Python executable path.

#### get_pheno_sdk_path

Get pheno-sdk installation path.

#### setup_development_environment

Set up development environment variables.

#### add_validator

Add a command validator.

#### _prepare_command

Prepare command for execution.

#### _validate_command

Validate command using all validators.

#### _setup_callbacks

Setup callbacks in the pipeline.

#### _handle_execution_error

Handle execution errors and return error result.

#### is_valid

Check if validation passed.

#### register_validator

Register a custom validator.

#### _get_type_validators

Get validators specific to project type.

#### _run_builtin_validator

Run a built-in validator.

#### _get_validator_map

Get mapping of validator names to their methods.

#### _create_unknown_validator_result

Create a result for unknown validators.

#### _validate_python_structure

Validate Python project structure.

#### _validate_python_dependencies

Validate Python dependencies.

#### _validate_python_imports

Validate Python imports.

#### _validate_node_structure

Validate Node.js project structure.

#### _validate_node_dependencies

Validate Node.js dependencies.

#### _validate_node_scripts

Validate Node.js scripts.

#### _validate_rust_structure

Validate Rust project structure.

#### _validate_rust_dependencies

Validate Rust dependencies.

#### _validate_go_structure

Validate Go project structure.

#### _validate_go_modules

Validate Go modules.

#### set_error

Set error status.

#### duration

Command duration in seconds.

#### failed_stages

Get stages that failed.

#### all_logs

Get all logs from all stages.

#### _trigger_callbacks

Trigger all registered callbacks.

#### cleanup

Clean up resources for a specific service.

#### to_string

Convert parsed command back to string format.

#### parse_command_string

Parse a command string into structured components.

Args:
    command: Command string to parse

Returns:
    ParsedCommand with structured components

#### parse_command_list

Parse a command list into structured components.

Args:
    command_parts: List of command parts

Returns:
    ParsedCommand with structured components

#### parse_command_with_template

Parse command using a template for validation.

Args:
    command: Command string or list
    template: Command template for validation

Returns:
    ParsedCommand with template validation

#### _validate_against_template

Validate parsed command against template.

#### compose_command

Compose a command string from components.

Args:
    command: Main command
    args: Positional arguments
    flags: Boolean flags
    options: Options with values

Returns:
    Composed command string

#### compose_command_list

Compose a command list from components.

Args:
    command: Main command
    args: Positional arguments
    flags: Boolean flags
    options: Options with values

Returns:
    Composed command list

#### compose_from_template

Compose command using a template and values.

Args:
    command: Main command
    template: Command template
    values: Values to populate template

Returns:
    Composed command string

#### escape_command_part

Escape a command part for safe shell usage.

Args:
    part: Command part to escape

Returns:
    Escaped command part

#### merge_commands

Merge additional arguments into a base command.

Args:
    base_command: Base command string
    additional_args: Additional arguments to append

Returns:
    Merged command string

#### _prepare_environment

Prepare environment for subprocess execution.

#### _format_output

Format command output according to configuration.

#### add_hook

Add a hook for execution events.

Args:
    event: Event name ('pre_execute', 'post_execute', 'on_error', 'on_success')
    hook: Hook function to add

#### remove_hook

Remove a hook.

Args:
    event: Event name
    hook: Hook function to remove

Returns:
    True if hook was removed, False if not found

#### create_build_pipeline

Create a standard build pipeline for a project.

#### create_deploy_pipeline

Create a deployment pipeline for a project.

#### failed_steps

Get steps that failed.

#### successful_steps

Get steps that succeeded.

#### _validate_dependencies

Validate that all project dependencies exist and don't create cycles.

#### _create_execution_plan

Create execution plan based on dependencies and mode.

#### cancel_workflow

Cancel a running workflow.

#### get_running_workflows

Get list of running workflow IDs.

#### validate_result

Validate command result output.

#### add_dangerous_command

Add a command to the dangerous commands list.

#### remove_dangerous_command

Remove a command from the dangerous commands list.

#### set_max_output_size

Set maximum allowed output size.

#### add_allowed_exit_code

Add an allowed exit code.

#### add_notification_handler

Add a notification handler.

#### remove_notification_handler

Remove a notification handler.

#### add_result_transformer

Add a result transformer.

Args:
    name: Transformer name
    transformer: Function that takes CommandResult and returns transformed data

#### remove_result_transformer

Remove a result transformer.

Args:
    name: Transformer name to remove

Returns:
    True if removed, False if not found

#### process_result

Process result using specified transformer.

Args:
    result: Command result to process
    transformer_name: Name of transformer to use

Returns:
    Transformed result data

Raises:
    ValueError: If transformer not found

#### get_available_transformers

Get list of available transformer names.

Returns:
    List of transformer names

#### _transform_to_summary

Transform result to summary format.

#### _transform_to_error_only

Transform result to error output only.

#### _transform_to_stdout_only

Transform result to stdout only.

#### setup_default_transformers

Set up default result transformers.

#### logger

Get the logger instance.

#### log_debug

Log debug messages.

#### _setup_pheno_sdk_paths

Set up pheno-sdk paths for development usage.

#### setup_commands

Set up all commands for this CLI framework.

#### _config_start_parser

Configure the start command parser.

#### _cmd_start

Handle start command.

#### _cmd_stop

Handle stop command.

#### _cmd_status

Handle status command.

#### _cmd_health

Handle health command.

#### _cmd_validate

Handle validate command.

#### _start_server

Start the Atoms MCP server.

#### _stop_server

Stop the Atoms MCP server.

#### _show_status

Show server status.

#### _health_check

Perform health check.

#### _validate_config



#### set_mcp_endpoint_for_target

Set/unset MCP_ENDPOINT for non-test runtime based on target.

Rules:
- production => set to production endpoint
- local      => set to local endpoint
- dev/preview=> unset (NONE)

#### ensure_git_state_and_push

Ensure git working tree is committed and pushed to origin current branch.

Returns 0 on success, non-zero on failure.

#### get_environment_variables

Get current environment variables relevant to MCP servers.

#### _setup_base_parser

Set up the base argument parser.

#### _create_zen_service_configs

Create Zen-specific service configurations.

#### get_server_info



#### _create_atoms_service_configs

Create Atoms-specific service configurations.

#### _create_service_factory

Create a service factory function for the ServiceLauncher.

#### service_factory



#### web_server_config

Create configuration for a web server project.

#### cli_tool_config

Create configuration for a CLI tool project.

#### api_server_config

Create configuration for an API server project.

#### microservice_config

Create configuration for a microservice project.

#### mcp_server_config

Create configuration for an MCP server project.

#### server

Get the underlying gRPC server instance.

#### command

Set the command to run.

#### working_directory

Set the working directory.

#### environment

Add environment variables.

#### tunnel

Enable or disable tunnel.

#### timeouts

Set startup and shutdown timeouts.

#### dev_mode

Enable development mode.

#### verbose

Enable verbose logging.

#### dependencies

Add dependencies.

#### services



#### cli_command

Add a CLI command.

#### validator

Add a validation function.

#### setup_hook

Add a setup hook.

#### custom

Add custom configuration.

#### _setup_services

Setup services and their dependencies.

#### _process_batch_results

Process results from a batch execution.

#### _create_orchestration_result

Create the final orchestration result.

#### _create_sequential_plan

Create sequential execution plan.

#### _create_parallel_plan

Create parallel execution plan (all services at once).

#### _create_dependency_ordered_plan

Create dependency-ordered execution plan.

#### _initialize_components

Initialize all infrastructure components.

#### _import_components

Import required infrastructure components.

#### _setup_allocators

Setup port and resource allocators.

#### _setup_monitoring_components

Setup monitoring components if enabled.

#### _setup_orchestrator

Setup service orchestrator.

#### register_resource



#### get_resource_status



#### get_status_snapshot



#### get_command_for_stage

Return the command associated with a named stage.

#### build_project_context

Construct a project context instance for the given path.

#### on_stage_start



#### on_stage_progress



#### on_stage_complete



#### on_stage_error



#### create_console_callback

Factory for :class:`ConsoleProgressCallback`.

Args:
    verbose: When ``True`` emit intermediate log lines.

Returns:
    Configured :class:`ConsoleProgressCallback` instance.

#### create_rich_callback

Factory for :class:`RichProgressCallback`.

Args:
    console: Optional Rich ``Console`` instance to reuse.

Returns:
    Configured :class:`RichProgressCallback` instance.

#### create_logging_callback

Factory for :class:`LoggingCallback`.

Args:
    logger_name: Name passed to ``logging.getLogger``.

Returns:
    Configured :class:`LoggingCallback` instance.

#### create_file_callback

Factory for :class:`FileCallback`.

Args:
    log_file: Path to the log file.

Returns:
    Configured :class:`FileCallback` instance.

#### _ensure_file

Lazily open the target log file in append mode.

Avoids unnecessary file handles when no output is produced. This method is safe
to call multiple times; it only opens the file on the first invocation.

#### register_progress_callback

Register a progress callback to receive stage lifecycle updates.

Args:
    callback: ProgressCallback implementation.

#### register_completion_callback

Register a completion callback to receive final command notifications.

Args:
    callback: CompletionCallback implementation.

#### register_event_callback

Register a callable that reacts to emitted events of ``event_type``.

Args:
    event_type: Event category string.
    callback: Callable accepting a :class:`CallbackEvent`.

#### trigger_stage_start

Invoke registered callbacks for the start of ``stage``.

Args:
    stage: Stage metadata about to execute.

#### trigger_stage_progress

Invoke registered callbacks when ``stage`` reports progress.

Args:
    stage: Stage metadata with updated progress information.

#### trigger_stage_complete

Invoke registered callbacks after ``stage`` completes.

Args:
    stage: Stage metadata including duration and logs.

#### trigger_stage_error

Invoke registered callbacks after ``stage`` fails.

Args:
    stage: Stage metadata including error information.

#### trigger_command_complete

Notify completion callbacks that the command has finished.

Args:
    result: CommandResult capturing success status and metrics.

#### on_command_complete



#### on_command_error



#### detect_dependencies

Return a tuple of (dependencies, dev_dependencies).

#### load_project_config

Alias for :meth:`load_config` for API parity.

#### detect_tools

Return a list of development tools detected in the project.

#### detect_project_type

Return the most likely project type for the provided path.

#### detect_environment

Auto-detect deployment environment.

Returns:
    str: Environment name (production/staging/development/local)

#### detect_build_command

Infer the build command for a project.

#### detect_test_command

Infer the test command for a project.

#### detect_start_command

Infer the start command for a project.

#### create_metrics_dashboard

Create comprehensive metrics dashboard data.

Args:
    collector: AgentMetricsCollector instance
    aggregator: Optional MetricsAggregator instance
    tracker: Optional PerformanceTracker instance

Returns:
    Dict containing comprehensive dashboard data

#### add_snapshot

Add a performance snapshot.

#### get_aggregated_metrics

Get aggregated metrics.

#### get_time_series

Get time series data for a specific metric.

#### start_request

Start tracking an MCP request.

#### end_request

End tracking an MCP request.

#### to_prometheus

Export metrics in Prometheus format.

#### to_csv

Export metrics in CSV format.

#### start_execution

Record the start of an agent execution.

#### complete_execution

Record the completion of an agent execution.

#### _calculate_summary

Calculate summary statistics.

#### get_recent_metrics

Get recent execution metrics.

#### get_performance_trends

Get performance trends over time.

#### export_metrics

Export monitoring data in various formats.

Args:
    format: Export format ('dict', 'json', 'csv')

Returns:
    Exported data

#### clear_old_metrics

Clear metrics older than specified days.

#### track_llm_call

Async decorator to track LLM provider calls with duration and outcome.

Expects the wrapped coroutine to return an object with optional `.usage`
carrying input_tokens/output_tokens attributes.

#### record_counter

Record a counter metric.

Args:
    name: Metric name
    value: Value to add
    **tags: Optional tags

#### record_gauge

Record a gauge metric.

Args:
    name: Metric name
    value: Current value
    **tags: Optional tags

#### record_histogram

Record a histogram value.

Args:
    name: Metric name
    value: Value to record
    **tags: Optional tags

#### _get_all_metrics

Get all metrics.

#### _get_counters

Get counter metrics.

#### _get_gauges

Get gauge metrics.

#### _get_histograms

Get histogram metrics.

#### _parse_query

Parse query string into dict.

#### get_shared_templates

Get all shared resource templates.

#### get_base_templates

Return core MCP resource templates.

#### add_team

Add a team to the project.

#### create_wbs_node

Create a WBS node with enhanced project management features.

#### create_node

Create a new node in the project graph.

#### get_ready_nodes

Get nodes that are ready to execute (all dependencies satisfied).

#### start_node

Start execution of a node.

#### complete_node

Mark a node as completed.

#### fail_node

Mark a node as failed.

#### send_message

Send a message between nodes.

#### get_messages_for_node

Get all messages for a specific node.

#### get_node_status

Get the status of a specific node.

#### get_project_summary

Get a summary of the project state.

#### _generate_wbs_code

Generate WBS code based on hierarchy position.

#### get_critical_path

Calculate and return critical path analysis.

#### export_to_dict

Export metrics to dictionary.

#### import_from_dict

Import tree from dictionary.

#### _import_basic_properties

Import basic graph properties from data.

#### _import_nodes

Import nodes from data.

#### _process_node_data

Process node data by converting types and enums.

#### _import_messages

Import messages from data.

#### _process_message_data

Process message data by converting types.

#### get_project_templates

Return project-specific resource templates using the provided handler factory.

#### get_counter_value

Get current counter value.

#### get_histogram_values

Get histogram values.

#### get_errors

Get current validation errors.

#### get_span

Get span by ID.

#### _parse_uri

Parse URI into scheme and path.

#### _get_nested

Get nested config value by dot-separated path.

#### initialize_workflow_monitoring

Initialize the global workflow monitoring integration.

#### get_workflow_monitoring

Get the global workflow monitoring integration instance.

#### monitor_workflow_execution

Decorator to automatically monitor workflow execution.

#### integrate_with_fastapi

Integrate monitoring routes with FastAPI application.

#### get_monitoring_context

Create monitoring context for workflow execution.

#### record_workflow_completion

Record workflow completion with observability.

#### _calculate_overall_success_rate

Calculate overall success rate across all workflows.

#### _generate_dashboard_html

Generate simple dashboard HTML.

#### integrate_with_server

One-line integration with existing MCP server.

Args:
    app: FastAPI application instance
    **kwargs: Additional configuration for monitoring

Returns:
    WorkflowMonitoringIntegration: Initialized integration instance

#### get_monitoring_config

Get monitoring configuration from environment variables.

Returns:
    dict: Configuration dictionary

#### configure_monitoring_from_env

Configure monitoring from environment variables.

Returns:
    dict: Full configuration dictionary with all settings

#### create_atoms_framework

Create an enhanced framework for the Atoms MCP server.

#### create_zen_framework

Create an enhanced framework for the Zen MCP server.

#### create_simple_framework

Create a simple framework with basic functionality.

#### create_enhanced_framework

Create an enhanced framework with custom configuration.

#### add_basic_commands

Add basic commands to the subparsers.

#### add_advanced_commands

Add advanced commands to the subparsers.

#### add_maintenance_commands

Add maintenance commands to the subparsers.

#### create_parser

Create the argument parser with all commands.

#### get_mcp_monitor

Get the global MCP performance monitor instance.

#### track_mcp_request

Decorator to track MCP request performance.

#### get_performance_optimizer

Get the global MCP performance optimizer instance.

#### get_system_performance_summary

Get comprehensive MCP performance summary.

#### record_metric

Record a performance metric.

#### get_optimization_history

Get recent optimization history.

#### store



#### ensure



#### get_test_registry



#### mcp_test



#### require_auth



#### get_tests



#### get_by_priority



#### _environment_signature



#### _persist



#### _hash



#### should_skip



#### register_config



#### get_endpoint



#### set_endpoint



#### check_tui_kit_available



#### get_migration_guide



#### create_compatible_widgets



#### _get_cache_path

Get the path to the OAuth token cache file.

Returns:
    Path object pointing to the token cache file location

#### _find_test_result

Find test result matching tool and operation.

Args:
    results_by_test: Dictionary of test results keyed by test name
    tool_name: Tool name to match (empty string to search all)
    op_name: Operation name to match

Returns:
    Matching test result or None

#### _report_rich

Generate rich formatted error report.

#### _print_rich_header

Print the rich report header.

#### _print_rich_connection_info

Print connection information.

#### _print_rich_summary

Print the rich summary section.

#### _build_rich_summary_table

Build the rich summary table.

#### _print_rich_results_by_tool

Print results grouped by tool.

#### _print_rich_tool_section

Print a single tool's results section.

#### _print_rich_footer

Print the rich report footer.

#### _report_plain

Generate plain text error report.

#### _print_rich_result

Print a single test result with rich formatting.

#### _print_plain_result

Print a single test result with plain formatting.

#### _group_by_tool

Group results by tool name.

#### _sanitize_metadata

Sanitize metadata for JSON serialization.

#### create_standard_reporters

Create a standard set of reporters for comprehensive test reporting.

Args:
    output_dir: Directory to write report files
    console_title: Title for console output
    verbose_errors: Show detailed error information

Returns:
    List of configured reporter instances

Example:
    reporters = create_standard_reporters("test-reports")
    for reporter in reporters:
        reporter.report(results, metadata)

#### add_reporter

Add a reporter to the list.

Args:
    reporter: Reporter instance to add

#### _print_rich_error

Print a single error with Rich formatting.

#### _print_plain_error

Print a single error with plain text formatting.

#### _get_suggestion

Get suggestion for a known error pattern.

Args:
    error: Error message to match

Returns:
    Dictionary with suggestion details or None

#### add_known_issue

Add a new known issue pattern and suggestion.

Args:
    pattern: Error message pattern to match
    title: Short title for the issue
    description: Detailed description
    fix: Suggested fix
    doc_link: Optional documentation link

#### record_event

Append an event to the buffer.

#### _select_tests



#### _summarise



#### _get_metadata

Projects provide run-specific metadata for reporting.

#### endpoint



#### _is_text_file

Check if file is likely a text file.

#### create_resource_handler

Factory function to create resource handler for scheme.

#### _register_default_handlers

Register default scheme handlers.

#### get_handler

Get handler for a scheme.

#### _extract_timestamp

Extract timestamp from log line.

#### _extract_level

Extract log level from log line.

#### _get_content_type

Determine content type from file extension.

#### get_parameter



#### _compile_pattern



#### matches



#### extract_parameters



#### validate_parameters



#### parse_query_parameters



#### replace



#### find_template



#### _is_cache_valid



#### get_template_info



#### get_critical_path_names

Get names of nodes in the critical path.

#### is_critical

Check if a node is on the critical path.

#### get_slack_time

Get slack time for a node.

#### add_deliverable

Add a deliverable to this WBS node.

#### add_acceptance_criterion

Add an acceptance criterion to the deliverable.

#### add_quality_gate

Add a quality gate to this WBS node.

#### get_completion_percentage

Calculate completion percentage based on acceptance criteria and deliverables.

#### get_critical_blockers

Get critical items blocking completion.

#### is_satisfied

Check if the criterion is satisfied.

#### get_acceptance_percentage

Get the percentage of acceptance criteria that are satisfied.

#### is_complete

Check if all acceptance criteria are satisfied.

#### get_critical_criteria

Get high priority acceptance criteria that are not satisfied.

#### add_criterion

Add a criterion to the quality gate.

#### add_approval

Add an approval decision from an approver.

#### _evaluate_gate_status

Evaluate and update the quality gate status.

#### get_progress

Get progress information for the quality gate.

#### get_total_capacity

Get total team capacity (sum of all member availability).

#### get_skills

Get all skills available in the team.

#### get_member

Get a team member by ID.

#### _temp_flag



#### format_catalog_items

Format catalog model entries with capability flags and optional details.

Flags rendered: [json] [json:schema] [json:strict] [func] [func+] [stream] [img] or [img:Nmb] [think] + [temp:...]
If show_temperature_details=True and show_details=True, an extra "Temperature:" line is included when constraints exist.

#### load_provider_catalogs

Load provider model catalogs from JSON files.

Args:
    catalog_dir: Directory containing catalog JSON files. If None, uses default.

Returns:
    Dictionary mapping ProviderType to catalog data

#### get_catalog_for_provider

Get catalog data for a specific provider.

Args:
    provider_type: The provider type to get catalog for

Returns:
    Catalog data dictionary (potentially empty if not found)

#### get_all_models_for_provider

Get all model names for a provider from the catalog.

Args:
    provider_type: The provider type

Returns:
    List of model names, potentially empty

#### register_model

Register a model and optional aliases/metadata.

#### _load_catalog



#### get_unified_registry

Get the global unified registry instance.

#### get_provider_capabilities

Get provider capabilities.

#### _get_env_var



#### run_performance_tests

Run comprehensive performance tests.

Returns:
    List of benchmark results

#### run_library_benchmark

Run benchmark for a specific library.

Args:
    library_name: Name of the library
    test_func: Test function to benchmark

Returns:
    Benchmark result

#### run_integration_benchmark

Run integration benchmark.

Returns:
    Benchmark result

#### get_results

Get all validation results.

#### _run_benchmark

Run a single benchmark.

#### _start_monitoring

Start performance monitoring.

#### _stop_monitoring

Stop performance monitoring.

#### _monitor_performance

Monitor performance metrics.

#### _calculate_memory_usage

Calculate average memory usage.

#### _calculate_cpu_usage

Calculate average CPU usage.

#### _benchmark_auth_library

Benchmark authentication library.

#### _benchmark_config_library

Benchmark configuration library.

#### _benchmark_logging_library

Benchmark logging library.

#### _benchmark_errors_library

Benchmark errors library.

#### _benchmark_testing_library

Benchmark testing library.

#### _benchmark_docs_library

Benchmark documentation library.

#### _benchmark_integration

Benchmark cross-library integration.

#### _benchmark_system

Benchmark overall system performance.

#### validate_migration_path

Validate migration path from source to target.

Args:
    source: Source version or path
    target: Target version or path

Returns:
    Migration validation result

#### validate_backward_compatibility

Validate backward compatibility.

Args:
    source: Source version
    target: Target version

Returns:
    Backward compatibility validation result

#### validate_data_integrity

Validate data integrity during migration.

Args:
    source: Source version
    target: Target version

Returns:
    Data integrity validation result

#### _validate_source

Validate source version or path.

#### _validate_target

Validate target version or path.

#### _validate_compatibility

Validate compatibility between source and target.

#### _validate_data_integrity

Validate data integrity during migration.

#### _validate_rollback_capability

Validate rollback capability.

#### _check_api_compatibility

Check API compatibility.

#### _check_data_format_compatibility

Check data format compatibility.

#### _check_configuration_compatibility

Check configuration compatibility.

#### _check_data_format_integrity

Check data format integrity.

#### _check_data_completeness

Check data completeness.

#### _check_data_consistency

Check data consistency.

#### validate_all_libraries

Validate all pheno-sdk libraries.

Returns:
    List of validation results

#### validate_library

Validate a specific library.

Args:
    library_name: Name of the library to validate

Returns:
    Validation result

#### validate_cross_library_integration

Validate cross-library integration.

Returns:
    Validation result

#### validate_performance

Validate performance across all libraries.

Returns:
    Validation result

#### validate_migration_paths

Validate migration paths.

Returns:
    Validation result

#### add_test

Add an integration test.

#### run_test

Run a specific integration test.

Args:
    test_name: Name of the test to run

Returns:
    Validation result

#### run_all_tests

Run all integration tests.

Returns:
    List of validation results

#### _validate_library

Validate a specific library.

#### _validate_cross_library_integration

Validate cross-library integration.

#### _validate_performance

Validate performance across all libraries.

#### _validate_migration_paths

Validate migration paths.

#### _run_single_test

Run a single integration test.

#### _library_exists

Check if library exists.

#### _library_importable

Check if library can be imported.

#### _validate_library_structure

Validate library structure.

#### _validate_library_interfaces

Validate library interfaces.

#### _validate_library_configuration

Validate library configuration.

#### _test_auth_config_integration

Test auth-config integration.

#### _test_logging_error_integration

Test logging-error integration.

#### _test_testing_docs_integration

Test testing-docs integration.

#### _test_config_logging_integration

Test config-logging integration.

#### _test_memory_usage

Test memory usage.

#### _test_response_time

Test response time.

#### _test_throughput

Test throughput.

#### _test_backward_compatibility

Test backward compatibility.

#### _test_data_integrity

Test data integrity.

#### _test_rollback_capability

Test rollback capability.

#### run_comprehensive_validation

Run comprehensive validation suite.

Returns:
    Comprehensive validation results

#### _validate_all_libraries

Validate all individual libraries.

#### _validate_security

Validate security patterns.

#### _validate_usability

Validate usability across all libraries.

#### _generate_validation_summary

Generate validation summary.

#### _calculate_basic_stats

Calculate basic statistics for all results.

#### _categorize_tests

Categorize tests by type.

#### _calculate_category_stats

Calculate statistics for each test category.

#### _calculate_category_statistics

Calculate statistics for a single category of tests.

#### _calculate_overall_status

Calculate overall validation status.

#### _test_auth_security

Test authentication security.

#### _test_config_security

Test configuration security.

#### _test_data_security

Test data security.

#### _test_api_consistency

Test API consistency.

#### _test_docs_quality

Test documentation quality.

#### _test_error_messages

Test error message clarity.

#### generate_integration_report

Generate integration validation report.

Args:
    validation_results: List of validation results

Returns:
    Path to generated report

#### generate_performance_report

Generate performance benchmark report.

Args:
    benchmark_results: List of benchmark results

Returns:
    Path to generated report

#### generate_migration_report

Generate migration validation report.

Args:
    migration_results: List of migration results

Returns:
    Path to generated report

#### generate_comprehensive_report

Generate comprehensive report combining all results.

Args:
    validation_results: List of validation results
    benchmark_results: List of benchmark results
    migration_results: List of migration results

Returns:
    Path to generated report

#### get_reports

Get all generated reports.

#### _generate_html_report

Generate HTML report for validation results.

#### _generate_json_report

Generate JSON report for validation results.

#### _generate_markdown_report

Generate Markdown report for validation results.

#### _build_markdown_header

Build the markdown report header.

#### _build_markdown_summary

Build the markdown summary section.

#### _build_markdown_test_results

Build the markdown test results section.

#### _build_markdown_test_result

Build markdown for a single test result.

#### _get_status_emoji

Get emoji for test status.

#### _generate_html_performance_report

Generate HTML performance report.

#### _generate_json_performance_report

Generate JSON performance report.

#### _generate_markdown_performance_report

Generate Markdown performance report.

#### _generate_html_migration_report

Generate HTML migration report.

#### _generate_json_migration_report

Generate JSON migration report.

#### _generate_markdown_migration_report

Generate Markdown migration report.

#### _generate_html_comprehensive_report

Generate HTML comprehensive report.

#### _generate_json_comprehensive_report

Generate JSON comprehensive report.

#### _generate_markdown_comprehensive_report

Generate Markdown comprehensive report.

#### validate_token

Validate and decode a JWT token.

#### get_user



#### from_

Query table with RLS.

#### select



#### limit



#### single



#### order



#### range



#### _match



#### register_user



#### decode_token

Decode JWT token without verification.

Args:
    token: JWT token string

Returns:
    Decoded token claims

#### get_authorization_url

Get OAuth authorization URL.

#### get_mfa_type

Get the MFA type this provider handles.

#### has_role

Check if user has a specific role.

#### has_permission

Check if user has a specific permission.

#### has_mfa_type

Check if user has MFA of specific type enabled.

#### time_until_expiry

Get seconds until expiry.

#### extend

Extend session by specified minutes.

#### register_mfa_provider

Register an MFA provider.

#### set_session_provider

Set the session provider.

#### get_oauth_provider

Get OAuth provider.

#### create_oauth_state

Create OAuth state for CSRF protection.

#### validate_oauth_state

Validate OAuth state.

#### get_oauth_authorization_url

Get OAuth authorization URL.

#### filesystem

Create filesystem storage.

Args:
    path: Path to session file

Returns:
    FilesystemStorage instance

#### memory

Create in-memory storage (for testing).

Returns:
    MemoryStorage instance

#### check_memory_limit

Check if memory usage is within limits.

#### check_cpu_limit

Check if CPU usage is within limits.

#### check_file_descriptors

Check if file descriptor count is within limits.

#### check_process_count

Check if process count is within limits.

#### check_disk_usage

Check if disk usage is within limits.

#### enforce_limits

Enforce all resource limits.

#### get_cpu_usage

Get CPU usage information.

#### get_file_descriptor_count

Get file descriptor information.

#### get_process_count

Get process count information.

#### get_disk_usage

Get disk usage information.

#### remove_rule

Remove policy rule.

#### check_policy

Check policy for resource and action.

#### _matches_rule

Check if resource matches rule pattern.

#### create_policy

Create new policy.

#### get_policy

Get policy by name.

#### remove_policy

Remove policy.

#### check_permission

Check permission for path within sandbox.

#### require_permission

Require permission for path, raise exception if not granted.

#### check_multiple_permissions

Check multiple permissions for a path.

#### require_multiple_permissions

Require multiple permissions for path.

#### get_effective_permissions

Get all effective permissions for a path.

#### _check_user_group_access

Check if current user/group has access to path.

#### _check_filesystem_permission

Check file system level permissions.

#### _check_custom_permissions

Check custom permission mappings.

#### _get_current_user

Get current user name.

#### _get_current_groups

Get current user groups.

#### set_permission_mapping

Set permission mapping for a path pattern.

#### remove_permission_mapping

Remove permission mapping for a path pattern.

#### _setup_sandbox

Setup sandbox environment.

#### _cleanup_sandbox

Clean up sandbox context.

#### _restrict_imports

Restrict module imports.

#### _restore_modules

Restore original modules.

#### execute_safely

Execute function safely within sandbox.

#### validate_path

Validate a file path against security policies.

#### get_sandbox_info

Get information about sandbox state.

#### restricted_import



#### _compile_patterns

Compile regex patterns for performance.

#### sanitize_path

Sanitize a path to be safe for use.

#### is_safe_path

Check if a path is safe without raising exceptions.

#### _validate_basic

Basic path validation.

#### _check_traversal

Check for directory traversal attempts.

#### _check_patterns

Check path against allowed/blocked patterns.

#### _check_extensions

Check file extensions.

#### _check_base_directories

Check if path is within allowed base directories.

#### _remove_traversal_patterns

Remove traversal patterns from path.

#### _is_symlink

Check if path is a symlink.

#### _is_hidden

Check if path is hidden.

#### get_relative_path

Get relative path from base directory.

#### create_safe_path

Create a safe path by joining parts.

#### read_file

Read file securely.

#### write_file

Write file securely.

#### delete_file

Delete file securely.

#### list_directory

List directory contents securely.

#### create_directory

Create directory securely.

#### file_exists

Check if file exists securely.

#### get_file_size

Get file size securely.

#### copy_file

Copy file securely.

#### move_file

Move file securely.

#### get_sandbox_manager

Get the global sandbox manager instance.

#### secure_file_access

Context manager for secure file access.

#### validate_path_security

Validate path security using the global sandbox manager.

#### sandbox_execution

Context manager for sandboxed execution.

#### check_file_access

Check if file access is allowed.

#### check_time_limit

Check if execution time limit is exceeded.

#### get_usage_stats

Get current resource usage statistics.

#### create_sandbox

Create a sandboxed execution context.

#### validate_file_operation

Validate a file operation within the sandbox.

#### _log_operation

Log a file operation for audit trail.

#### secure_temp_file

Create a secure temporary file.

#### get_operation_history

Get operation history for monitoring.

#### generate_security_report

Generate a security summary.

#### _create_result

Convert ScanSummary to ScanResult.

#### create_baseline

Create suppression rules from current findings (baseline).

Args:
    findings: Findings to baseline

Returns:
    SuppressionRules that will suppress these findings

#### apply_suppressions



#### allows



#### _matches



#### _read_lines



#### run_detect_secrets



#### run_trufflehog



#### calculate_entropy



#### scan_entropy



#### _validate_api_contracts

Validate API contracts.

#### _validate_error_handling

Validate error handling patterns.

#### _validate_logging

Validate logging implementation.

#### _validate_monitoring

Validate monitoring integration.

#### _has_error_handling

Check if class has error handling.

#### _has_proper_exception_handling

Check if function has proper exception handling.

#### _has_proper_logging

Check if function has proper logging.

#### _has_sql_injection_risk

Check if function has SQL injection risk.

#### _has_metrics_collection

Check if function has metrics collection.

#### _validate_layered_architecture

Validate Layered Architecture.

#### _validate_domain_driven_design

Validate Domain-Driven Design patterns.

#### _validate_microservices_patterns

Validate Microservices patterns.

#### _has_shared_database_dependencies

Check if service has shared database dependencies.

#### _analyze_coverage

Analyze test coverage.

#### _analyze_complexity

Analyze code complexity.

#### _analyze_duplication

Analyze code duplication.

#### _detect_dead_code

Detect dead code.

#### _analyze_security

Analyze security issues.

#### _analyze_performance

Analyze performance issues.

#### _analyze_documentation

Analyze documentation coverage.

#### _functions_similar

Check if two functions are similar.

#### _get_nested_loop_depth

Get the depth of nested loops.

#### _detect_n_plus_one_queries

Detect N+1 query problems.

#### _detect_memory_leaks

Detect potential memory leaks.

#### _detect_blocking_calls

Detect blocking I/O calls.

#### _detect_inefficient_loops

Detect inefficient loop patterns.

#### _detect_excessive_io

Detect excessive I/O operations.

#### _loop_contains_database_queries

Check if loop contains database queries.

#### _function_creates_large_objects

Check if function creates large objects.

#### _count_io_operations

Count I/O operations in function.

#### _get_call_string

Get string representation of a function call.

#### _get_attr_string

Get string representation of an attribute.

#### _is_in_loop

Check if node is inside a loop.

#### _detect_god_object

Detect god objects.

#### _detect_feature_envy

Detect feature envy.

#### _detect_data_clump

Detect data clumps.

#### _detect_shotgun_surgery

Detect shotgun surgery.

#### _detect_divergent_change

Detect divergent change.

#### _detect_parallel_inheritance

Detect parallel inheritance.

#### _detect_lazy_class

Detect lazy classes.

#### _detect_inappropriate_intimacy

Detect inappropriate intimacy.

#### _detect_message_chain

Detect message chains.

#### _detect_middle_man

Detect middle man classes.

#### _detect_incomplete_library_class

Detect incomplete library class usage.

#### _detect_temporary_field

Detect temporary fields.

#### _detect_refused_bequest

Detect refused bequest.

#### _detect_alternative_classes

Detect alternative classes.

#### _detect_duplicate_code_blocks

Detect duplicate code blocks.

#### _get_chain_length

Get the length of a method call chain.

#### _detect_sql_injection

Detect SQL injection vulnerabilities.

#### _detect_xss_vulnerability

Detect XSS vulnerabilities.

#### _detect_insecure_deserialization

Detect insecure deserialization.

#### _detect_authentication_bypass

Detect authentication bypass vulnerabilities.

#### _detect_authorization_flaw

Detect authorization flaws.

#### _has_string_formatting

Check if call has string formatting.

#### _has_user_input

Check if call uses user input.

#### _has_proper_authentication

Check if function has proper authentication.

#### _has_proper_authorization

Check if function has proper authorization.

#### _detect_long_methods

Detect long methods.

#### _detect_large_classes

Detect large classes.

#### _detect_duplicate_code

Detect duplicate code.

#### _detect_magic_numbers

Detect magic numbers.

#### _detect_high_complexity

Detect high complexity methods.

#### with_email

Set the user email.

#### with_name

Set the service name.

#### with_environment

Set the deployment environment.

#### with_strategy

Set the deployment strategy.

#### for_production

Configure for production environment.

#### for_staging

Configure for staging environment.

#### for_development

Configure for development environment.

#### with_blue_green_strategy

Use blue-green deployment strategy.

#### with_rolling_strategy

Use rolling deployment strategy.

#### with_canary_strategy

Use canary deployment strategy.

#### with_port

Set the service port.

#### with_protocol

Set the service protocol.

#### with_http_protocol

Use HTTP protocol.

#### with_https_protocol

Use HTTPS protocol.

#### with_grpc_protocol

Use gRPC protocol.

#### with_tcp_protocol

Use TCP protocol.

#### as_http_service

Configure as HTTP service with defaults.

#### as_grpc_service

Configure as gRPC service with defaults.

#### with_key

Set the configuration key.

#### with_value

Set the configuration value.

#### with_description

Set the configuration description.

#### with_string_value

Set a string value.

#### with_int_value

Set an integer value.

#### with_bool_value

Set a boolean value.

#### with_float_value

Set a float value.

#### create_user_repository

Create a user repository.

Returns:
    User repository implementation

#### create_deployment_repository

Create a deployment repository.

Returns:
    Deployment repository implementation

#### create_service_repository

Create a service repository.

Returns:
    Service repository implementation

#### create_configuration_repository

Create a configuration repository.

Returns:
    Configuration repository implementation

#### create_all

Create all repositories.

Returns:
    Tuple of all repository implementations

#### create_deployment_use_case

Create a CreateDeploymentUseCase instance.

#### start_deployment_use_case

Create a StartDeploymentUseCase instance.

#### complete_deployment_use_case

Create a CompleteDeploymentUseCase instance.

#### fail_deployment_use_case

Create a FailDeploymentUseCase instance.

#### rollback_deployment_use_case

Create a RollbackDeploymentUseCase instance.

#### get_deployment_use_case

Create a GetDeploymentUseCase instance.

#### list_deployments_use_case

Create a ListDeploymentsUseCase instance.

#### create_service_use_case

Create a CreateServiceUseCase instance.

#### start_service_use_case

Create a StartServiceUseCase instance.

#### stop_service_use_case

Create a StopServiceUseCase instance.

#### get_service_use_case

Create a GetServiceUseCase instance.

#### list_services_use_case

Create a ListServicesUseCase instance.

#### create_configuration_use_case

Create a CreateConfigurationUseCase instance.

#### update_configuration_use_case

Create an UpdateConfigurationUseCase instance.

#### get_configuration_use_case

Create a GetConfigurationUseCase instance.

#### list_configurations_use_case

Create a ListConfigurationsUseCase instance.

#### create_from_dict

Create widget from dictionary specification.

#### create_production_deployment

Create a production deployment with default settings.

Args:
    strategy: Deployment strategy (default: blue_green)

Returns:
    Created deployment entity

#### create_staging_deployment

Create a staging deployment with default settings.

Args:
    strategy: Deployment strategy (default: rolling)

Returns:
    Created deployment entity

#### create_http_service

Create an HTTP service with default settings.

Args:
    name: Service name
    port: Service port (default: 8080)

Returns:
    Created service entity

#### create_grpc_service

Create a gRPC service with default settings.

Args:
    name: Service name
    port: Service port (default: 50051)

Returns:
    Created service entity

#### create_from_env

Create configurations from environment variables.

Args:
    prefix: Environment variable prefix (default: PHENO_)

Returns:
    List of created configuration entities

#### validate_field

Validate a specific field.

Args:
    dto: DTO being validated
    field_name: Name of the field
    value: Field value

Raises:
    ValidationError: If field validation fails

#### validate_business_rules

Validate business rules.

Args:
    dto: DTO to validate

Raises:
    ValidationError: If business rules are violated

#### validate_uuid

Validate UUID format.

#### validate_positive_number

Validate positive number.

#### validate_non_empty_string

Validate non-empty string.

#### validate_enum_value

Validate enum value.

#### validate_length

Validate string length.

#### handle_validation_error

Handle Pydantic validation error.

Args:
    error: Pydantic validation error

Returns:
    Domain exception

#### handle_business_rule_error

Handle business rule validation error.

Args:
    error: Business rule validation error

Returns:
    Domain exception

#### handle_field_error

Handle field validation error.

Args:
    field_name: Name of the field
    error: Field validation error

Returns:
    Domain exception

#### add_dto_validator

Add DTO validator.

#### add_business_rule_validator

Add business rule validator.

#### remove_dto_validator

Remove DTO validator.

#### remove_business_rule_validator

Remove business rule validator.

#### entity_to_dto

Convert entity to DTO.

#### dto_to_entity

Convert DTO to entity.

#### entities_to_dtos

Convert entities to DTOs.

#### dtos_to_entities

Convert DTOs to entities.

#### update_entity_from_dto

Update entity from DTO.

#### _get_entity_field

Get entity field name from DTO field name.

#### _convert_value

Convert value for mapping.

#### entity_to_event

Convert entity to event.

#### _extract_entity_event_data

Extract event-specific data from entity.

Override in subclasses for custom event data extraction.

#### create_use_cases

Create all use cases for the entity.

#### create_routes

Create all routes for the entity.

#### create_dependencies

Create dependency injection functions.

#### create_all_use_cases

Create all use cases.

#### create_use_case

Create use case.

#### update_use_case

Create update use case.

#### get_use_case

Create get use case.

#### list_use_case

Create list use case.

#### delete_use_case

Create delete use case.

#### add_routes

Add all routes to the router.

#### create_repository

Create a repository with standard methods.

#### get_create_use_case



#### get_update_use_case



#### get_get_use_case



#### get_list_use_case



#### get_delete_use_case



#### _create_entity_from_dto

Create entity from create DTO.

#### _update_entity_from_dto

Update entity from update DTO.

#### _get_entity_id_from_dto

Get entity ID from update DTO.

#### _get_not_found_exception

Get the not found exception for this entity type.

#### _to_dto

Convert entity to response DTO.

#### use_case

Decorator for use case methods.

Provides:
- Execution logging
- Error handling
- Event publishing
- Performance monitoring

Args:
    entity_name: Name of the entity (e.g., "User", "Deployment")
    operation: Operation name (e.g., "create", "update", "get")
    log_execution: Whether to log execution details
    publish_events: Whether to publish events

#### crud_route

Decorator for CRUD API routes.

Provides:
- Standard error handling
- HTTP status code mapping
- Request/response logging
- OpenAPI documentation

Args:
    entity_name: Name of the entity
    operation: Operation name
    success_status: HTTP status code for success
    error_mapping: Mapping of exceptions to HTTP status codes

#### validate_dto

Decorator for DTO validation.

Provides:
- Pydantic validation
- Business rule validation
- Validation error handling

Args:
    dto_type: DTO type to validate
    validate_business_rules: Whether to validate business rules

#### _find_dto_parameter

Find DTO parameter in function signature and get its value.

#### _validate_dto_instance

Validate and convert DTO instance.

#### _validate_business_rules

Validate business rules if requested.

#### _replace_dto_in_arguments

Replace DTO in function arguments.

#### handle_errors

Decorator for error handling.

Provides:
- Custom error mapping
- Standard error responses
- Error logging

Args:
    error_mapping: Mapping of exceptions to HTTP exceptions
    default_status: Default HTTP status code

#### publish_events

Decorator for event publishing.

Provides:
- Automatic event publishing
- Event type filtering
- Event publishing error handling

Args:
    event_publisher: Event publisher instance
    event_types: List of event types to publish (None for all)

#### health



#### _is_expired

Check if a cache entry has expired.

#### _record_metric

Record a metric for an operation.

#### _read_dotenv_values

Read dotenv values from .env file.

#### _compute_force_override

Compute if force override is enabled.

#### reload_env



#### env_override_enabled



#### get_all_env

Expose the loaded .env mapping for diagnostics/logging.

#### suppress_env_vars

Temporarily remove environment variables during the context.

Args:
    names: Environment variable names to remove. Empty or falsy names are ignored.

#### get_restriction_service

Get the global restriction service instance.

#### _load_from_env

Load restrictions from environment variables.

#### is_allowed

Check if a model is allowed for a given provider.

Args:
    provider_type: The provider type
    model_name: The model name to check

Returns:
    True if the model is allowed, False otherwise

#### filter_models

Filter a list of models to only those allowed for the provider.

Args:
    provider_type: The provider type
    models: List of model names to filter

Returns:
    List of allowed model names

#### get_restricted_models

Get the set of restricted (allowed) models for a provider.

Args:
    provider_type: The provider type

Returns:
    Set of allowed model names, or empty set if no restrictions

#### has_restrictions

Check if there are any restrictions for a provider.

Args:
    provider_type: The provider type

Returns:
    True if there are restrictions, False otherwise

#### _create_provider_instance



#### get_providers_by_priority



#### clear_instances



#### get_with_metadata



#### load_entry_points



#### create_adapter_instance



#### resolve_adapter



#### resolve_many



#### get_adapter_types



#### get_adapters_by_priority



#### register_callback



#### trigger_callbacks



#### autodiscover



#### _instance_key



#### default_model_field_schema



#### build_schema

Build a full JSON schema for a tool.

Args:
    tool_specific_fields: Fields unique to the tool
    required_fields: Names that must be present in input
    model_field_schema: Custom model field schema (defaults to common)
    auto_mode: When True, include a model field but do not require it
    include_common_defaults: Whether to include temperature/thinking_mode/images/continuation_id

#### model_dump_json



#### Field



#### for_model

Create capabilities for a specific model using heuristics.

#### supports_temperature

Check if the model supports temperature tuning.

#### create_temperature_constraint

Create the appropriate temperature constraint for a model.

#### get_corrected_value



#### get_default



#### infer_support

Heuristically determine whether a model supports temperature.

#### get_annotations

Return tool annotations. Simple tools are read-only by default.

All simple tools perform operations without modifying the environment.
They may call external AI models for analysis or conversation, but they
don't write files or make system changes.

Override this method if your simple tool needs different annotations.

Returns:
    Dictionary with readOnlyHint set to True

#### is_effective_auto_mode

Check if we're in effective auto mode for schema generation.

#### get_default_thinking_mode

Return the default thinking mode.

#### get_language_instruction

Return the language instruction prompt.

#### _augment_system_prompt_with_capabilities

Add capability-specific instructions to the system prompt.

#### validate_and_correct_temperature

Validate and correct temperature for the specified model.

#### _validate_image_limits

Validate image size and count against model capabilities.

#### _build_model_unavailable_message

Build message for when a model is not available.

#### get_request_model_name

Get model name from request.

Override for custom model name handling.

#### get_request_images

Get images from request.

Override for custom image handling.

#### get_request_continuation_id

Get continuation_id from request.

Override for custom continuation handling.

#### get_request_prompt

Get prompt from request.

Override for custom prompt handling.

#### get_request_temperature

Get temperature from request.

Override for custom temperature handling.

#### get_request_thinking_mode

Get thinking_mode from request.

Override for custom thinking mode handling.

#### get_request_files

Get files from request.

Override for custom file handling.

#### _validate_file_paths

Validate that all file paths in the request are absolute paths.

This is a security measure to prevent path traversal attacks and ensure
proper access control. All file paths must be absolute (starting with '/').

Args:
    request: The validated request object

Returns:
    Optional[str]: Error message if validation fails, None if all paths are valid

#### _parse_response

Parse the raw response and format it using the hook method.

This simplified version focuses on the SimpleTool pattern: format the response
using the format_response hook, then handle conversation continuation.

#### _create_continuation_offer

Create continuation offer following old base.py pattern.

#### _create_continuation_offer_response

Create response with continuation offer following old base.py pattern.

#### _record_assistant_turn

Persist an assistant response in conversation memory.

#### build_standard_prompt

Build a standard prompt with system prompt, user content, and optional files.

This is a convenience method that handles the common pattern of:
1. Adding file content if present
2. Checking token limits
3. Adding web search instructions
4. Combining everything into a well-formatted prompt

Args:
    system_prompt: The system prompt for the tool
    user_content: The main user request/content
    request: The validated request object
    file_context_title: Title for the file context section

Returns:
    Complete formatted prompt ready for the AI model

#### get_prompt_content_for_size_validation

Override to use original user prompt for size validation when conversation
history is embedded.

When server.py embeds conversation history into the prompt field, it also stores
the original user prompt in _original_user_prompt. We use that for size validation
to avoid incorrectly triggering size limits due to conversation history.

Args:
    user_content: The user content (may include conversation history)

Returns:
    The original user prompt if available, otherwise the full user content

#### get_websearch_guidance

Return tool-specific web search guidance.

Override this to provide tool-specific guidance for when web searches
would be helpful. Return None to use the default guidance.

Returns:
    Tool-specific web search guidance or None for default

#### handle_prompt_file_with_fallback

Handle prompt.txt files with fallback to request field.

This is a convenience method for tools that accept prompts either
as a field or as a prompt.txt file. It handles the extraction
and validation automatically.

Args:
    request: The validated request object

Returns:
    The effective prompt content

Raises:
    ValueError: If prompt is too large for MCP transport

#### get_chat_style_websearch_guidance

Get Chat tool-style web search guidance.

Returns web search guidance that matches the original Chat tool pattern.
This is useful for tools that want to maintain the same search behavior.

Returns:
    Web search guidance text

#### prepare_chat_style_prompt

Prepare a prompt using Chat tool-style patterns.

This convenience method replicates the Chat tool's prompt preparation logic:
1. Handle prompt.txt file if present
2. Add file context with specific formatting
3. Add web search guidance
4. Format with system prompt

Args:
    request: The validated request object
    system_prompt: System prompt to use (uses get_system_prompt() if None)

Returns:
    Complete formatted prompt

#### get_required_fields

Return list of required field names.

Override this to specify which fields are required for your tool.
The model field is automatically added if in auto mode.

Returns:
    List of required field names

#### format_response

Format the AI response before returning to the client.

This is a hook method that subclasses can override to customize
response formatting. The default implementation returns the response as-is.

Args:
    response: The raw response from the AI model
    request: The validated request object
    model_info: Optional model information dictionary

Returns:
    Formatted response string

#### get_validated_temperature

Get temperature from request and validate it against model constraints.

This is a convenience method that combines temperature extraction and validation
for simple tools. It ensures temperature is within valid range for the model.

Args:
    request: The request object containing temperature
    model_context: Model context object containing model info

Returns:
    Tuple of (validated_temperature, warning_messages)

#### get_request_as_dict

Convert request to dictionary.

Override for custom serialization.

#### set_request_files

Set files on request.

Override for custom file setting.

#### supports_custom_request_model

Indicate whether this tool supports custom request models.

Simple tools support custom request models by default. Tools that override
get_request_model() to return something other than ToolRequest should
return True here.

Returns:
    True if the tool uses a custom request model

#### get_actually_processed_files

Get actually processed files.

Override for custom file tracking.

#### _request



#### add_upstream

Register an upstream service.

#### remove_upstream



#### list_upstreams

Return a list of upstream metadata for admin APIs.

#### deregister_tenant

Remove upstreams associated with a tenant or explicit prefixes.

#### get_inline_error_page



#### render_logs_html



#### delete_status



#### list_status



#### set_service_state



#### should_show_loading



#### register_health_check



#### unregister_health_check

Unregister a health check for a service if it exists.

#### load_template



#### _get_fallback_html



#### create_middleware



#### enable



#### disable



#### _get_status_color

Get color for status indicator.

#### _get_status_icon



#### _get_environment_badge



#### _format_bytes



#### generate_routes_html



#### generate_health_checks_html



#### generate_metrics_html



#### generate_links_html



#### build_status_page_html



#### generate_html



#### generate_json



#### get_fallback_port

Get the fallback port for this project.

#### get_proxy_port

Get the proxy port for this project.

#### _load_config

Load configuration from disk.

#### _create_default_config

Create default configuration with common pheno-sdk projects.

#### _load_runtime_state

Load runtime state from disk.

#### _save_runtime_state

Save runtime state to disk.

#### get_startup_order

Get project startup order respecting dependencies.

#### update_runtime_state

Update runtime state for a project.

#### get_runtime_state

Get runtime state for a project.

#### has_cycle



#### _handle_monitor_event

Handle events from the monitor engine.

#### attach_project_monitor

Attach an existing project monitor.

#### detach_project_monitor

Detach a project monitor.

#### _stream_output

Stream output from a process in a background thread.

#### _process_stream_lines

Process lines from the stream.

#### _store_output_line

Store output line in the result with size management.

#### _notify_output_callbacks

Notify all output callbacks about the new line.

#### _monitor_processes

Monitor active processes for completion.

#### is_command_running

Check if a command is still running.

#### terminate_command

Terminate a running command.

Args:
    command_id: Command to terminate
    timeout: Grace period before killing

Returns:
    True if successfully terminated

#### get_active_commands

Get list of currently active command IDs.

#### performance_score

Calculated performance score (lower is better).

#### start_command_tracking

Start tracking a command execution.

Args:
    command_id: Unique command identifier
    command: Command being executed
    project_name: Associated project name

#### update_command_tracking

Update tracking data for a command.

Args:
    command_id: Command identifier
    **updates: Fields to update (end_time, exit_code, etc.)

#### finish_command_tracking

Finish tracking a command and calculate final metrics.

Args:
    command_id: Command identifier

Returns:
    Final command metrics

#### get_command_metrics

Get metrics for a specific command.

#### get_performance_stats

Get performance statistics.

Args:
    project_name: Filter by project name
    command_filter: Filter by command pattern

Returns:
    Performance statistics dictionary

#### add_metrics_callback

Add callback for metrics events.

Args:
    callback: Function called with (event_type, data)

#### _update_performance_stats

Update aggregated performance statistics.

#### _cleanup_old_metrics

Remove old metrics to maintain history limit.

#### register_process

Register a process for monitoring.

#### unregister_process

Unregister a process from monitoring.

#### get_resource

Get resource information.

#### get_all_projects

Get all monitored project names.

#### _cleanup_old_logs

Remove log entries older than retention period.

#### register_project_context

Register context for a project.

Args:
    project_name: Project name
    working_dir: Working directory for commands
    env_vars: Environment variables
    cli_prefix: Default CLI prefix (e.g., ['atoms'])

#### get_project_commands

Get available commands for a project.

#### run_desktop_gui

Run the desktop GUI application.

#### _ensure_port_available

Ensure a port is available, incrementing if necessary.

#### _is_port_in_use

Check if a port is currently in use.

#### get_project_tunnels

Get all tunnels for a project.

#### get_project_fallback_port

Get fallback port for a project.

#### get_project_proxy_port

Get proxy port for a project.

#### get_tunnel_status



#### create_tunnel



#### create_quick_tunnel



#### create_persistent_tunnel



#### get_service_url



#### stop_all_tunnels



#### ensure_port_and_tunnel



#### get_info



#### get_service_info



#### cleanup_all



#### _cleanup_stale_processes

Best‑effort cleanup of stale processes from previous runs on startup.

#### cleanup_environment

Run comprehensive runtime cleanup, including stray cloudflared processes.

#### _cleanup_on_exit



#### _cleanup_on_signal



#### _matches_domain



#### _handle_json_request



#### _handle_html_request



#### update_routes



#### update_health_status



#### update_metrics

Update displayed metrics.

#### update_uptime



#### calculate_similarity



#### get_route_suggestions



#### generate_routes_table_html



#### generate_404_html



#### create_wildcard_handler



#### to_options

Convert config to gRPC options.

#### address

Get server address string.

#### add_interceptor

Add a client interceptor.

Note: Must be called before creating stubs for the interceptor to take effect.

#### intercept_unary_unary



#### intercept_service



#### create_channel

Create a gRPC channel with interceptors.

Args:
    target: Server address (host:port)
    interceptors: List of client interceptors
    config: Optional client configuration (created if not provided)

Returns:
    GrpcChannel instance ready to create stubs

Example:
    >>> from grpc_kit import create_channel
    >>> from grpc_kit.interceptors import ClientTelemetryInterceptor
    >>> from my_pb2_grpc import MyServiceStub
    >>>
    >>> channel = create_channel(
    ...     "localhost:50051",
    ...     interceptors=[ClientTelemetryInterceptor()],
    ... )
    >>>
    >>> stub = MyServiceStub(channel.channel)
    >>> response = await stub.MyMethod(request)
    >>>
    >>> await channel.close()

#### _create_channel

Create the underlying gRPC channel.

#### channel

Get the underlying gRPC channel.

#### warn



#### get_networking_config_from_env



#### allocate_free_port

Find an available port with smart fallback logic.

Mirrors legacy behavior from kinfra_networking.allocate_free_port.

#### try_bind



#### detect_framework



#### age_seconds

Process age in seconds.

#### start_monitoring

Start monitoring a process.

Args:
    pid: Process ID to monitor
    name: Process name (auto-detected if None)

Returns:
    ProcessMetrics object if successful, None otherwise

#### update_all_metrics

Update metrics for all monitored processes.

#### get_process_metrics

Get metrics for a specific process.

#### get_active_processes

Get list of currently active process IDs.

#### get_process_history

Get metrics history.

Args:
    pid: Filter by process ID
    event_type: Filter by event type

Returns:
    List of historical events

#### set_alert_thresholds

Set alert thresholds for resource usage.

#### _update_process_metrics

Update metrics for a process.

#### cleanup_stale_processes

Remove processes that are no longer running.

#### terminate_process

Safely terminate a process with graceful shutdown attempt.

First attempts graceful termination (SIGTERM), then force kills (SIGKILL)
if process doesn't terminate within the timeout.

Args:
    pid: Process ID to terminate
    timeout: Seconds to wait for graceful termination (default: 5.0)
    force_kill: Whether to force kill if graceful termination fails (default: True)

Returns:
    True if process was terminated successfully, False otherwise

Examples:
    >>> terminate_process(12345)
    True
    >>> terminate_process(12345, timeout=10.0, force_kill=False)
    False  # Process didn't terminate gracefully

#### cleanup_orphaned_processes

Terminate orphaned processes matching a pattern.

Useful for cleaning up stale cloudflared or other background processes
that were not properly terminated.

Args:
    grace_period: Seconds to wait after SIGTERM before SIGKILL (default: 3.0)
    force_kill: Whether to force kill stubborn processes (default: True)
    exclude_pids: Set of PIDs to exclude from cleanup (default: None)
    process_name_pattern: Process name pattern to match (default: "cloudflared")

Returns:
    Dictionary with cleanup statistics:
    - inspected: Total processes inspected
    - terminated: Processes terminated gracefully
    - force_killed: Processes force killed
    - skipped: Processes skipped (excluded)

Examples:
    >>> cleanup_orphaned_processes()
    {'inspected': 156, 'terminated': 2, 'force_killed': 0, 'skipped': 1}

    >>> cleanup_orphaned_processes(process_name_pattern="python")
    {'inspected': 156, 'terminated': 5, 'force_killed': 1, 'skipped': 2}

#### _build_trace_config

Return an aiohttp TraceConfig if the OTel instrumentation is available.

Uses opentelemetry.instrumentation.aiohttp_client.create_trace_config.
Returns None if unavailable.

#### apply_aiohttp_otel_kwargs

Merge OTel trace config into aiohttp.ClientSession kwargs if possible.

Example:
    session = aiohttp.ClientSession(**apply_aiohttp_otel_kwargs({"timeout": timeout}))

#### dns_safe_slug

Create a DNS-safe slug from a service name.

Converts strings to lowercase, replaces invalid characters with hyphens,
and ensures the result is a valid DNS label according to RFC 1123.

DNS label rules:
- Must start and end with alphanumeric character
- Can contain alphanumeric characters and hyphens
- Cannot contain consecutive hyphens
- Maximum 63 characters per label

Args:
    value: Input string to convert to DNS-safe slug
    default: Default value if input is empty or invalid (default: "local")

Returns:
    DNS-safe slug string

Examples:
    >>> dns_safe_slug("My Service Name")
    'my-service-name'
    >>> dns_safe_slug("api_v2.0")
    'api-v2-0'
    >>> dns_safe_slug("--invalid--")
    'invalid'
    >>> dns_safe_slug("")
    'local'
    >>> dns_safe_slug("CamelCaseService")
    'camelcaseservice'

#### validate_dns_label

Validate if a string is a valid DNS label according to RFC 1123.

Args:
    label: String to validate

Returns:
    True if valid DNS label, False otherwise

Examples:
    >>> validate_dns_label("my-service")
    True
    >>> validate_dns_label("-invalid")
    False
    >>> validate_dns_label("valid123")
    True
    >>> validate_dns_label("too--many--hyphens")
    True  # Actually valid, just unusual

#### create_subdomain

Create a full subdomain from service name and base domain.

Args:
    service_name: Service name to use as subdomain
    domain: Base domain
    max_levels: Maximum number of subdomain levels (default: 3)

Returns:
    Full subdomain string

Examples:
    >>> create_subdomain("api", "example.com")
    'api.example.com'
    >>> create_subdomain("my_service", "example.com")
    'my-service.example.com'
    >>> create_subdomain("test", "api.example.com", max_levels=4)
    'test.api.example.com'

#### extract_service_name_from_hostname

Extract service name from a hostname by taking the first label.

Args:
    hostname: Full hostname (e.g., "my-service.example.com")

Returns:
    Service name (first DNS label) or None if invalid

Examples:
    >>> extract_service_name_from_hostname("api.example.com")
    'api'
    >>> extract_service_name_from_hostname("my-service.example.com")
    'my-service'
    >>> extract_service_name_from_hostname("invalid")
    'invalid'

#### check_tcp_health

Check if a TCP port is accepting connections (synchronous).

Args:
    host: Host to check (default: "localhost")
    port: Port to check (default: 5432)
    timeout: Connection timeout in seconds (default: 2.0)

Returns:
    True if port is accepting connections, False otherwise

Examples:
    >>> check_tcp_health("localhost", 5432)
    True  # PostgreSQL is running
    >>> check_tcp_health("localhost", 9999)
    False  # Nothing listening on 9999

#### check_http_health

Check HTTP endpoint health (synchronous).

Args:
    url: Full URL to check (e.g., "http://localhost:8080/health")
    timeout: Request timeout in seconds (default: 2.0)
    expected_status: Expected HTTP status code (default: 200)
    method: HTTP method to use (default: "GET")

Returns:
    True if endpoint returns expected status, False otherwise

Examples:
    >>> check_http_health("http://localhost:8080/health")
    True
    >>> check_http_health("https://api.example.com/healthz", timeout=5.0)
    False  # Endpoint not reachable

#### check_tunnel_health

Check both local service and tunnel reachability.

Args:
    hostname: Tunnel hostname (e.g., "myapp.example.com")
    port: Local port the service is running on

Returns:
    Dictionary with health status:
    - local_service_up: bool
    - tunnel_reachable: bool
    - response_time_ms: Optional[int]

Examples:
    >>> check_tunnel_health("myapp.example.com", 8080)
    {'local_service_up': True, 'tunnel_reachable': True, 'response_time_ms': 245}

#### _load_pydevkit_httpx_hooks

Best-effort import of pydevkit's HTTPX OTel hooks.

Tries a few likely attribute names and returns a dict compatible with httpx's
event_hooks parameter: {"request": [callables], "response": [callables]}. Returns an
empty mapping on any failure.

#### apply_httpx_otel_event_hooks

Merge pydevkit's HTTPX OTel event hooks (if present) into client kwargs.

Example:
    async with httpx.AsyncClient(**apply_httpx_otel_event_hooks({})) as client:
        ...

#### _resolve_lsof

Resolve path to lsof binary.

Order:
- KINFRA_LSOF_PATH env var
- shutil.which("lsof")
- common path /usr/sbin/lsof if exists

#### is_port_free

Check if a port is free by attempting to bind to it.

Args:
    port: Port number to check
    host: Host address to bind to (default: '127.0.0.1')

Returns:
    True if port is free, False otherwise

Examples:
    >>> is_port_free(8080)
    True
    >>> is_port_free(80)  # May be in use
    False

#### get_port_occupant

Get information about process occupying a port.

Uses lsof (if available) for fast lookups, falls back to psutil scan.

Args:
    port: Port number to check

Returns:
    Dictionary with process information if found:
    - pid: Process ID
    - name: Process name
    - cmdline: Full command line
    - cwd: Current working directory (if available)
    - create_time: Process creation time

    None if no process found or permission denied.

Examples:
    >>> info = get_port_occupant(8080)
    >>> if info:
    ...     print(f"Port occupied by PID {info['pid']}: {info['name']}")

#### kill_processes_on_port

Kill all processes listening on a specific port.

Args:
    port: Port number to clear
    timeout: Timeout for graceful termination (default: 5.0)

Returns:
    True if any processes were killed, False otherwise

Examples:
    >>> kill_processes_on_port(8080)
    True  # Killed processes on port 8080
    >>> kill_processes_on_port(9999)
    False  # No processes on port 9999

#### _kill_via_lsof

Kill processes using lsof (fallback for permission issues).

Internal helper function.

#### _is_likely_our_cmd

Best-effort detection that a process belongs to our dev stack.

Uses simple substring checks; intentionally conservative to avoid terminating
unrelated processes.

#### free_port_if_likely_ours

If the given port is occupied by a same-project process, terminate it.

Uses PortRegistry to determine ownership. Only terminates when the occupying process
is registered to this project. Falls back to conservative heuristics if no registry
info is available.

Returns True if port is free after the attempt (either was free, or the occupant was
terminated successfully).

#### get_project_id

Return a stable project identifier.

Priority:
1) KINFRA_PROJECT_ID env var
2) Git repo root or working directory folder name
3) Provided default or "default"

#### stable_offset

Compute a small, deterministic offset for the given project id.

Defaults to modulo=50 to keep offsets in a compact range.

#### base_ports_from_env

Read base fallback/proxy ports from env if provided, else defaults.

#### _sanitize



#### pytest_tunnel_config



#### pytest_sync_tunnel_manager



#### pytest_async_tunnel_manager



#### register_sync_tunnel



#### register_async_tunnel



#### get_tunnel



#### list_tunnels



#### stop_all_sync_tunnels



#### cleanup_all_tunnels



#### cleanup_orphaned_cloudflared_processes



#### cleanup_runtime_environment



#### _signal_handler



#### _start_quick_tunnel



#### _start_persistent_tunnel



#### managed_tunnel



#### _find_cloudflared



#### _create_temp_config



#### _tunnel_log



#### _format_env



#### _emit_live_log

Emit a live log line to stdout to appear above the TUI.

ServiceManager owns the subprocess streams, so we stream here to avoid competing
readers and ensure live output regardless of monitor wiring.

#### _start_log_capture



#### _stop_log_capture



#### _blocking_tcp_check



#### setup_file_watching



#### on_modified



#### service_status



#### resources



#### resource_status



#### processes



#### file_observers



#### _monitor_tasks



#### _log_capture_tasks



#### _shutdown



#### update_status_running



#### update_status_error



#### _get_cloud_adapters



#### resource_from_dict

Convenience function to create resource from dict.

Args:
    name: Resource name
    config: Resource configuration

Returns:
    ResourceAdapter instance

Example:
    >>> pg = resource_from_dict("db", {
    ...     "type": "docker",
    ...     "image": "postgres:16",
    ...     "ports": {5432: 5432},
    ...     "environment": {"POSTGRES_PASSWORD": "pass"},
    ...     "health_check": {"type": "tcp", "port": 5432}
    ... })

#### create_many

Create multiple resources from a config dictionary.

Args:
    configs: Dict mapping resource names to their configurations

Returns:
    Dict of ResourceAdapter instances

Example:
    >>> resources = ResourceFactory.create_many({
    ...     "postgres": {"type": "docker", "image": "postgres:16", ...},
    ...     "redis": {"type": "docker", "image": "redis:7", ...}
    ... })

#### _get_auth_headers

Get authentication headers based on config.

#### get_state

Convenience proxy to :class:`ComponentStateStore.get`.

#### update_state

Merge multiple state values at once.

#### build_python_service

Build a ServiceConfig for a Python module service.

Args:
    options: Python service configuration options

Returns:
    ServiceConfig ready for KInfra orchestration

Example:
    >>> options = PythonServiceOptions(
    ...     name="atoms-mcp",
    ...     module="server",
    ...     port=50002,
    ...     enable_tunnel=True,
    ...     tunnel_domain="atomcp.kooshapari.com",
    ... )
    >>> service = build_python_service(options)

#### _setup_dns_route



#### _setup_dns_via_api



#### _setup_dns_via_cli



#### _generate_unified_config



#### _start_unified_tunnel_service



#### _unregister_unified_service



#### wait_for_ready



#### events



#### _get_event_queue



#### _emit



#### _wait_for_quick_url



#### _start_separate_tunnel



#### _create_tunnel



#### _update_tunnel_port



#### _find_existing_tunnel



#### _create_cloudflare_tunnel



#### _generate_tunnel_config



#### _stream_tunnel_pipe



#### _start_tunnel_process



#### _stop_tunnel_process



#### _is_tunnel_running



#### resolve_cloudflare_token

Resolve a Cloudflare API token from explicit value, env, or local files.

#### verify_cloudflared_setup

Ensure cloudflared binary and authentication are available.

#### ensure_dirs



#### determine_verbose



#### _log_tunnel



#### cleanup_all_unified_tunnels

Clean up all unified tunnels and related resources.

#### _stop_cloudflared_processes

Stop all running cloudflared processes.

#### _delete_existing_tunnels

Delete existing unified tunnels and return count of deleted tunnels.

#### _cleanup_dns_and_configs

Clean up DNS records and old configuration files.

#### _delete_cloudflared_tunnel



#### _stop_all_cloudflared_processes



#### _list_all_tunnels



#### _cleanup_old_configs



#### _cleanup_dns_records



#### _cleanup_dns_via_api



#### _get_zone_id



#### _configure_ssl_for_tunnels



#### get_mcp_endpoint

Get MCP endpoint URL for environment.

Args:
    environment: Environment name (prod/staging/dev/local)
                If None, auto-detects environment
    config: Configuration dictionary

Returns:
    str: MCP endpoint URL

#### _is_local_environment

Check if running in local environment.

#### get_mcp_config

Get complete MCP configuration for environment.

Args:
    environment: Environment name (prod/staging/dev/local)
                If None, auto-detects environment
    config: Configuration dictionary

Returns:
    dict: Complete MCP configuration

#### get_environment_display

Get human-readable environment display.

Returns:
    str: Formatted environment information

#### _get_default_mcp_config

Get default MCP configuration.

#### attach_process

Attach or update tracking for a service process.

#### detach_process

Detach a service from monitoring.

#### _start_log_readers

Start log streaming for all attached services.

#### _check_process_exits

Check for newly exited processes and report summaries.

#### clear_service

Remove buffer state for a detached service.

#### start_subprocess_streams

Spawn background readers for a subprocess' stdout/stderr.

#### _spawn_thread



#### start_async_streams

Attach asyncio readers for stdout/stderr streams.

#### cancel_async_tasks

Cancel any active asyncio log reader tasks.

#### get_buffer

Return the rolling buffer for a service, if present.

#### reader



#### set_overrides

Register optional override callbacks for status/pid resolution.

#### clear_overrides

Remove overrides for the supplied service.

#### get_pid

Return the PID for a monitored process, honoring overrides.

#### cloudflared_pid_for_port

Locate a cloudflared process bound to the provided localhost port.

#### _lookup_cloudflared_pid



#### check_port

Quick TCP port availability check.

#### build_status_panel



#### mongodb



#### mysql



#### custom_docker



#### systemd_service



#### custom_command



#### api_resource



#### supabase_project



#### render_service



#### aws_rds_instance



#### vercel_deployment



#### neon_database



#### railway_service



#### kubernetes_deployment



#### custom_api



#### redis



#### nats



#### get_connection_string

Get PostgreSQL connection string for the project.

#### _prepare_service_startup



#### _handle_startup_cancellation



#### _handle_startup_error



#### _start_watchers



#### _finalize_startup



#### _on_change



#### emit_stage



#### emit_status



#### emit_and_log



#### _publish_status



#### _init_control_center

Initialize control center components.

#### _init_ui

Initialize the user interface.

#### _create_menus

Create application menus.

#### _create_toolbar

Create application toolbar.

#### _create_status_bar

Create status bar.

#### _setup_system_tray

Setup system tray icon and menu.

#### _restore_settings

Restore application settings.

#### _save_settings

Save application settings.

#### showEvent

Handle show event.

#### closeEvent

Handle close event.

#### tray_icon_activated

Handle tray icon activation.

#### on_worker_finished

Handle async worker finished.

#### new_project

Create new project.

#### open_settings

Open settings dialog.

#### show_about

Show about dialog.

#### start_all_projects

Start all projects.

#### stop_all_projects

Stop all projects.

#### refresh_status

Manually refresh status.

#### toggle_project_launcher

Toggle project launcher visibility.

#### start_project

Handle start button click.

#### stop_project

Handle stop button click.

#### _create_project_tiles

Create tiles for all registered projects.

#### _add_project_tile

Add a project tile to the launcher.

#### _start_project

Start a project via CLI bridge.

#### _stop_project

Stop a project via CLI bridge.

#### _create_status_overview

Create status overview widget.

#### _create_process_table

Create process status table.

#### _create_resource_table

Create resource status table.

#### _create_log_display

Create log display area.

#### _update_process_table

Update the process status table.

#### _update_resource_table

Update the resource status table.

#### _create_global_status_widget

Create global status display widget.

#### _create_mt_status_widget

Create multi-tenant status display widget.

#### _update_global_status

Update global status tree.

#### _update_mt_status

Update multi-tenant status display.

#### _build_mt_status_text

Build the multi-tenant status text content.

#### _build_infrastructure_summary

Build infrastructure summary section.

#### _build_project_breakdown

Build project breakdown section.

#### _build_project_fallback_info

Build fallback server information for a project.

#### _build_project_proxy_info

Build proxy server information for a project.

#### _build_project_tunnel_info

Build tunnel information for a project.

#### run_desktop_app

Run the Pheno Control Center desktop application.

Args:
    config_dir: Optional configuration directory

Returns:
    Exit code (0 for success)

#### _create_tab_widget

Create and configure the tab widget.

#### _create_button_box

Create and configure the button box.

#### _create_basic_tab

Create basic settings tab.

#### _add_basic_fields

Add basic required fields to the layout.

#### _add_optional_fields

Add optional configuration fields to the layout.

#### _add_checkbox_fields

Add checkbox fields to the layout.

#### _create_advanced_tab

Create advanced settings tab.

#### _add_port_offset_fields

Add port offset configuration fields to the layout.

#### _add_working_directory_field

Add working directory field with browse button.

#### _add_dependencies_field

Add dependencies list with add/remove buttons.

#### _create_environment_tab

Create environment variables tab.

#### _browse_working_directory

Browse for working directory.

#### _add_dependency

Add a dependency to the list.

#### _remove_dependency

Remove selected dependency.

#### _populate_fields

Populate fields with existing project configuration.

#### _parse_cli_entry

Parse CLI entry from text field.

#### _parse_environment_variables

Parse environment variables from text area.

#### accept

Accept dialog and apply settings.

#### _create_general_tab

Create general settings tab.

#### _create_projects_tab

Create projects management tab.

#### _load_settings

Load current settings.

#### _refresh_projects_list

Refresh the projects list.

#### _add_project

Add a new project.

#### _edit_project

Edit selected project.

#### _remove_project

Remove selected project.

#### _apply_settings

Apply settings without closing dialog.

#### append_output

Append text to output area with optional color.

#### clear_output

Clear terminal output.

#### set_current_directory

Set current working directory.

#### set_shell

Set the shell to use for command execution.

#### _create_overview_tab

Create overview tab with system summary.

#### _create_details_tab

Create details tab with detailed information.

#### _create_logs_tab

Create logs tab with recent activity.

#### _start_refresh_timer

Start timer for automatic refresh.

#### _manual_refresh

Handle manual refresh.

#### _update_overview

Update overview tab.

#### _update_details

Update details tab with project information.

#### refresh_projects

Refresh the projects list.

#### on_project_selected

Handle project selection.

#### start_selected_project

Start the selected project.

#### stop_selected_project

Stop the selected project.

#### _update_project_actions

Update action button states.

#### _update_processes_tree

Update processes tree with status data.

#### _update_summary

Update system summary display.

#### _get_health_color

Get color for health indicator.

#### on_project_double_click

Handle project double click.

#### on_process_double_click

Handle process double click.

#### _render_steps



#### attach_service_manager

Bind a service manager for restart/stop actions.

#### set_page

Update the currently displayed fallback page metadata.

#### update_service_status

Update the status metadata for a service and mirror to the page config.

#### remove_services_with_prefix

Remove all services whose names share the provided prefix.

#### _register_routes

Configure aiohttp routes for public and admin endpoints.

#### remove_service

Remove a single tracked service by name.

#### as_status_payload

Return a serializable representation of the current status.

#### _normalize_fields



#### bind_service_manager

Attach a service manager after initialization.

#### _collect_manager_status



#### find_upstream

Locate the best matching upstream for a request path.

#### iter_upstreams

Iterate through registered upstreams.

#### _sorted_upstreams



#### _service_name



#### app

Expose the aiohttp application for external customization.

#### _configure_routes



#### set_service_starting



#### set_service_running



#### set_service_error



#### enable_maintenance



#### disable_maintenance



#### _register_health_check



#### _unregister_health_check



#### _filtered_headers



#### _inline_error_page



#### _require_session



#### _build_metadata



#### _extract_message



#### get_parser



#### _build_fallback_message

Derive a human friendly message when Gemini returns empty content.

#### create_clink_tool

Factory function to create a CLinkTool instance.

#### get_available_clis

Get list of available CLI clients.

#### get_available_roles

Get available roles for a specific CLI.

#### get_all_roles

Get all available roles across all CLIs.

#### get_default_cli

Get the default CLI name.

#### get_input_schema_info

Get schema information for building the MCP input schema.

Returns:
    Dictionary containing CLI names, role mappings, and defaults
    that can be used to build a proper MCP schema.

#### load_client_configs

Load and merge all CLI client JSON configs from a directory.

#### save_client_config

Save a client configuration to JSON file.

#### _recover_from_error



#### create_agent



#### _build_environment



#### bool



#### load_from_directory

Load migrations from a directory.

Args:
    directory: Path to migrations directory

#### _calculate_checksum

Calculate migration checksum.

Args:
    version: Migration version
    name: Migration name

Returns:
    Checksum hash

#### get_id

Get migration ID.

Returns:
    Migration ID (version_name)

#### get_pool_manager

Get the global connection pool manager instance.

#### get_provider_pool

Convenience function to get a pool for a specific provider.

Args:
    provider_name: Name of the provider (e.g., "openai", "anthropic")
    async_pool: If True, return AsyncConnectionPool
    config: Optional pool configuration

Returns:
    Connection pool for the provider

#### get_pool

Get or create a connection pool.

Args:
    pool_name: Unique name for the pool
    async_pool: If True, return AsyncConnectionPool, else SyncConnectionPool
    config: Optional configuration for the pool

Returns:
    Connection pool instance

#### list_pools

List all active pools.

#### _record_response_time

Record response time for statistics.

#### initialize

Initialize the connection pool.

#### list_subscriptions

List active subscription IDs (utility method).

#### get_subscription_info

Get info about a subscription (utility method).

#### _get_api_client

Get Neon API client for management operations.

#### _get_cached

Get cached result if still valid.

#### _set_cache

Cache result with timestamp.

#### _build_dsn

Build PostgreSQL DSN.

Args:
    host: Database host
    port: Database port
    database: Database name
    user: Database user
    password: Database password

Returns:
    DSN string

#### _apply_theme



#### create_tui_app



#### create_status_app



#### create_progress_app



#### create_log_viewer_app



#### invalidate_dependents

Invalidate all computed properties that depend on a given property.

Args:
    property_name: Name of the property that changed

#### reactive_property

Decorator for creating reactive properties.

Example:
    >>> class MyWidget:
    ...     @reactive_property(default=0, debounce=0.1)
    ...     def count(self):
    ...         return self._count

#### computed_property

Decorator for creating computed properties.

Example:
    >>> class MyWidget:
    ...     items = reactive_property(default=[])
    ...
    ...     @computed_property
    ...     def total_count(self):
    ...         return len(self.items)

#### create_reactive_proxy

Create a reactive proxy for an object with specified properties.

Args:
    obj: Object to proxy
    properties: List of property names to make reactive

Returns:
    Proxy object with reactive properties

#### _track_dependency

Track a dependency during computation.

#### start_tracking

Start tracking dependencies for a computation.

#### end_tracking

End tracking and store dependencies.

#### track_dependency

Track access to a reactive property.

#### clear_dependencies

Clear dependencies for a computation.

#### get_all_dependencies

Get all tracked dependencies.

#### __setattr__



#### create_example_config

Generate an example configuration YAML file.

#### _register_default_migrations

Seed the migration registry with built-in upgrades.

#### load_defaults

Populate defaults from :class:`ConfigSchema`.

#### load_user_config

Merge a user-level configuration file.

#### _merge_configs

Rebuild the merged configuration snapshot honoring precedence.

#### _deep_merge



#### get_all

Return a deep copy of the merged configuration.

#### switch_profile

Switch to ``profile`` and apply predefined overrides.

#### enable_hot_reload

Start watching the active config file for changes.

#### disable_hot_reload

Stop the file watcher if it is running.

#### _on_file_changed



#### export_schema

Write the JSON schema for the configuration to ``path``.

#### export_example

Write an example YAML configuration to ``path``.

#### __del__



#### migrate_1_0_to_1_1



#### validate_name



#### validate_backend



#### validate_level



#### validate_secret_key



#### _find_path

Return the shortest migration path via breadth-first search.

#### get_version_history

Return a sorted list of all known schema versions.

#### _initialize_state_containers

Initialize all state storage containers.

#### _initialize_locks_and_transactions

Initialize thread safety and transaction state.

#### _load_persisted_state

Load persisted state from file if available.

#### set_state

Proxy to :class:`ComponentStateStore.set` for ergonomic overrides.

#### transaction

Context manager for atomic state updates.

Usage:
    >>> with store.transaction() as tx:
    ...     store.set_state("user.name", "Bob")
    ...     store.set_state("user.age", 31)
    ...     # Changes applied atomically when context exits

#### undo

Undo the last state change.

Returns:
    True if undo was successful, False otherwise

#### redo

Redo the last undone state change.

Returns:
    True if redo was successful, False otherwise

#### persist_state

Persist current state to file.

Returns:
    True if successful, False otherwise

#### get_all_state

Get a copy of the entire state.

#### clear_state

Clear all state and history.

#### _get_nested_value

Get value from nested dictionary using dot notation.

#### _set_nested_value

Set value in nested dictionary using dot notation.

#### _delete_nested_value

Delete value from nested dictionary using dot notation.

#### _apply_change

Apply a state change and notify observers.

#### _notify_observers

Notify observers of state change.

#### _discover_reactive_properties

Discover reactive properties on the widget.

#### _on_property_changed

Handle reactive property changes.

#### refresh



#### enable_auto_refresh

Enable or disable automatic refresh on property changes.

#### get_reactive_properties

Get list of reactive property names.

#### _debounced_notify

Notify observers with debouncing.

#### __set_name__



#### get_change_history

Get the history of changes for this property.

#### draw_box

Draw a box with optional title.

Args:
    width: Box width
    height: Box height
    title: Optional title text
    style: Box style (single, double, heavy, rounded)

Returns:
    String representation of the box

#### draw_border

Draw a border around content.

Args:
    content: Content to wrap
    style: Box style
    title: Optional title
    padding: Padding around content

Returns:
    Content wrapped in border

#### get_charset

Get box drawing character set.

#### hex_to_rgb

Convert hex color to RGB tuple.

#### rgb_to_hex

Convert RGB to hex color.

#### darken

Darken color by amount (0-1).

#### lighten

Lighten color by amount (0-1).

#### is_light

Determine if color is light or dark.

#### contrast_color

Get contrasting color (black or white).

#### blend

Blend with another color.

#### get_shortcuts

Get global shortcuts instance.

#### register_shortcut

Register a global shortcut.

#### get_shortcut

Get shortcut by key.

#### get_all_categories

Get list of all categories.

#### get_help_text

Generate help text for all shortcuts.

#### add_cell

Add a cell to the grid.

#### remove_cell

Remove a cell from the grid.

#### update_cell

Update cell properties.

#### set_grid_size

Set grid dimensions.

#### clear_grid

Remove all cells from grid.

#### get_cell_at

Get cell at specific position.

#### get_cells

Get all cells.

#### set_gutter

Set grid gutter size.

#### add_tab

Add a new tab.

#### remove_tab

Remove a tab.

#### switch_to_tab

Switch to a specific tab.

#### get_tab

Get tab by ID.

#### get_active_tab

Get currently active tab.

#### update_tab

Update tab properties.

#### reorder_tabs

Reorder tabs.

#### add_tab_switch_callback

Add callback for tab switches (old_tab_id, new_tab_id).

#### add_tab_close_callback

Add callback for tab closures.

#### get_tab_ids

Get list of all tab IDs.

#### get_tab_count

Get number of tabs.

#### add_pane

Add a new pane to the layout.

#### remove_pane

Remove a pane from the layout.

#### set_ratio

Set the ratio for a specific pane.

#### set_ratios

Set ratios for all panes.

#### get_pane

Get pane widget by index.

#### swap_panes

Swap two panes.

#### get_widget_factory

Get global widget factory instance.

#### create_widget

Create widget by type name.

#### register_widget_type

Register a widget type.

#### register_creator

Register a custom widget creator function.

#### create_from_template

Create widget from registered template.

#### create_preset

Create widget from preset configuration.

#### get_theme_manager

Get global theme manager instance.

#### get_css

Generate CSS from theme.

#### register_theme

Register a theme.

#### unregister_theme

Unregister a theme.

#### set_theme

Set the current theme.

#### get_theme

Get theme by name (or current theme if None).

#### get_current_theme_name

Get current theme name.

#### list_themes

List available theme names.

#### create_custom_theme

Create a custom theme.

#### add_theme_callback

Add callback for theme changes.

#### remove_theme_callback

Remove theme callback.

#### formatted_time

Get formatted timestamp.

#### to_rich_text

Convert to Rich Text with optional highlighting.

#### _create_log_entry

Create a new log entry with timestamp.

#### _add_entry_to_storage

Add entry to storage and update counts.

#### _trim_entries_if_needed

Trim entries if they exceed maximum count.

#### _update_display_for_entry

Update display for a single entry.

#### _should_display

Check if entry should be displayed based on filters.

#### _display_entry

Display a single entry in the log.

#### _update_stats

Update statistics display.

#### set_filter_level

Set minimum log level to display.

#### set_search

Set search term.

#### toggle_auto_scroll

Toggle auto-scroll.

#### refresh_display

Refresh the entire display based on current filters.

#### export_to_file

Export logs to file.

#### get_entries

Get filtered log entries.

#### _create_field_widget

Create appropriate widget for field type.

#### handle_submit

Handle form submission.

#### handle_cancel

Handle form cancellation.

#### set_values

Set form values.

#### add_submit_callback

Add callback for form submission.

#### add_cancel_callback

Add callback for form cancellation.

#### add_child

Attach a child component to this component.

#### find_node

Find a node by label (recursive).

#### _build_tree

Build the tree structure from root node.

#### _add_children

Recursively add children to tree.

#### add_node

Add a node at the specified path.

#### remove_node

Remove a node at the specified path.

#### update_node

Update node properties.

#### expand_path

Expand nodes along a path.

#### collapse_path

Collapse a node.

#### find_nodes

Find all nodes matching a predicate.

#### get_selected_node

Get currently selected node.

#### on_tree_node_selected

Handle node selection.

#### add_selection_callback

Add callback for node selection.

#### create_status_dashboard

Factory function to create a status dashboard.

Args:
    oauth_client: OAuth client for token status monitoring
    server_client: Server client for connectivity monitoring
    update_interval: Status update interval in seconds

Returns:
    Configured StatusDashboard widget

#### run_status_dashboard_app

Run the status dashboard as a standalone application.

Args:
    oauth_client: OAuth client for monitoring
    server_client: Server client for monitoring

#### should_update

Check if widget should update based on interval.

#### mark_updated

Mark widget as recently updated.

#### _update_status

Update resource status.

#### get_current_status

Get current status of all widgets.

#### add_status_callback

Add callback to be called when status updates.

#### remove_status_callback

Remove status callback.

#### percent



#### eta_seconds



#### eta_formatted



#### duration_formatted

Get formatted duration string.

#### update_task

Update task progress.

#### complete_task

Mark task as complete.

#### _render_compact

Render compact progress view.

#### _render_detailed

Render detailed progress view.

#### get_task



#### get_all_tasks



#### get_running_tasks

Get currently running tasks.

#### clear_completed

Remove completed tasks.

#### status_color

Get status color based on thresholds.

#### get_historical_data

Get historical data for a metric.

#### set_thresholds

Set thresholds for a metric.

#### get_metric_status

Get status for a metric based on thresholds.

#### get_status_color

Get color for status.

#### generate_sparkline

Generate ASCII sparkline from data.

#### _update_historical_data

Update historical data for sparklines.

#### _update_task_metrics

Update task metrics for integration.

#### export_task_metrics

Export metrics for TaskMetrics integration.

#### update_content

Update panel content.

#### display_json

Display JSON data with formatting.

#### display_log

Display log output.

#### display_python

Display Python code.

#### display_yaml

Display YAML content.

#### display_markdown

Display Markdown content.

#### add_row

Add a single row.

#### remove_task

Remove a task.

#### generate_ascii_banner

Generate ASCII art banner from text.

Args:
    text: Text to convert to ASCII art
    style: Banner style (standard, box, double_box)
    color: Color for the banner

Returns:
    ASCII art string

Example:
    banner = generate_ascii_banner("ZEN", style="box", color="cyan")

#### add_value

Add a new value to history.

#### formatted_value

Get formatted current value.

#### trend

Calculate trend (up, down, stable).

#### get_sparkline



#### add_metric

Add a new metric to track.

#### update_metric

Update a metric value.

#### _create_table

Create and configure the metrics table.

#### _add_metric_rows

Add rows for all metrics to the table.

#### _build_metric_row

Build a single metric row.

#### _format_trend

Format trend column for a metric.

#### _format_sparkline

Format sparkline column for a metric.

#### _format_status

Format status column for a metric.

#### get_metric_value

Get current value of a metric.

#### get_metric_history

Get history for a metric.

#### set_success

Set success status.

#### set_warning

Set warning status.

#### set_info

Set info status.

#### set_starting

Set starting status.

#### set_checking

Set checking status.

#### get_health_history



#### get_latency_history



#### set_client_adapter



#### get_status_summary



#### _generate_sparkline



#### _create_progress



#### _update_task_progress

Update task progress (current value).

#### _update_task_status

Update task status and handle status transitions.

#### _handle_task_completion

Handle task completion (set end time and calculate duration).

#### _update_category_stats

Update category statistics based on task status.

#### _update_task_metadata

Update task metadata (description, metrics, error, etc.).

#### _refresh_display

Refresh the display with updated task information.

#### _create_display



#### elapsed_seconds



#### speed



#### throughput



#### elapsed_formatted



#### add_history_point



#### running



#### pass_rate



#### cache_hit_rate



#### build_category_panel



#### build_current_task_panel



#### build_statistics_panel



#### notify_sync

Synchronous notification (blocks until all observers called).

Args:
    old_value: Previous value
    new_value: New value
    **kwargs: Additional metadata passed to observers

#### _cleanup_dead_ref

Clean up dead weak reference.

#### observer_count

Get number of active observers.

#### invert

Create an inverted change for undo operations.

#### commit

Mark transaction as committed.

#### on_create

Invoked once after a component mounts and completes initialization.

#### on_destroy

Executed during teardown just before the component is unmounted.

#### on_show

Called when the component transitions from hidden to visible.

#### on_hide

Called when the component transitions from visible to hidden.

#### on_focus

Trigger fired when the component gains input focus.

#### on_blur

Trigger fired when the component loses input focus.

#### on_resize

React to layout recalculations that change the component's size.

#### on_move

Respond to positional changes in the layout.

#### handle_click

Process pointer click interactions.

#### handle_key

Process keyboard events such as key presses and releases.

#### handle_mouse

Process low-level mouse events (move, wheel, etc.).

#### handle_focus

Respond to focus events dispatched by the UI framework.

#### handle_blur

Respond to blur events dispatched by the UI framework.

#### subscribe_to_state

Register a callback that runs whenever a state key changes.

#### unsubscribe_from_state

Remove a previously registered state change callback.

#### has_plugin

Determine whether a plugin has been registered.

#### on_unmount

Lifecycle hook triggered before the component is removed.

#### create_component

Instantiate a component while forwarding constructor kwargs.

#### mount_component

Convenience helper that calls :meth:`BaseComponent.mount`.

#### unmount_component

Convenience helper that calls :meth:`BaseComponent.unmount`.

#### component_lifecycle

Context manager that mounts a component for the duration of the block.

#### mount

Transition the component into the mounted state and invoke hooks.

#### unmount

Gracefully tear down the component and trigger unmount hooks.

#### remove_child

Remove a previously attached child component.

#### emit_event

Emit an event synchronously through the global bus.

#### add_event_handler

Register an event handler for a specific event category.

#### remove_event_handler

Unregister a previously registered event handler.

#### from_base_color

Generate a complete palette from a base color.

#### get_color

Get color by name, falling back to the primary color.

#### add_theme

Add a theme to the engine.

#### _matches_selector

Check if selector matches element and context.

#### _apply_theme_colors

Apply theme colors to properties.

#### export_theme

Export theme as dictionary.

#### import_theme

Import theme from dictionary.

#### apply_high_contrast



#### apply_colorblind_support



#### apply_reduced_motion



#### __lt__



#### from_selector

Calculate specificity from CSS selector.

#### prevent_default

Mark the event as having its default action prevented.

#### stop_propagation

Stop further propagation after current handlers.

#### stop_immediate_propagation

Alias for stop_propagation to match DOM semantics.

#### detect_format



#### format_structured



#### highlight_urls



#### format_rich



#### write



#### capture_output



#### _append_line



#### _on_line_captured



#### _on_log_captured



#### get_lines



#### set_propagation_path

Set the ordered path for propagation (target last).

#### propagate_event

Dispatch an event through capture, target, and bubble phases.

#### __gt__



#### is_async

Return True when the wrapped handler is coroutine based.

#### get_global_event_bus

Return a process-wide event bus instance.

#### get_global_propagation

Return a global propagation helper bound to the global bus.

#### clear_handlers

Clear handlers for a given type or all handlers.

#### get_event_history

Return recent events, optionally filtered by type.

#### clear_event_history

Clear recorded history.

#### from_hex

Create RGB color from hex string.

#### to_hex

Convert to hex string.

#### to_hsl

Convert to HSL (hue, saturation, lightness).

#### from_hsl

Create RGB color from HSL values.

#### luminance

Calculate relative luminance according to WCAG.

Returns:
    float: Relative luminance (0-1)

#### contrast_ratio

Calculate WCAG contrast ratio between two colors.

Args:
    other: Color to compare against

Returns:
    float: Contrast ratio (1-21)

#### meets_wcag

Check if color meets WCAG contrast requirements.

Args:
    background: Background color
    level: WCAG level to check

Returns:
    bool: True if contrast meets requirements

#### saturate

Increase saturation by amount (0-1).

#### desaturate

Decrease saturation by amount (0-1).

#### rotate_hue

Rotate hue by degrees.

#### _channel_luminance



## 🧪 Testing

```bash
# Run kit-specific tests
pytest tests/pheno/

# Run with coverage
pytest tests/pheno/ --cov=src/pheno/pheno
```

## 📁 Structure

```
pheno/
├── __init__.py
├── core.py
├── utils.py
├── tests/
└── README.md
```

## 🔗 Related Kits

- [Core Kit](../core/README.md)
- [Utils Kit](../utils/README.md)

## 📝 Changelog

See the main [CHANGELOG.md](../../CHANGELOG.md) for changes.

---

*This documentation is automatically generated.*
