"""Tests for MLflow-compatible run logging."""

# ruff: noqa: ANN001, ANN002, ANN202, ANN204, D103, PLR2004, RUF069, S101, S108

from __future__ import annotations

import json

import httpx
import pytest

from tracertm.observability.mlflow_run_logger import MLflowRunLogger


def _read_events(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_run_logger_writes_mlflow_compatible_events(tmp_path) -> None:
    logger = MLflowRunLogger(local_dir=tmp_path)

    run = logger.start_run(run_name="side-49", experiment_id="7", tags={"owner": "qa"})
    logger.log_param("model", "ranker", run=run)
    logger.log_metric("accuracy", 0.98, step=2, run=run)
    logger.end_run(run=run)

    events = _read_events(tmp_path / run.run_id / "events.jsonl")
    endpoints = [event["mlflow_endpoint"] for event in events]

    assert endpoints == [
        "/api/2.0/mlflow/runs/create",
        "/api/2.0/mlflow/runs/set-tag",
        "/api/2.0/mlflow/runs/log-parameter",
        "/api/2.0/mlflow/runs/log-metric",
        "/api/2.0/mlflow/runs/update",
    ]
    assert events[0]["payload"]["experiment_id"] == "7"
    assert events[0]["payload"]["tags"] == [{"key": "mlflow.runName", "value": "side-49"}]
    assert events[2]["payload"]["value"] == "ranker"
    assert events[3]["payload"]["value"] == 0.98
    assert events[4]["payload"]["status"] == "FINISHED"


def test_run_logger_copies_artifacts(tmp_path) -> None:
    source = tmp_path / "metrics.json"
    source.write_text('{"score": 1}', encoding="utf-8")
    logger = MLflowRunLogger(local_dir=tmp_path / "runs")
    run = logger.start_run()

    copied_to = logger.log_artifact(source, artifact_path="eval", run=run)

    assert copied_to == tmp_path / "runs" / run.run_id / "artifacts" / "eval" / source.name
    assert copied_to.read_text(encoding="utf-8") == '{"score": 1}'
    events = _read_events(tmp_path / "runs" / run.run_id / "events.jsonl")
    assert events[-1]["mlflow_endpoint"] == "/api/2.0/mlflow/runs/log-artifact"
    assert events[-1]["payload"]["local_path"] == str(copied_to)


def test_run_logger_requires_active_run(tmp_path) -> None:
    logger = MLflowRunLogger(local_dir=tmp_path)

    with pytest.raises(RuntimeError, match="No active MLflow run"):
        logger.log_metric("missing", 1)


def test_run_logger_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("TRACERTM_MLFLOW_TRACKING_URI", "http://mlflow.local")
    monkeypatch.setenv("TRACERTM_MLFLOW_LOCAL_DIR", "/tmp/tracertm-runs")

    logger = MLflowRunLogger.from_env()

    assert logger.tracking_uri == "http://mlflow.local"
    assert logger.local_dir == "/tmp/tracertm-runs"


def test_run_logger_posts_mlflow_rest_payloads(tmp_path, monkeypatch) -> None:
    requests = []

    class FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def post(self, url, json):
            requests.append((url, json))
            return httpx.Response(200, request=httpx.Request("POST", url))

    monkeypatch.setattr("tracertm.observability.mlflow_run_logger.httpx.Client", FakeClient)
    logger = MLflowRunLogger(tracking_uri="http://mlflow.local/", local_dir=tmp_path)
    run = logger.start_run(experiment_id="9")

    logger.log_metric("loss", 0.2, run=run)

    assert requests[0][0] == "http://mlflow.local/api/2.0/mlflow/runs/create"
    assert requests[0][1]["experiment_id"] == "9"
    assert requests[1][0] == "http://mlflow.local/api/2.0/mlflow/runs/log-metric"
    assert requests[1][1]["key"] == "loss"
