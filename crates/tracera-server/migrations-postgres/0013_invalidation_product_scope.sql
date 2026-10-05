-- Migration 0013: scope invalidation ledger rows to canonical product identity.
--
-- Existing v1 rows predate product scoping and remain NULL. Product-scoped
-- application reads intentionally do not surface those ambiguous historical
-- rows as current product truth.
ALTER TABLE invalidation_events_v1
    ADD COLUMN IF NOT EXISTS product_id TEXT REFERENCES product_nodes(id);

CREATE INDEX IF NOT EXISTS idx_invalidation_product_target
    ON invalidation_events_v1(product_id, target_kind, target_ref, occurred_at);
