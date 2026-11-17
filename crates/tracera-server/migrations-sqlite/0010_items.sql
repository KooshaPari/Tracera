-- Canonical item records are independent of SWEE graph node identity.
-- The JSON document preserves optional frontend Item extensions losslessly.
CREATE TABLE items (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    status TEXT NOT NULL,
    view TEXT NOT NULL,
    priority TEXT NOT NULL,
    document TEXT NOT NULL
);
CREATE INDEX idx_items_project_id ON items(project_id, id);
