"""MLflow-compatible run logging for TraceRTM observability."""

from __future__ import annotations

import json
import os
import shutil
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx


def _now_ms() -> int:
    return int(time.time() * 1000)


def _string_value(value: object) -> str:
    return str(value)


@dataclass(frozen=True)
class MLflowRun:
    """Minimal MLflow-compatible run identity."""

    run_id: str
    experiment_id: str = "0"
    run_name: str | None = None


@dataclass
class MLflowRunLogger:
    """Log run metadata using MLflow Tracking REST shapes with local fallback.

    When tracking_uri is provided, events are sent to compatible MLflow endpoints.
    Every event is also written as JSON Lines when local_dir is set.
    """

    tracking_uri: str | None = None
    local_dir: Path | str | None = None
    timeout_seconds: float = 5.0
    _active_run: MLflowRun | None = field(default=None, init=False, repr=False)

    @classmethod
    def from_env(cls) -> MLflowRunLogger:
        """Create a logger from TraceRTM or MLflow environment variables."""
        return cls(
            tracking_uri=os.getenv("TRACERTM_MLFLOW_TRACKING_URI")
            or os.getenv("MLFLOW_TRACKING_URI"),
            local_dir=os.getenv("TRACERTM_MLFLOW_LOCAL_DIR", ".tracertm/mlflow-runs"),
        )

    def start_run(
        self,
        run_name: str | None = None,
        experiment_id: str = "0",
        tags: dict[str, object] | None = None,
    ) -> MLflowRun:
        """Start a run and emit MLflow-compatible create/set-tag records."""
        run = MLflowRun(run_id=uuid.uuid4().hex, experiment_id=experiment_id, run_name=run_name)
        self._active_run = run
        self._emit(
            "runs/create",
            {
                "experiment_id": experiment_id,
                "start_time": _now_ms(),
                "tags": self._tag_list({"mlflow.runName": run_name} if run_name else {}),
                "run_id": run.run_id,
            },
            run,
        )
        if tags:
            for key, value in tags.items():
                self.set_tag(key, value, run=run)
        return run

    def end_run(self, status: str = "FINISHED", run: MLflowRun | None = None) -> None:
        """Mark a run terminated with an MLflow-compatible status."""
        target = self._require_run(run)
        self._emit(
            "runs/update",
            {"run_id": target.run_id, "status": status, "end_time": _now_ms()},
            target,
        )
        if self._active_run == target:
            self._active_run = None

    def log_param(self, key: str, value: object, run: MLflowRun | None = None) -> None:
        """Log one MLflow parameter."""
        target = self._require_run(run)
        self._emit(
            "runs/log-parameter",
            {"run_id": target.run_id, "key": key, "value": _string_value(value)},
            target,
        )

    def log_metric(
        self,
        key: str,
        value: float | int,
        step: int = 0,
        run: MLflowRun | None = None,
    ) -> None:
        """Log one MLflow metric."""
        target = self._require_run(run)
        self._emit(
            "runs/log-metric",
            {
                "run_id": target.run_id,
                "key": key,
                "value": float(value),
                "timestamp": _now_ms(),
                "step": step,
            },
            target,
        )

    def set_tag(self, key: str, value: object, run: MLflowRun | None = None) -> None:
        """Set one MLflow tag."""
        target = self._require_run(run)
        self._emit(
            "runs/set-tag",
            {"run_id": target.run_id, "key": key, "value": _string_value(value)},
            target,
        )

    def log_artifact(
        self,
        source: Path | str,
        artifact_path: str | None = None,
        run: MLflowRun | None = None,
    ) -> Path | None:
        """Copy an artifact into the local run store and record its metadata."""
        target = self._require_run(run)
        source_path = Path(source)
        copied_to: Path | None = None
        if self.local_dir is not None:
            destination_dir = Path(self.local_dir) / target.run_id / "artifacts"
            if artifact_path:
                destination_dir /= artifact_path
            destination_dir.mkdir(parents=True, exist_ok=True)
            copied_to = destination_dir / source_path.name
            shutil.copy2(source_path, copied_to)
        self._emit(
            "runs/log-artifact",
            {
                "run_id": target.run_id,
                "path": str(source_path),
                "artifact_path": artifact_path,
                "local_path": str(copied_to) if copied_to else None,
            },
            target,
        )
        return copied_to

    def _require_run(self, run: MLflowRun | None) -> MLflowRun:
        target = run or self._active_run
        if target is None:
            msg = "No active MLflow run; call start_run() or pass run=..."
            raise RuntimeError(msg)
        return target

    def _emit(self, endpoint: str, payload: dict[str, Any], run: MLflowRun) -> None:
        event = {
            "mlflow_endpoint": f"/api/2.0/mlflow/{endpoint}",
            "run_id": run.run_id,
            "experiment_id": run.experiment_id,
            "payload": payload,
            "timestamp": _now_ms(),
        }
        self._write_local_event(event)
        if self.tracking_uri:
            url = self.tracking_uri.rstrip("/") + event["mlflow_endpoint"]
            with httpx.Client(timeout=self.timeout_seconds) as client:
                client.post(url, json=payload).raise_for_status()

    def _write_local_event(self, event: dict[str, Any]) -> None:
        if self.local_dir is None:
            return
        run_dir = Path(self.local_dir) / event["run_id"]
        run_dir.mkdir(parents=True, exist_ok=True)
        with (run_dir / "events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

    @staticmethod
    def _tag_list(tags: dict[str, object]) -> list[dict[str, str]]:
        return [{"key": key, "value": _string_value(value)} for key, value in tags.items()]


__all__ = ["MLflowRun", "MLflowRunLogger"]
