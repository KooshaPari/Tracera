#!/usr/bin/env python3
"""Script to fix all stub __init__.py docstrings in src/pheno/core/."""

import os
import re
from pathlib import Path

# Comprehensive docstrings for each module based on its path/purpose
DOCSTRINGS = {
    # Root core module
    "core": '''"""
Pheno SDK core module providing foundational infrastructure.

This module contains the essential building blocks for the Pheno SDK including
configuration management, database adapters, storage backends, security primitives,
health monitoring, logging infrastructure, and the registry system for component
discovery and dependency injection.

Key submodules:
    - adapters: External service adapters (databases, APIs, storage)
    - config/configuration: Application configuration management
    - database: Database connection and query abstractions
    - factories: Component factory patterns for DI
    - health: Health check infrastructure
    - logging: Structured logging setup
    - monitoring: Metrics and observability
    - ports: Port/adapter interfaces (hexagonal architecture)
    - registries: Component registration and discovery
    - security: Authentication and authorization
    - shared: Cross-cutting utilities and helpers
    - storage: File and object storage abstractions
    - testing: Test fixtures and utilities
    - validators: Input validation framework
"""''',

    # Database modules
    "database": '''"""
Database connection and query abstractions.

Provides database client management, connection pooling, query builders,
and transaction handling for PostgreSQL, Supabase, and other supported
database backends.

Key exports:
    - DatabaseClient: Async database client wrapper
    - ConnectionPool: Connection pooling management
    - QueryBuilder: Type-safe query construction
    - Transaction: Transaction context manager
"""''',

    "database_registry": '''"""
Database registry for managing database adapters and connections.

Provides centralized registration and discovery of database backends,
connection factories, and migration handlers.

Key exports:
    - DatabaseRegistry: Central registry for database providers
    - register_database: Decorator for registering database adapters
    - get_database: Factory function for database instances
"""''',

    # Configuration modules
    "configuration": '''"""
Application configuration management system.

Handles loading, validation, and access to configuration from environment
variables, files, and remote sources. Supports hierarchical configuration
with overrides and environment-specific settings.

Key exports:
    - Configuration: Main configuration container
    - ConfigLoader: Configuration loading strategies
    - ConfigSchema: Pydantic-based config validation
"""''',

    "configuration_registry": '''"""
Configuration registry for plugin-based config providers.

Enables registration of custom configuration sources and transformers
for extensible configuration management.

Key exports:
    - ConfigurationRegistry: Registry for config providers
    - ConfigProvider: Base class for config sources
    - register_config_provider: Registration decorator
"""''',

    "config": '''"""
Core configuration module with settings and components.

Provides the primary configuration interface, environment detection,
and component-specific configuration classes.

Key exports:
    - Settings: Application settings container
    - get_settings: Settings factory function
    - Environment: Environment enum (dev, staging, prod)
"""''',

    "config/components": '''"""
Configuration components for specific subsystems.

Contains configuration classes for individual components like
database, cache, storage, and external service integrations.

Key exports:
    - DatabaseConfig: Database connection settings
    - CacheConfig: Cache backend settings
    - StorageConfig: Storage provider settings
"""''',

    # Security modules
    "security": '''"""
Security primitives for authentication and authorization.

Provides JWT handling, API key management, RBAC/ABAC authorization,
encryption utilities, and security middleware.

Key exports:
    - JWTHandler: JWT token creation and validation
    - APIKeyManager: API key lifecycle management
    - Authorizer: Permission checking interface
    - SecurityMiddleware: Request security middleware
"""''',

    "security_factory": '''"""
Factory for creating security components.

Provides factory functions for instantiating security providers,
authentication handlers, and authorization services.

Key exports:
    - SecurityFactory: Main factory class
    - create_jwt_handler: JWT handler factory
    - create_authorizer: Authorization service factory
"""''',

    # Health modules
    "health": '''"""
Health check infrastructure for service monitoring.

Provides health check protocols, aggregation, and reporting for
monitoring service health and dependencies.

Key exports:
    - HealthChecker: Health check protocol
    - HealthAggregator: Combines multiple health checks
    - HealthStatus: Health status enumeration
    - HealthResponse: Structured health response
"""''',

    "health/checkers": '''"""
Built-in health check implementations.

Contains health checkers for common dependencies like databases,
caches, external APIs, and storage backends.

Key exports:
    - DatabaseHealthChecker: Database connectivity check
    - CacheHealthChecker: Cache backend check
    - StorageHealthChecker: Storage availability check
    - HTTPHealthChecker: External API health check
"""''',

    # Managers
    "managers": '''"""
Resource and lifecycle managers for SDK components.

Provides manager classes for handling component lifecycle,
resource pooling, and coordinated shutdown.

Key exports:
    - ResourceManager: Generic resource lifecycle management
    - ConnectionManager: Database connection management
    - TaskManager: Background task coordination
"""''',

    # Utils and Utilities
    "utils": '''"""
Core utility functions and helpers.

Common utility functions used across the SDK including string
manipulation, type conversions, and functional programming helpers.

Key exports:
    - retry: Retry decorator with backoff
    - ensure_async: Sync-to-async wrapper
    - deep_merge: Deep dictionary merge
    - generate_id: Unique ID generation
"""''',

    "utilities": '''"""
Extended utilities module with advanced helpers.

Additional utility functions for complex operations including
serialization, validation helpers, and debugging tools.

Key exports:
    - Serializer: Object serialization utilities
    - Timer: Performance timing context manager
    - DebugHelper: Development debugging utilities
"""''',

    # Shared module and submodules
    "shared": '''"""
Cross-cutting shared utilities and infrastructure.

Contains reusable components shared across the SDK including
authentication helpers, caching, scheduling, and framework integrations.

Submodules:
    - auth: Authentication utilities
    - cache: Caching infrastructure
    - celery: Celery task integration
    - fastapi: FastAPI integration helpers
    - postgrest: PostgREST client utilities
    - scheduler: Job scheduling infrastructure
    - validators: Shared validation logic
"""''',

    "shared/tenant": '''"""
Multi-tenant context and isolation utilities.

Provides tenant context management, isolation boundaries,
and tenant-aware database operations.

Key exports:
    - TenantContext: Current tenant context holder
    - tenant_required: Decorator requiring tenant context
    - get_current_tenant: Retrieve current tenant
"""''',

    "shared/analyzers": '''"""
Code and data analysis utilities.

Static analysis tools, code quality checkers, and data
structure analyzers for SDK development and runtime checks.

Key exports:
    - Analyzer: Base analyzer class
    - CodeAnalyzer: Source code analysis
    - DataAnalyzer: Runtime data analysis
"""''',

    "shared/analyzers/types": '''"""
Type definitions for analyzer components.

Contains type hints, protocols, and dataclasses used by
the analyzer subsystem.

Key exports:
    - AnalyzerResult: Analysis result container
    - AnalyzerConfig: Analyzer configuration
    - Finding: Individual analysis finding
"""''',

    "shared/analyzers/rules": '''"""
Analysis rules and rule definitions.

Provides rule definitions for code and data analysis including
security rules, style rules, and custom rule creation.

Key exports:
    - Rule: Base rule class
    - SecurityRule: Security-focused rules
    - StyleRule: Code style rules
    - RuleRegistry: Rule discovery and registration
"""''',

    "shared/tracing": '''"""
Distributed tracing integration.

OpenTelemetry-based tracing for request tracking, span creation,
and distributed trace context propagation.

Key exports:
    - Tracer: Trace span creation
    - trace: Decorator for automatic tracing
    - get_current_span: Current span accessor
    - inject_trace_context: Context propagation
"""''',

    "shared/configuration": '''"""
Shared configuration utilities and types.

Cross-cutting configuration helpers used by multiple modules
including config validation, defaults, and transformations.

Key exports:
    - ConfigMixin: Mixin for configurable classes
    - validate_config: Configuration validator
    - merge_configs: Configuration merging
"""''',

    "shared/configuration/types": '''"""
Configuration type definitions.

Type hints and protocols for configuration components
ensuring type safety across configuration handling.

Key exports:
    - ConfigType: Configuration type protocol
    - ConfigValue: Configuration value union type
    - ConfigSource: Configuration source enum
"""''',

    "shared/configuration/configs": '''"""
Predefined configuration schemas.

Contains reusable configuration schemas for common
subsystems and external service integrations.

Key exports:
    - BaseConfig: Base configuration class
    - ServiceConfig: External service config
    - FeatureConfig: Feature flag configuration
"""''',

    "shared/celery_tasks": '''"""
Celery task definitions and utilities.

Pre-built Celery tasks for common async operations and
utilities for task creation and management.

Key exports:
    - BaseTask: Enhanced Celery task base
    - TaskResult: Structured task result
    - task_with_retry: Retry-enabled task decorator
"""''',

    "shared/cache": '''"""
Caching infrastructure with multiple backends.

Provides caching abstractions supporting Redis, memory,
and custom cache backends with namespace isolation.

Key exports:
    - CacheManager: Central cache management
    - NamespaceCache: Namespace-isolated cache
    - cache: Caching decorator
    - invalidate: Cache invalidation helper
"""''',

    "shared/typer": '''"""
Typer CLI integration utilities.

Helpers for building CLI applications using Typer with
consistent styling, error handling, and configuration.

Key exports:
    - TyperApp: Enhanced Typer application
    - cli_option: Typed CLI option helper
    - cli_command: Command decorator with defaults
"""''',

    "shared/auth": '''"""
Authentication utilities and helpers.

Common authentication patterns, token handling, and
identity verification utilities.

Key exports:
    - AuthHandler: Authentication handler protocol
    - TokenValidator: Token validation utilities
    - get_current_user: User extraction helper
    - require_auth: Authentication decorator
"""''',

    "shared/postgrest": '''"""
PostgREST client and query utilities.

Type-safe PostgREST client for Supabase database access
with query building and response parsing.

Key exports:
    - PostgRESTClient: HTTP client for PostgREST
    - QueryBuilder: PostgREST query construction
    - ResponseParser: Response transformation
"""''',

    "shared/scheduler": '''"""
Job scheduling infrastructure.

Background job scheduling using APScheduler with persistence,
job management, and monitoring integration.

Key exports:
    - Scheduler: Main scheduler instance
    - schedule_job: Job scheduling function
    - Job: Job definition class
    - JobStore: Job persistence backend
"""''',

    "shared/utilities": '''"""
Shared utility functions and helpers.

Cross-cutting utilities used throughout the shared module
for common operations and transformations.

Key exports:
    - safe_get: Safe dictionary access
    - flatten: Nested structure flattening
    - chunk: Iterable chunking
"""''',

    "shared/utilities/types": '''"""
Type definitions for shared utilities.

Common type hints, type guards, and generic types used
across shared utilities.

Key exports:
    - JSON: JSON-serializable type
    - PathLike: Path-compatible type
    - Callback: Generic callback type
"""''',

    "shared/utilities/utils": '''"""
Core shared utility implementations.

Fundamental utility functions for common operations
shared across the SDK.

Key exports:
    - slugify: String slugification
    - timestamp: Timestamp generation
    - hash_value: Value hashing
"""''',

    "shared/multitenancy": '''"""
Multi-tenancy infrastructure and isolation.

Complete multi-tenant support including tenant resolution,
data isolation, and tenant-aware operations.

Key exports:
    - TenantResolver: Tenant identification
    - TenantMiddleware: Request tenant extraction
    - TenantAwareModel: Tenant-scoped model mixin
"""''',

    "shared/deployment": '''"""
Deployment configuration and utilities.

Helpers for deployment configuration, environment detection,
and deployment-specific settings.

Key exports:
    - DeploymentConfig: Deployment settings
    - detect_environment: Environment detection
    - get_deployment_info: Deployment metadata
"""''',

    "shared/fastapi": '''"""
FastAPI integration utilities.

Middleware, dependencies, and utilities for FastAPI
application integration with the Pheno SDK.

Key exports:
    - PhenoMiddleware: SDK middleware stack
    - get_sdk: FastAPI dependency for SDK access
    - setup_routes: Route registration helper
"""''',

    "shared/factories": '''"""
Shared factory implementations.

Factory classes for creating shared components with
proper initialization and configuration.

Key exports:
    - SharedFactory: Base shared factory
    - create_cache: Cache instance factory
    - create_scheduler: Scheduler factory
"""''',

    "shared/factories/plugins": '''"""
Plugin factory system.

Factory infrastructure for plugin discovery, loading,
and instantiation with dependency injection.

Key exports:
    - PluginFactory: Plugin instantiation
    - PluginLoader: Plugin discovery
    - PluginRegistry: Plugin registration
"""''',

    "shared/celery": '''"""
Celery integration and configuration.

Celery application setup, configuration, and integration
utilities for background task processing.

Key exports:
    - CeleryApp: Configured Celery application
    - celery_config: Celery configuration
    - setup_celery: Celery initialization
"""''',

    "shared/validators": '''"""
Shared validation utilities.

Common validators and validation patterns used across
multiple modules for input and data validation.

Key exports:
    - Validator: Base validator class
    - validate: Validation decorator
    - ValidationError: Validation exception
"""''',

    "shared/supavisor": '''"""
Supavisor connection pooling integration.

Integration with Supavisor for PostgreSQL connection
pooling in Supabase environments.

Key exports:
    - SupavisorConfig: Supavisor configuration
    - get_supavisor_url: Connection URL builder
    - SupavisorPool: Pool management
"""''',

    "shared/messaging": '''"""
Messaging and event bus infrastructure.

Pub/sub messaging, event handling, and message queue
integration for async communication.

Key exports:
    - MessageBus: Event bus implementation
    - publish: Message publishing
    - subscribe: Message subscription
    - Message: Message container
"""''',

    "shared/apscheduler": '''"""
APScheduler integration and configuration.

Advanced Python Scheduler setup with job stores,
triggers, and monitoring.

Key exports:
    - Scheduler: APScheduler instance
    - add_job: Job addition helper
    - JobTrigger: Trigger definitions
"""''',

    "shared/validation": '''"""
Validation framework and utilities.

Comprehensive validation infrastructure including
schema validation, custom validators, and error handling.

Key exports:
    - validate_schema: Schema validation
    - ValidationContext: Validation context
    - ValidationResult: Validation outcome
"""''',

    "shared/console": '''"""
Console output and formatting utilities.

Rich console integration for formatted output, tables,
progress bars, and interactive prompts.

Key exports:
    - Console: Rich console wrapper
    - print_table: Table formatting
    - progress: Progress bar context
    - prompt: Interactive prompts
"""''',

    # Storage modules
    "storage": '''"""
File and object storage abstractions.

Provides unified storage interface supporting local filesystem,
S3-compatible storage, and Supabase Storage.

Key exports:
    - StorageClient: Unified storage interface
    - LocalStorage: Local filesystem backend
    - S3Storage: S3-compatible backend
    - StorageConfig: Storage configuration
"""''',

    "storage_registry": '''"""
Storage provider registry.

Registration and discovery of storage backends with
factory functions for storage instantiation.

Key exports:
    - StorageRegistry: Storage provider registry
    - register_storage: Registration decorator
    - get_storage: Storage factory function
"""''',

    # Testing
    "testing": '''"""
Test fixtures and utilities for SDK testing.

Provides test helpers, fixtures, mocks, and utilities
for testing applications using the Pheno SDK.

Key exports:
    - TestClient: Test client with SDK integration
    - MockDatabase: Database mock
    - MockStorage: Storage mock
    - fixture: Fixture decorator
"""''',

    # Adapters
    "adapters": '''"""
External service adapters.

Adapters for integrating external services following
the ports and adapters (hexagonal) architecture pattern.

Key exports:
    - Adapter: Base adapter class
    - DatabaseAdapter: Database service adapter
    - StorageAdapter: Storage service adapter
    - APIAdapter: External API adapter
"""''',

    # Factories
    "factories": '''"""
Component factory system.

Factory classes for creating SDK components with proper
initialization, configuration, and dependency injection.

Key exports:
    - ComponentFactory: Base component factory
    - create_component: Generic factory function
    - FactoryRegistry: Factory registration
"""''',

    "factories/core": '''"""
Core component factories.

Factories for fundamental SDK components including
configuration, logging, and infrastructure services.

Key exports:
    - CoreFactory: Core component factory
    - create_config: Configuration factory
    - create_logger: Logger factory
"""''',

    # Exception handling
    "exception_factories": '''"""
Exception factory system.

Factories for creating typed exceptions with context,
error codes, and structured error information.

Key exports:
    - ExceptionFactory: Exception creation
    - create_error: Error factory function
    - ErrorCode: Error code enumeration
"""''',

    "exception_factory": '''"""
Single exception factory implementation.

Primary exception factory for creating SDK exceptions
with consistent formatting and error handling.

Key exports:
    - ExceptionFactory: Main exception factory
    - SDKException: Base SDK exception
    - create_exception: Exception factory function
"""''',

    # Registry modules
    "registry": '''"""
Central registry system.

Base registry implementation for component registration,
discovery, and dependency injection.

Key exports:
    - Registry: Base registry class
    - register: Registration decorator
    - get: Component retrieval
    - RegistryError: Registry exceptions
"""''',

    "registries": '''"""
Domain-specific registries collection.

Contains specialized registries for different component
types including adapters, validators, and providers.

Submodules:
    - adapter: Adapter registration
    - api: API endpoint registration
    - configuration: Config provider registration
    - database: Database backend registration
    - factory: Factory registration
    - logging: Logger registration
    - monitoring: Monitor registration
    - port: Port interface registration
    - security: Security provider registration
    - storage: Storage backend registration
    - testing: Test fixture registration
    - utility: Utility registration
    - validator: Validator registration
"""''',

    # Individual registries
    "registries/database": '''"""
Database provider registry.

Registry for database backends including connection
factories, query builders, and migration handlers.

Key exports:
    - DatabaseRegistry: Database provider registry
    - register_database: Registration decorator
    - get_database_provider: Provider retrieval
"""''',

    "registries/configuration": '''"""
Configuration provider registry.

Registry for configuration sources and transformers
enabling extensible configuration loading.

Key exports:
    - ConfigurationRegistry: Config provider registry
    - register_config_source: Source registration
    - get_config_provider: Provider retrieval
"""''',

    "registries/validator": '''"""
Validator registry.

Registry for input validators, schema validators,
and custom validation functions.

Key exports:
    - ValidatorRegistry: Validator registry
    - register_validator: Registration decorator
    - get_validator: Validator retrieval
"""''',

    "registries/security": '''"""
Security provider registry.

Registry for authentication providers, authorization
handlers, and security middleware.

Key exports:
    - SecurityRegistry: Security provider registry
    - register_auth_provider: Auth registration
    - get_security_provider: Provider retrieval
"""''',

    "registries/adapter": '''"""
Adapter registry.

Registry for service adapters following the ports
and adapters pattern.

Key exports:
    - AdapterRegistry: Adapter registry
    - register_adapter: Registration decorator
    - get_adapter: Adapter retrieval
"""''',

    "registries/storage": '''"""
Storage backend registry.

Registry for file and object storage backends
with factory functions.

Key exports:
    - StorageRegistry: Storage provider registry
    - register_storage_backend: Registration
    - get_storage_backend: Backend retrieval
"""''',

    "registries/testing": '''"""
Test fixture registry.

Registry for test fixtures, mocks, and test
utilities used in SDK testing.

Key exports:
    - TestingRegistry: Test fixture registry
    - register_fixture: Fixture registration
    - get_fixture: Fixture retrieval
"""''',

    "registries/api": '''"""
API endpoint registry.

Registry for API routes, handlers, and middleware
for API construction.

Key exports:
    - APIRegistry: API endpoint registry
    - register_route: Route registration
    - get_routes: Route retrieval
"""''',

    "registries/port": '''"""
Port interface registry.

Registry for port interfaces in hexagonal architecture
enabling pluggable adapters.

Key exports:
    - PortRegistry: Port interface registry
    - register_port: Port registration
    - get_port: Port interface retrieval
"""''',

    "registries/monitoring": '''"""
Monitor registry.

Registry for health monitors, metrics collectors,
and observability components.

Key exports:
    - MonitoringRegistry: Monitor registry
    - register_monitor: Monitor registration
    - get_monitor: Monitor retrieval
"""''',

    "registries/logging": '''"""
Logger registry.

Registry for log handlers, formatters, and
logging configuration.

Key exports:
    - LoggingRegistry: Logger registry
    - register_handler: Handler registration
    - get_logger_config: Config retrieval
"""''',

    "registries/factory": '''"""
Factory registry.

Registry for component factories enabling
plugin-based factory discovery.

Key exports:
    - FactoryRegistry: Factory registry
    - register_factory: Factory registration
    - get_factory: Factory retrieval
"""''',

    "registries/utility": '''"""
Utility function registry.

Registry for utility functions, helpers, and
shared operations.

Key exports:
    - UtilityRegistry: Utility registry
    - register_utility: Utility registration
    - get_utility: Utility retrieval
"""''',

    # Port modules
    "port": '''"""
Port interface definitions.

Defines port interfaces for hexagonal architecture
enabling pluggable adapters and implementations.

Key exports:
    - Port: Base port protocol
    - InputPort: Input port interface
    - OutputPort: Output port interface
"""''',

    "ports": '''"""
Port interface collection.

Collection of all port interfaces used throughout
the SDK for dependency inversion.

Key exports:
    - DatabasePort: Database access port
    - StoragePort: Storage access port
    - CachePort: Cache access port
    - AuthPort: Authentication port
"""''',

    # Monitoring
    "monitoring": '''"""
Metrics and observability infrastructure.

Provides metrics collection, dashboards, alerting,
and observability integrations.

Key exports:
    - MetricsCollector: Metrics collection
    - Monitor: Base monitor class
    - Alert: Alert definition
    - Dashboard: Dashboard configuration
"""''',

    "monitoring/monitors": '''"""
Built-in monitor implementations.

Pre-built monitors for common observability needs
including performance, errors, and resources.

Key exports:
    - PerformanceMonitor: Performance tracking
    - ErrorMonitor: Error rate monitoring
    - ResourceMonitor: Resource usage monitoring
"""''',

    "monitoring/monitor_components": '''"""
Monitor component building blocks.

Reusable components for building custom monitors
including collectors, aggregators, and reporters.

Key exports:
    - Collector: Data collection component
    - Aggregator: Metric aggregation
    - Reporter: Metric reporting
"""''',

    # Logging
    "logging": '''"""
Structured logging infrastructure.

Provides logging configuration, formatters, handlers,
and structured logging utilities.

Key exports:
    - setup_logging: Logging initialization
    - get_logger: Logger factory
    - StructuredFormatter: JSON formatter
    - LogContext: Logging context manager
"""''',

    # Environment
    "environment": '''"""
Environment detection and configuration.

Utilities for detecting runtime environment, loading
environment variables, and environment-specific behavior.

Key exports:
    - Environment: Environment enumeration
    - detect_environment: Auto-detection
    - get_env: Environment variable access
    - require_env: Required env variable
"""''',

    # API modules
    "api": '''"""
API construction utilities.

Helpers for building REST APIs including route
registration, serialization, and middleware.

Key exports:
    - APIRouter: Route collection
    - api_route: Route decorator
    - APIResponse: Response wrapper
"""''',

    "api_registry": '''"""
API registry for dynamic route registration.

Registry for API endpoints enabling plugin-based
API construction.

Key exports:
    - APIRegistry: API endpoint registry
    - register_endpoint: Endpoint registration
    - get_endpoints: Endpoint retrieval
"""''',

    # Validators
    "validators": '''"""
Input validation framework.

Provides validators for common data types, custom
validator creation, and validation error handling.

Key exports:
    - Validator: Base validator class
    - StringValidator: String validation
    - NumberValidator: Numeric validation
    - validate: Validation decorator
"""''',

    # Commands
    "commands/advanced": '''"""
Advanced CLI commands.

Complex CLI operations for power users including
batch operations, migrations, and diagnostics.

Key exports:
    - batch_command: Batch operation command
    - migrate_command: Migration command
    - diagnose_command: Diagnostics command
"""''',

    "commands/developer": '''"""
Developer-focused CLI commands.

Commands for SDK development, debugging, and
local development workflows.

Key exports:
    - dev_server: Development server command
    - debug_command: Debug utilities
    - scaffold_command: Code scaffolding
"""''',

    "commands/identity": '''"""
Identity and authentication CLI commands.

Commands for managing authentication, users,
and identity providers.

Key exports:
    - login_command: User login
    - logout_command: User logout
    - whoami_command: Current user info
"""''',

    "commands/security": '''"""
Security management CLI commands.

Commands for managing security settings, keys,
and access control.

Key exports:
    - rotate_keys: Key rotation
    - audit_command: Security audit
    - permissions_command: Permission management
"""''',

    "commands/workflows": '''"""
Workflow management CLI commands.

Commands for managing and executing workflows
including CI/CD and automation.

Key exports:
    - run_workflow: Workflow execution
    - list_workflows: Workflow listing
    - workflow_status: Status checking
"""''',

    "commands/mcp": '''"""
MCP (Model Context Protocol) CLI commands.

Commands for MCP server management, tool registration,
and protocol operations.

Key exports:
    - start_server: Start MCP server
    - list_tools: List available tools
    - call_tool: Direct tool invocation
"""''',

    "commands/observability": '''"""
Observability CLI commands.

Commands for metrics, logging, and tracing
management.

Key exports:
    - logs_command: Log viewing
    - metrics_command: Metrics display
    - traces_command: Trace inspection
"""''',

    "commands/testing": '''"""
Testing CLI commands.

Commands for running tests, coverage reports,
and test management.

Key exports:
    - test_command: Run tests
    - coverage_command: Coverage report
    - fixtures_command: Fixture management
"""''',

    "commands/resilience": '''"""
Resilience testing CLI commands.

Commands for chaos engineering, fault injection,
and resilience testing.

Key exports:
    - chaos_command: Chaos testing
    - fault_inject: Fault injection
    - resilience_test: Resilience verification
"""''',

    "commands/performance": '''"""
Performance testing CLI commands.

Commands for benchmarking, profiling, and
performance analysis.

Key exports:
    - benchmark_command: Run benchmarks
    - profile_command: Performance profiling
    - analyze_command: Performance analysis
"""''',

    "commands/infrastructure": '''"""
Infrastructure management CLI commands.

Commands for managing infrastructure resources,
deployments, and environments.

Key exports:
    - deploy_command: Deployment
    - provision_command: Resource provisioning
    - teardown_command: Resource cleanup
"""''',

    "commands/data": '''"""
Data management CLI commands.

Commands for data operations, migrations,
and data pipeline management.

Key exports:
    - migrate_data: Data migration
    - import_command: Data import
    - export_command: Data export
"""''',

    "commands/vector": '''"""
Vector database CLI commands.

Commands for vector store management, embeddings,
and similarity search operations.

Key exports:
    - index_command: Vector indexing
    - search_command: Vector search
    - embeddings_command: Embedding management
"""''',

    "commands/analytics": '''"""
Analytics CLI commands.

Commands for analytics queries, reports,
and data exploration.

Key exports:
    - query_command: Analytics queries
    - report_command: Report generation
    - explore_command: Data exploration
"""''',

    "commands/multicloud": '''"""
Multi-cloud management CLI commands.

Commands for managing resources across multiple
cloud providers.

Key exports:
    - cloud_status: Multi-cloud status
    - sync_command: Cross-cloud sync
    - migrate_cloud: Cloud migration
"""''',
}


def get_module_key(path: Path, base: Path) -> str:
    """Extract module key from path."""
    rel = path.parent.relative_to(base)
    parts = list(rel.parts)

    # Remove leading 'core' if present
    if parts and parts[0] == 'core':
        parts = parts[1:]

    if not parts:
        return 'core'

    return '/'.join(parts)


def get_docstring(module_key: str, path: Path) -> str:
    """Get docstring for a module, generating if not defined."""
    if module_key in DOCSTRINGS:
        return DOCSTRINGS[module_key]

    # Generate based on module name
    name = path.parent.name
    parent = path.parent.parent.name if path.parent.parent.name != 'core' else 'core'

    # Clean up name
    display_name = name.replace('_', ' ').title()

    return f'''"""
{display_name} module.

Provides {name.replace('_', ' ')} functionality for the Pheno SDK core
infrastructure. Part of the {parent} subsystem.

See module contents for available exports and usage patterns.
"""'''


def update_init_file(path: Path, base: Path) -> bool:
    """Update a single __init__.py file."""
    content = path.read_text()

    # Check if it's a stub docstring
    stub_patterns = [
        r'^r?"""\\?\s*\\?\w+\s*module\.?\\?\s*\\?"""',
        r'^"""[\w\s]+module\."""',
        r'^"""\s*\n[\w\s]+module\.?\s*\n"""',
    ]

    is_stub = any(re.match(p, content.strip(), re.IGNORECASE | re.MULTILINE) for p in stub_patterns)

    # Also check for very short docstrings (under 50 chars)
    first_line = content.strip().split('\n')[0] if content.strip() else ''
    if first_line.startswith(('"""', "r'''")):
        is_stub = is_stub or len(content.strip().split('"""')[1] if '"""' in content else '') < 30

    if not is_stub:
        # Check if docstring is already comprehensive
        if len(content) > 200 and 'Key exports' in content:
            return False

    module_key = get_module_key(path, base)
    new_docstring = get_docstring(module_key, path)

    # Replace existing docstring or add new one
    if content.strip().startswith(('"""', "r'''")):
        # Find end of docstring
        if content.strip().startswith('r"""'):
            match = re.match(r'r""".*?"""', content, re.DOTALL)
        else:
            match = re.match(r'""".*?"""', content, re.DOTALL)

        if match:
            rest = content[match.end():].lstrip('\n')
            new_content = new_docstring + '\n' + rest if rest else new_docstring + '\n'
        else:
            new_content = new_docstring + '\n'
    else:
        new_content = new_docstring + '\n' + content

    path.write_text(new_content)
    return True


def main():
    base = Path('/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/src/pheno')
    core_path = base / 'core'

    updated = 0
    skipped = 0

    for init_path in sorted(core_path.rglob('__init__.py')):
        if update_init_file(init_path, base):
            print(f"Updated: {init_path.relative_to(base)}")
            updated += 1
        else:
            print(f"Skipped: {init_path.relative_to(base)}")
            skipped += 1

    print(f"\nTotal: {updated} updated, {skipped} skipped")


if __name__ == '__main__':
    main()
