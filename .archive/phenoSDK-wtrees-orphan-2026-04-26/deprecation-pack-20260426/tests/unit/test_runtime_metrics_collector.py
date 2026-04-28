from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from pheno.observability.runtime_metrics.collector import MetricsCollector
from pheno.observability.runtime_metrics.storage import SqliteMetricsStorage


@pytest.fixture()
def temp_storage(tmp_path: Path) -> SqliteMetricsStorage:
    db_path = tmp_path / "metrics.db"
    return SqliteMetricsStorage(db_path)


def test_metrics_collector_persists_records(temp_storage: SqliteMetricsStorage) -> None:
    collector = MetricsCollector(storage_backend=temp_storage, flush_batch_size=1)

    request_id = "req-123"
    collector.record_request_start(
        request_id=request_id,
        task_type="code_generation",
        user_id="user-1",
        input_tokens=128,
    )
    collector.record_model_selection(
        request_id,
        model_used="gpt-4o",
        candidate_models=["gpt-4o", "claude-3"],
        selection_method="policy",
        model_tier="premium",
    )
    collector.record_model_performance(
        request_id,
        response_tokens=256,
        latency_ms=1200.0,
        cost_in_usd=0.002,
        cost_out_usd=0.004,
        fallback_used=False,
    )
    collector.record_quality_assessment(request_id, quality_score=0.9, was_successful=True)
    collector.finalize_request(request_id)

    with sqlite3.connect(temp_storage.database_path) as conn:
        cursor = conn.execute(
            "SELECT request_id, task_type, model_used, latency_ms FROM metrics_records",
        )
        row = cursor.fetchone()

    assert row == ("req-123", "code_generation", "gpt-4o", 1200.0)


def test_finalize_missing_request_returns_none(temp_storage: SqliteMetricsStorage) -> None:
    collector = MetricsCollector(storage_backend=temp_storage)
    assert collector.finalize_request("unknown") is None


def test_flush_without_records_noop(temp_storage: SqliteMetricsStorage) -> None:
    collector = MetricsCollector(storage_backend=temp_storage)
    collector.flush_cache()
