-- Evidence is listed in chronological order by every dashboard request.
-- Keep the query index-backed as the dataset grows.
CREATE INDEX IF NOT EXISTS ix_evidence_created_at ON evidence (created_at);
