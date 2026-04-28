from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from export_metrics import export_metrics  # type: ignore  # noqa: E402


def create_sample_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE metrics_records (
                request_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                task_type TEXT NOT NULL,
                task_complexity REAL,
                task_risk TEXT,
                model_used TEXT,
                candidate_models TEXT,
                input_tokens INTEGER,
                input_characters INTEGER,
                model_tier TEXT,
                routing_policy TEXT,
                selection_method TEXT,
                response_tokens INTEGER,
                response_characters INTEGER,
                latency_ms REAL,
                cost_in_usd REAL,
                cost_out_usd REAL,
                total_cost_usd REAL,
                cascade_cost_usd REAL,
                ttft_ms REAL,
                throughput_tps REAL,
                fallback_used INTEGER,
                error_occurred INTEGER,
                quality_score REAL,
                human_feedback_score REAL,
                was_successful INTEGER,
                validation_passed INTEGER,
                refinement_needed INTEGER,
                chain_length INTEGER,
                chain_position INTEGER,
                user_id TEXT,
                session_id TEXT,
                metadata TEXT
            )
            """,
        )
        conn.execute(
            """
            INSERT INTO metrics_records (
                request_id, timestamp, task_type, model_used,
                candidate_models, input_tokens, input_characters,
                latency_ms, cost_in_usd, cost_out_usd, total_cost_usd,
                fallback_used, error_occurred, quality_score, was_successful,
                chain_length, chain_position, metadata
            ) VALUES (
                'req-1', '2024-01-01T00:00:00Z', 'code.function', 'gpt-4o',
                '["gpt-4o"]', 120, 480, 1500.0, 0.002, 0.004, 0.006,
                0, 0, 0.9, 1, 1, 1, '{}'
            )
            """,
        )
        conn.commit()


def test_export_metrics(tmp_path: Path) -> None:
    db_path = tmp_path / "metrics.db"
    create_sample_db(db_path)

    data = export_metrics(db_path, limit=5)

    assert data["database"] == str(db_path)
    assert data["summary"]["gpt-4o"]["request_count"] == 1
    assert len(data["recent_records"]) == 1
