-- Migration 0013: ingest idempotency (SQLite)
--
-- Ingest now writes deterministic IDs and replays whole batches. The natural
-- key for a trace edge is (source_id, target_id, relationship); dedupe any
-- legacy rows before enforcing it so this migration is safe on existing DBs.
DELETE FROM trace_links
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM trace_links
    GROUP BY source_id, target_id, relationship
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_trace_links_natural
    ON trace_links (source_id, target_id, relationship);
