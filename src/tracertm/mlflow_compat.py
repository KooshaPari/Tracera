"""Small MLflow-compatible tracking client for TraceRTM training runs."""

from __future__ import annotations

import json
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import ParseResult, urlparse

import httpx
from opentelemetry import trace

_TRACER = trace.get_tracer(__name__)
_EVENT_SOURCE = "tracertm.mlflow_compat"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _as_str(value: object) -> str:
    return str(value)


class Run:
    """Active MLflow-compatible run."""

    def __init__(
        self,
        run_id: str | None = None,
        tracking_uri: str | None = None,
        experiment_id: str = "0",
        timeout_seconds: float = 5.0,
    ) -> None:
        """Create a run bound to a file:// or HTTP MLflow-compatible backend."""
        self.run_id = run_id or uuid.uuid4().hex
        self.tracking_uri = tracking_uri or "file://.tracertm/mlflow-runs"
        self.experiment_id = experiment_id
        self.timeout_seconds = timeout_seconds
        self._ended = False
        self._emit("runs/create", {"run_id": self.run_id, "experiment_id": experiment_id})

    def log_metric(self, key: str, value: float | int, step: int = 0) -> None:
        """Log one scalar metric at a training step."""
        self._ensure_active()
        self._emit(
            "runs/log-metric",
            {
                "run_id": self.run_id,
                "key": key,
                "value": float(value),
                "timestamp": _now_ms(),
                "step": step,
            },
        )

    def log_params(self, params: dict[str, object]) -> None:
        """Log run parameters."""
        self._ensure_active()
        for key, value in params.items():
            self._emit(
                "runs/log-parameter",
                {"run_id": self.run_id, "key": key, "value": _as_str(value)},
            )

    def log_artifact(self, path: str | os.PathLike[str]) -> Path | None:
        """Log an artifact path, copying it for file:// tracking stores."""
        self._ensure_active()
        source = Path(path)
        copied_to = self._copy_artifact(source)
        self._emit(
            "runs/log-artifact",
            {
                "run_id": self.run_id,
                "path": str(source),
                "local_path": str(copied_to) if copied_to else None,
            },
        )
        return copied_to

    def end(self) -> None:
        """Mark the run finished."""
        if self._ended:
            return
        self._emit(
            "runs/update",
            {"run_id": self.run_id, "status": "FINISHED", "end_time": _now_ms()},
        )
        self._ended = True

    def _ensure_active(self) -> None:
        if self._ended:
            msg = f"Run {self.run_id} has already ended"
            raise RuntimeError(msg)

    def _emit(self, endpoint: str, payload: dict[str, Any]) -> None:
        event_id = str(payload.get("event_id") or uuid.uuid4().hex)
        correlation_id = str(payload.get("correlation_id") or payload.get("run_id") or event_id)
        span_attributes = {
            "event.id": event_id,
            "event.type": endpoint,
            "source": _EVENT_SOURCE,
            "correlation_id": correlation_id,
        }
        with _TRACER.start_as_current_span(
            "tracertm.bus.emit",
            attributes=span_attributes,
        ):
            parsed = urlparse(self.tracking_uri)
            if parsed.scheme in ("", "file"):
                self._write_file_event(endpoint, payload)
                return
            if parsed.scheme in ("http", "https"):
                url = self.tracking_uri.rstrip("/") + f"/api/2.0/mlflow/{endpoint}"
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    client.post(url, json=payload).raise_for_status()
                return
            msg = f"Unsupported MLflow tracking URI scheme: {parsed.scheme}"
            raise ValueError(msg)

    def _write_file_event(self, endpoint: str, payload: dict[str, Any]) -> None:
        run_dir = self._run_dir()
        run_dir.mkdir(parents=True, exist_ok=True)
        event = {
            "mlflow_endpoint": f"/api/2.0/mlflow/{endpoint}",
            "payload": payload,
            "run_id": self.run_id,
            "timestamp": _now_ms(),
        }
        with (run_dir / "events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

    def _copy_artifact(self, source: Path) -> Path | None:
        parsed = urlparse(self.tracking_uri)
        if parsed.scheme not in ("", "file"):
            return None
        artifact_dir = self._run_dir() / "artifacts"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        destination = artifact_dir / source.name
        shutil.copy2(source, destination)
        return destination

    def _run_dir(self) -> Path:
        parsed = urlparse(self.tracking_uri)
        root = Path(parsed.path if parsed.scheme == "file" else self.tracking_uri)
        return root / self.run_id


class TrackingClient:
    """Minimal client compatible with common MLflow tracking operations."""

    def __init__(self, tracking_uri: str | None = None) -> None:
        """Create a tracking client with an optional backend URI."""
        self.tracking_uri = tracking_uri or os.getenv(
            "MLFLOW_TRACKING_URI",
            "file://.tracertm/mlflow-runs",
        )

    def set_tracking_uri(self, uri: str) -> None:
        """Set the tracking backend URI."""
        self.tracking_uri = uri

    def start_run(self, run_id: str | None = None, experiment_id: str = "0") -> Run:
        """Create a new active run."""
        return Run(run_id=run_id, tracking_uri=self.tracking_uri, experiment_id=experiment_id)

    def get_run(self, run_id: str) -> dict[str, Any]:
        """Return run metadata from a file or HTTP tracking backend."""
        parsed = urlparse(self.tracking_uri)
        if parsed.scheme in ("", "file"):
            run_dir = self._file_root(parsed) / run_id
            return {"run_id": run_id, "path": str(run_dir), "events": self._read_events(run_dir)}
        if parsed.scheme in ("http", "https"):
            return self._http_get("/api/2.0/mlflow/runs/get", {"run_id": run_id})
        msg = f"Unsupported MLflow tracking URI scheme: {parsed.scheme}"
        raise ValueError(msg)

    def search_runs(self) -> list[dict[str, Any]]:
        """List runs from a file or HTTP tracking backend."""
        parsed = urlparse(self.tracking_uri)
        if parsed.scheme in ("", "file"):
            root = self._file_root(parsed)
            if not root.exists():
                return []
            return [self.get_run(path.name) for path in sorted(root.iterdir()) if path.is_dir()]
        if parsed.scheme in ("http", "https"):
            data = self._http_get("/api/2.0/mlflow/runs/search", {})
            runs = data.get("runs", data)
            return runs if isinstance(runs, list) else [runs]
        msg = f"Unsupported MLflow tracking URI scheme: {parsed.scheme}"
        raise ValueError(msg)

    def _http_get(self, endpoint: str, params: dict[str, str]) -> dict[str, Any]:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(self.tracking_uri.rstrip("/") + endpoint, params=params)
            response.raise_for_status()
            return response.json()

    @staticmethod
    def _file_root(parsed: ParseResult) -> Path:
        return Path(parsed.path if parsed.scheme == "file" else parsed.geturl())

    @staticmethod
    def _read_events(run_dir: Path) -> list[dict[str, Any]]:
        event_file = run_dir / "events.jsonl"
        if not event_file.exists():
            return []
        return [
            json.loads(line)
            for line in event_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]


__all__ = ["Run", "TrackingClient"]
