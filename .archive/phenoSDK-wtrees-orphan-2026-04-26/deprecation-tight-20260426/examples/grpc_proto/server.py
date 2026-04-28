"""Proto-based gRPC server using generated stubs (requires echo_pb2*.py in this folder).

Generate stubs (requires grpcio-tools):
  python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. echo.proto

Run:
  python examples/grpc_proto/server.py
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

from grpc_kit.interceptors import ServerTelemetryInterceptor


class EchoService(echo_pb2_grpc.EchoServiceServicer):
    def Echo(self, request: echo_pb2.EchoRequest, context):
        return echo_pb2.EchoReply(message=f"echo:{request.message}")


def serve(port: int = 50052):
    server = grpc.server(
        grpc.futures.ThreadPoolExecutor(max_workers=4), interceptors=[ServerTelemetryInterceptor()],
    )
    echo_pb2_grpc.add_EchoServiceServicer_to_server(EchoService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Proto gRPC server listening on {port}...")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":  # pragma: no cover
    serve()
