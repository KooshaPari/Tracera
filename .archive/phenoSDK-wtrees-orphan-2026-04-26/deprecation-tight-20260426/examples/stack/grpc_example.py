"""Minimal gRPC example with grpc-kit interceptors.

Note: Illustrative only; requires grpcio installed to run.
"""

from __future__ import annotations

try:
    import grpc  # type: ignore
except Exception:  # pragma: no cover
    grpc = None  # type: ignore

from grpc_kit.interceptors import ClientTelemetryInterceptor, ServerTelemetryInterceptor


def make_server_interceptors():
    def on_md(md: dict[str, str]):
        # Here you can map metadata into logs/traces
        pass

    return [ServerTelemetryInterceptor(on_metadata=on_md)]


def make_client_interceptors():
    def headers():
        return {"x-correlation-id": "demo"}

    return [ClientTelemetryInterceptor(get_headers=headers)]


# In real usage, attach interceptors when creating server/channel
# server = grpc.server(..., interceptors=make_server_interceptors())
# channel = grpc.intercept_channel(grpc.insecure_channel("localhost:50051"), *make_client_interceptors())
