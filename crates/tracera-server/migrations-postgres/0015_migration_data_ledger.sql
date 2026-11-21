CREATE TABLE IF NOT EXISTS tracera_migration_data_ledger (
    version BIGINT PRIMARY KEY,
    description TEXT NOT NULL,
    checksum BYTEA NOT NULL,
    data_fingerprint BYTEA NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
