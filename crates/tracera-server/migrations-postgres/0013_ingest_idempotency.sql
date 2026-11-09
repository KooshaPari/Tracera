-- Migration 0013: ingest idempotency (Postgres, server tier)
--
-- 1. Bring `trace_links` in line with the columns the store already writes
--    (`source`, `updated_at`) and `stories` in line with `story_points`.
-- 2. Deduplicate legacy trace edges and enforce their natural key so repeated
--    ingest cannot create duplicate rows.

ALTER TABLE trace_links
    ADD COLUMN IF NOT EXISTS source TEXT NOT NULL DEFAULT 'manual';
ALTER TABLE trace_links
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();

ALTER TABLE stories
    ADD COLUMN IF NOT EXISTS story_points BIGINT;

DELETE FROM trace_links a
USING trace_links b
WHERE a.ctid < b.ctid
  AND a.source_id = b.source_id
  AND a.target_id = b.target_id
  AND a.relationship = b.relationship;

CREATE UNIQUE INDEX IF NOT EXISTS trace_links_natural_idx
    ON trace_links (source_id, target_id, relationship);
