-- Migration 011: evidence reuse and invalidation ledger v1
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS evidence_reuse_decisions_v1 (
    reuse_decision_id TEXT PRIMARY KEY,
    observation_id TEXT NOT NULL REFERENCES product_observations_v1(observation_id),
    target_baseline_id TEXT NOT NULL REFERENCES product_baselines_v1(baseline_id),
    target_candidate_ref TEXT NOT NULL,
    criterion_ref TEXT NOT NULL,
    applicability_state TEXT NOT NULL,
    compatibility_certificate_ref TEXT,
    policy_version TEXT NOT NULL,
    reason TEXT NOT NULL,
    decided_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS invalidation_events_v1 (
    invalidation_id TEXT PRIMARY KEY,
    trigger_kind TEXT NOT NULL,
    trigger_ref TEXT NOT NULL,
    target_kind TEXT NOT NULL,
    target_ref TEXT NOT NULL,
    prior_state TEXT,
    new_state TEXT NOT NULL,
    reason TEXT NOT NULL,
    occurred_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_reuse_observation ON evidence_reuse_decisions_v1(observation_id);
CREATE INDEX IF NOT EXISTS idx_reuse_target ON evidence_reuse_decisions_v1(target_baseline_id, criterion_ref);
CREATE INDEX IF NOT EXISTS idx_invalidation_target ON invalidation_events_v1(target_kind, target_ref, occurred_at);
