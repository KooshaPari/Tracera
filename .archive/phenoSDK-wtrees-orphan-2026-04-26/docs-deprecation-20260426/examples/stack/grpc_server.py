"""Runnable gRPC server using generic handlers + grpc-kit interceptors.

Requirements: pip install grpcio
Run: python examples/stack/grpc_server.py
"""

from __future__ import annotations

import time

try:
    import grpc  # type: ignore
except Exception:  # pragma: no cover
    raise SystemExit("grpcio is required: pip install grpcio")

from grpc_kit.interceptors import ServerTelemetryInterceptor


def make_server_interceptors():
    def on_md(md: dict[str, str]):
        # map metadata into logs/traces if desired
        pass

    return [ServerTelemetryInterceptor(on_metadata=on_md)]


# Implement a simple unary-unary echo via generic handler
ECHO_METHOD = "/demo.EchoService/Echo"


def echo_unary_unary(request: bytes, context):
    # Echo back body, prefixing 'echo:'
    return b"echo:" + bytes(request)


def serve(port: int = 50051):
    server = grpc.server(
        grpc.futures.ThreadPoolExecutor(max_workers=4), interceptors=make_server_interceptors(),
    )

    # Build generic handler
    method_handler = grpc.unary_unary_rpc_method_handler(
        echo_unary_unary,
        request_deserializer=lambda x: x,
        response_serializer=lambda x: x,
    )
    generic_handler = grpc.method_handlers_generic_handler(
        "demo.EchoService", {"Echo": method_handler},
    )
    server.add_generic_rpc_handlers((generic_handler,))

    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"gRPC server listening on {port}. Method: {ECHO_METHOD}")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":  # pragma: no cover
    serve()
