# Pheno-SDK Application Layer

## Overview

The application layer provides a cohesive, asynchronous API for orchestrating pheno-sdk infrastructure operations. It lives under `pheno.application.pheno_sdk` and is split into four building blocks:

- **DTOs (`dtos.py`)** – immutable dataclasses that describe input/outputs for lifecycle, health, tunnel, and port workflows.
- **Ports (`ports.py`)** – `Protocol` definitions that isolate the application layer from infrastructure adapters.
- **Application services (`services.py`)** – orchestration logic that sequences operations across ports (e.g., allocate port → start service → health check).
- **Use cases (`use_cases.py`)** – thin entrypoints that expose the concrete workflows (StartService, StopService, CheckHealth, CreateTunnel, AllocatePort).

All components are asynchronous to align with the existing service manager and networking stacks.

## Data Transfer Objects

Key DTOs exported from `pheno.application.pheno_sdk.dtos`:

- `StartServiceRequest` / `ServiceOperationResult` – lifecycle orchestration parameters and results, including optional `AllocatePortRequest` and `CreateTunnelRequest` payloads.
- `StopServiceRequest` – supports signaling whether the use case should close tunnels or release previously allocated ports.
- `HealthCheckRequest` / `HealthCheckResult` – encapsulate health probe configuration and responses.
- `CreateTunnelRequest` / `TunnelInfo` – describe tunnel creation and resulting connection details.
- `AllocatePortRequest` / `PortAllocationResult` – handle dynamic port provisioning.

DTOs accept optional `OperationContext` metadata, making correlation identifiers or actor information available to infrastructure adapters.

## Ports

`pheno.application.pheno_sdk.ports` defines four interfaces that infrastructure adapters must implement:

1. `ServiceLifecyclePort` – start/stop operations that return `ServiceOperationResult`.
2. `HealthCheckPort` – executes health probes.
3. `TunnelManagementPort` – creates and closes tunnels.
4. `PortAllocationPort` – allocates and releases network ports.

These protocols enable swapping underlying transport layers (local processes, Kubernetes, remote orchestration APIs, etc.) without altering the application logic.

## Application Services

`pheno.application.pheno_sdk.services` contains orchestration logic:

- `ServiceLifecycleService` coordinates port allocation, lifecycle transitions, optional tunnel creation, and post-start health checks. It automatically enriches metadata with allocation/tunnel/health details and tears down dependencies on failure.
- `HealthMonitoringService` is a focused wrapper around the health port.
- `TunnelOrchestrationService` manages tunnel lifecycle, optionally allocating a local port when one is not supplied.
- `PortProvisioningService` exposes direct allocate/release helpers for standalone port management scenarios.

Each service accepts the relevant port implementations during construction, promoting dependency injection and simplifying testing.

## Use Cases

`pheno.application.pheno_sdk.use_cases` packages the services into use case entrypoints:

- `StartServiceUseCase.execute(StartServiceRequest)`
- `StopServiceUseCase.execute(StopServiceRequest)`
- `CheckHealthUseCase.execute(HealthCheckRequest)`
- `CreateTunnelUseCase.execute(CreateTunnelRequest)`
- `AllocatePortUseCase.allocate(...)` / `.release(...)`

Use cases are intentionally thin adapters so that adapters (CLI, API, automation) interact with a stable surface while the orchestration logic remains centralized.

## Wiring Example

```python
from pheno.application.pheno_sdk import dtos, ports, services, use_cases

lifecycle_port: ports.ServiceLifecyclePort = ...
health_port: ports.HealthCheckPort = ...
allocator_port: ports.PortAllocationPort = ...

lifecycle_service = services.ServiceLifecycleService(
    lifecycle_port,
    health_port=health_port,
    port_allocator=allocator_port,
)
start_use_case = use_cases.StartServiceUseCase(lifecycle_service)

request = dtos.StartServiceRequest(
    service_name="analytics",
    port_request=dtos.AllocatePortRequest(service_name="analytics"),
)
result = await start_use_case.execute(request)
```

This example shows how an adapter wires concrete infrastructure ports into application services and use cases. The same wiring model applies for tunnels and health checks.

