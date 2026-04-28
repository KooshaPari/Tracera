"""Helpers for rendering proxy health snapshots in TUIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def _coerce_service_name(upstream: Mapping[str, Any]) -> str:
    service = upstream.get("service")
    if service:
        return str(service)
    path_prefix = str(upstream.get("path_prefix", "/"))
    service = path_prefix.strip("/")
    return service or "service"


def build_proxy_health_rows(snapshot: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Prepare simple rows for TUI table rendering from a registry snapshot."""

    upstreams = snapshot.get("upstreams") or []
    rows: list[dict[str, Any]] = []
    for upstream in upstreams:
        if not isinstance(upstream, Mapping):
            continue

        row = {
            "tenant": upstream.get("tenant") or upstream.get("project") or "-",
            "service": _coerce_service_name(upstream),
            "path": upstream.get("path_prefix"),
            "host": upstream.get("host"),
            "port": upstream.get("port"),
            "healthy": upstream.get("healthy"),
            "last_checked": upstream.get("last_checked"),
        }
        rows.append(row)

    rows.sort(key=lambda item: (str(item.get("tenant") or ""), str(item.get("service") or "")))
    return rows


__all__ = ["build_proxy_health_rows"]
