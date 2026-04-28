"""Proto-based gRPC client using generated stubs (requires echo_pb2*.py in this folder).

Generate stubs (requires grpcio-tools):
  python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. echo.proto

Run:
  python examples/grpc_proto/client.py
"""

from __future__ import annotations

try:
    import grpc  # type: ignore
except Exception:  # pragma: no cover
    raise SystemExit("grpcio is required: pip install grpcio")

try:
    import echo_pb2  # type: ignore
    import echo_pb2_grpc
except Exception as e:  # pragma: no cover
    raise SystemExit(
        "Missing generated stubs. Run: python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. echo.proto",
    ) from e

from grpc_kit.interceptors import ClientTelemetryInterceptor


def make_stub(address: str = "localhost:50052"):
    interceptor = ClientTelemetryInterceptor(
        get_headers=lambda: {"x-correlation-id": "demo-client"},
    )
    channel = grpc.intercept_channel(grpc.insecure_channel(address), interceptor)
    return echo_pb2_grpc.EchoServiceStub(channel)


def main():
    stub = make_stub()
    resp = stub.Echo(echo_pb2.EchoRequest(message="hello"), timeout=5)
    print(f"Response: {resp.message}")


if __name__ == "__main__":  # pragma: no cover
    main()
