# ADR 0003: Introduce grpc-kit (gRPC support with DI + Observability)

- **Status**: ✅ Accepted and Implemented (Task 3.1)
- **Date**: 2025-10-12
- **Implementation Date**: 2025-10-12
- **Decision Makers**: Pheno-SDK Core Team
- **Tags**: grpc, rpc, observability, di, adapters

## Context
Many services require high-performance RPC. We currently emphasize HTTP/ASGI and streaming; gRPC unlocks strong contracts and performance. We need a minimal, composable kit that integrates with adapter-kit (DI), config-kit (settings), and observability (OTEL interceptors), without re-implementing core gRPC behaviors.

## Decision
Create a `grpc-kit` package providing:
- **Interceptor interfaces** (client/server) integrating OpenTelemetry, correlation IDs, auth (per-request metadata)
- **Small DI glue** to register stubs/servers in adapter-kit Container
- **Config models** (host/port/opts/keepalive) via GrpcServerConfig and GrpcClientConfig
- **Codegen helper docs** (protoc commands) and comprehensive examples
- **Server and client wrappers** (GrpcServer, GrpcChannel) for simplified setup

No hard dependency on grpcio at repo root; grpc-kit declares its own deps.

## Implementation (Task 3.1)

### Components Delivered

#### 1. Interceptors (`grpc_kit/interceptors.py`)
- `ClientTelemetryInterceptor` - Inject trace context and correlation IDs
- `ServerTelemetryInterceptor` - Extract metadata for logging/OTEL
- `MetadataAuthInterceptor` - Server-side auth via bearer tokens
- `ClientSpanAttributesInterceptor` - Add request metadata to OTEL spans
- `ServerSpanAttributesInterceptor` - Add request metadata to OTEL spans

#### 2. Server Helpers (`grpc_kit/server.py`)
- `GrpcServerConfig` - Configuration with keepalive, TLS, options
- `GrpcServer` - Lightweight wrapper with interceptor composition
- `create_server()` - Factory function for quick setup

```python
from grpc_kit import create_server, GrpcServerConfig
from grpc_kit.interceptors import ServerTelemetryInterceptor

config = GrpcServerConfig(host="0.0.0.0", port=50051)
server = create_server(
    config,
    interceptors=[ServerTelemetryInterceptor()],
)

# Register services
add_YourServiceServicer_to_server(YourService(), server.server)

await server.start()
await server.wait_for_termination()
```

#### 3. Client Helpers (`grpc_kit/client.py`)
- `GrpcClientConfig` - Configuration with message limits, keepalive, TLS
- `GrpcChannel` - Lightweight wrapper with interceptor composition
- `create_channel()` - Factory function for quick setup

```python
from grpc_kit import create_channel
from grpc_kit.interceptors import ClientTelemetryInterceptor

channel = create_channel(
    "localhost:50051",
    interceptors=[ClientTelemetryInterceptor()],
)

stub = YourServiceStub(channel.channel)
response = await stub.YourMethod(request)

await channel.close()
```

#### 4. Examples
- `examples/hello_world_example.py` - Comprehensive server/client demo
- Shows interceptor usage, metadata injection, observability integration
- Demonstrates graceful degradation when dependencies unavailable

### Features

✅ **DI Integration**: Optional adapter-kit Container support
✅ **Observability**: Built-in OTEL and structlog integration
✅ **Configuration**: Structured config objects (not magic strings)
✅ **Interceptors**: Composable middleware for cross-cutting concerns
✅ **TLS Support**: SSL/TLS configuration for production
✅ **Keepalive**: Configurable keepalive settings
✅ **Graceful Degradation**: Works without optional dependencies

## Non-Goals
- Codegen toolchain management (leave to standard grpcio-tools)
- Full framework wrappers; keep it thin and composable
- Pre-wired OTEL exporters (use observability-kit helpers instead)

## Consequences

### Pros
✅ Standardized interceptors and DI wiring
✅ Simpler adoption with helper functions
✅ Consistent telemetry across services
✅ Clear configuration objects (not dictionaries)
✅ Optional dependencies for flexibility

### Cons
⚠️ Another kit to maintain (minimal due to thin wrapper approach)
⚠️ Need version pin guidance for grpcio (documented in pyproject.toml)
⚠️ Binary compatibility requires testing across platforms

## Migration/Adoption

### Quick Start

1. **Install dependencies**:
   ```bash
   pip install grpcio grpcio-tools
   pip install observability-kit[otel,structlog]  # Optional
   ```

2. **Define your .proto files**:
   ```protobuf
   syntax = "proto3";

   service YourService {
     rpc YourMethod (Request) returns (Response) {}
   }
   ```

3. **Generate Python code**:
   ```bash
   python -m grpc_tools.protoc \
     -I. \
     --python_out=. \
     --grpc_python_out=. \
     your_service.proto
   ```

4. **Use grpc-kit helpers**:
   ```python
   from grpc_kit import create_server, GrpcServerConfig
   from grpc_kit.interceptors import ServerTelemetryInterceptor

   # Server
   config = GrpcServerConfig(port=50051)
   server = create_server(config, interceptors=[...])
   # ... register services ...
   await server.start()

   # Client
   from grpc_kit import create_channel
   channel = create_channel("localhost:50051", interceptors=[...])
   stub = YourServiceStub(channel.channel)
   ```

### Integration Patterns

#### With Observability-Kit
```python
from observability_kit.helpers import configure_otel, configure_structlog
from grpc_kit import create_server, ServerTelemetryInterceptor

# Configure observability
configure_otel(service_name="grpc-service", ...)
configure_structlog(service_name="grpc-service", ...)

# Create server with telemetry
server = create_server(
    config,
    interceptors=[ServerTelemetryInterceptor(on_metadata=log_metadata)],
)
```

#### With Adapter-Kit DI
```python
from adapter_kit import Container
from grpc_kit import create_server

container = Container()
# Register dependencies
container.register_instance(DatabaseClient, db_client)

# Pass container to service implementations
server = create_server(config, container=container)
```

## Open Questions (Resolved)

### Binary compatibility across platforms?
- **Resolution**: Use standard grpcio packages; they handle platform-specific wheels
- **Action**: Document platform requirements in README

### Ship pre-wired OTEL exporters?
- **Resolution**: No; use observability-kit helpers for consistency
- **Rationale**: Avoid duplicating observability logic; keep grpc-kit focused on gRPC concerns

## Testing

- ✅ Interceptor functionality verified
- ✅ Server/client configuration tested
- ✅ Graceful degradation validated
- ✅ Example runs successfully

## Documentation

- ✅ ADR-0003 updated with implementation details
- ✅ Comprehensive example (`examples/hello_world_example.py`)
- ✅ Inline code documentation
- ✅ Integration patterns documented

## Next Steps

1. ✅ Basic implementation complete (Task 3.1)
2. 🔄 Validate in production-like scenario
3. 📝 Add advanced examples (streaming, bidirectional)
4. 🧪 Add integration tests
5. 📚 Create migration guide for existing gRPC services

## References

- gRPC Python: https://grpc.io/docs/languages/python/
- OpenTelemetry gRPC: https://opentelemetry.io/docs/instrumentation/python/automatic/grpc/
- observability-kit: `docs/guides/observability-bootstrap.md`
- adapter-kit: `docs/adr/0001-pheno-sdk-integration-layer.md`

---

**Updated**: 2025-10-12 (Task 3.1 implementation)
