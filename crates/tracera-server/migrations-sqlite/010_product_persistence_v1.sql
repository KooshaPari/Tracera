-- Migration 010: Product persistence v1 historical identity
-- Additive only. Preserves product_nodes/product_edges v0.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS product_baselines_v1 (
    baseline_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    revision_number INTEGER NOT NULL CHECK (revision_number >= 0),
    parent_baseline_id TEXT NULL REFERENCES product_baselines_v1(baseline_id),
    accepted_at TEXT NOT NULL,
    metadata TEXT NOT NULL DEFAULT '{}',
    UNIQUE(product_id, revision_number)
);

CREATE TABLE IF NOT EXISTS product_entities_v1 (
    entity_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    local_id TEXT NOT NULL,
    entity_kind TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(product_id, local_id)
);

CREATE TABLE IF NOT EXISTS product_entity_revisions_v1 (
    entity_revision_id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL REFERENCES product_entities_v1(entity_id),
    content_revision INTEGER NOT NULL CHECK (content_revision >= 1),
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL,
    metadata TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    UNIQUE(entity_id, content_revision)
);

CREATE TABLE IF NOT EXISTS baseline_entity_membership_v1 (
    baseline_id TEXT NOT NULL REFERENCES product_baselines_v1(baseline_id),
    entity_id TEXT NOT NULL REFERENCES product_entities_v1(entity_id),
    entity_revision_id TEXT NOT NULL REFERENCES product_entity_revisions_v1(entity_revision_id),
    PRIMARY KEY(baseline_id, entity_id),
    UNIQUE(baseline_id, entity_revision_id)
);

CREATE TABLE IF NOT EXISTS product_observations_v1 (
    observation_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    baseline_id TEXT NOT NULL REFERENCES product_baselines_v1(baseline_id),
    subject_entity_id TEXT NULL REFERENCES product_entities_v1(entity_id),
    subject_local_id TEXT NULL,
    candidate_ref TEXT NOT NULL,
    configuration TEXT NOT NULL DEFAULT '{}',
    result TEXT NOT NULL,
    verifier_id TEXT NOT NULL,
    verifier_version TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    raw_evidence_ref TEXT NULL,
    metadata TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_pbv1_product ON product_baselines_v1(product_id, revision_number);
CREATE INDEX IF NOT EXISTS idx_pev1_product_local ON product_entities_v1(product_id, local_id);
CREATE INDEX IF NOT EXISTS idx_perv1_entity ON product_entity_revisions_v1(entity_id, content_revision);
CREATE INDEX IF NOT EXISTS idx_bemv1_baseline ON baseline_entity_membership_v1(baseline_id);
CREATE INDEX IF NOT EXISTS idx_pov1_scope ON product_observations_v1(product_id, baseline_id, subject_local_id);
