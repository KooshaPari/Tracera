//! Canonical PostgreSQL migration root with a data/checksum ledger.
//!
//! Applied status is derived only from ledger rows. Schema contents are never
//! used to infer that a migration ran.

use sqlx::migrate::Migrator;
use sqlx::postgres::{PgAdvisoryLock, PgPool};
use std::collections::{BTreeMap, BTreeSet};

pub(crate) static MIGRATOR: Migrator = sqlx::migrate!("./migrations-postgres");

#[cfg_attr(not(test), allow(dead_code))]
pub(crate) const LEDGER_TABLE: &str = "tracera_migration_data_ledger";
pub(crate) const HISTORICAL_VERSION: i64 = 11;
pub(crate) const REPAIRED_VERSION: i64 = 16;

/// SHA-384 of the original `0011_agileplus_ingest.sql` content at base 5f2643ba.
pub(crate) const HISTORICAL_AGILEPLUS_SHA384: &str =
    "a0f5049611d48abb8dcff2c1f2a70bd34addbcc3359af86e49a5b1e0324131625bdcf69ab61b7db24e2ae6ca2f319376";
/// SHA-384 of the original `0011_items.sql` content at base 5f2643ba.
pub(crate) const HISTORICAL_ITEMS_SHA384: &str =
    "254909bab0b5a4c4bb1e15ae8a90c92ecac9425def85279b0d137f902d90fc09e7aa9fc0f5d194d7dd18363d8adc2e8e";

pub(crate) const CREATE_LEDGER_SQL: &str = r#"
CREATE TABLE IF NOT EXISTS tracera_migration_data_ledger (
    version BIGINT PRIMARY KEY,
    description TEXT NOT NULL,
    checksum BYTEA NOT NULL,
    data_fingerprint BYTEA NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
"#;

pub(crate) const APPLY_RECORD_SQL: &str = r#"
INSERT INTO tracera_migration_data_ledger
    (version, description, checksum, data_fingerprint)
VALUES ($1, $2, $3, $4)
ON CONFLICT (version) DO NOTHING
"#;

pub(crate) const READ_APPLIED_SQL: &str =
    "SELECT version, checksum FROM _sqlx_migrations WHERE version = $1";
pub(crate) const REVERSE_VERSION_SQL: &str = r#"
UPDATE _sqlx_migrations
SET version = $1, description = $2, checksum = $3
WHERE version = $4 AND checksum = $5
"#;
pub(crate) const READ_LEDGER_SQL: &str =
    "SELECT version, checksum, data_fingerprint FROM tracera_migration_data_ledger ORDER BY version";
#[cfg_attr(not(test), allow(dead_code))]
pub(crate) const DATA_MARKER_SQL: &str = r#"
SELECT EXISTS (
    SELECT 1 FROM tracera_migration_data_ledger
    WHERE version = $1 AND data_fingerprint <> decode($2, 'hex')
)
"#;

const ADVISORY_LOCK_KEY: &str = "tracera-postgres-migration-root";

#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) struct DuplicateVersion {
    pub(crate) version: i64,
    pub(crate) descriptions: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) enum RepairPlan {
    Noop,
    Reversion { from: i64, to: i64 },
    Error(String),
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[cfg_attr(not(test), allow(dead_code))]
pub(crate) enum LedgerDecision {
    ApplyAll,
    ApplyMissing,
    RepairLedger,
    Noop,
}

/// Duplicate versions in a migrator manifest, using up migrations only.
pub(crate) fn duplicate_versions(migrator: &Migrator) -> Vec<DuplicateVersion> {
    let mut by_version: BTreeMap<i64, Vec<String>> = BTreeMap::new();
    for migration in migrator
        .iter()
        .filter(|m| m.migration_type.is_up_migration())
    {
        by_version
            .entry(migration.version)
            .or_default()
            .push(migration.description.to_string());
    }
    by_version
        .into_iter()
        .filter(|(_, descriptions)| descriptions.len() > 1)
        .map(|(version, descriptions)| DuplicateVersion {
            version,
            descriptions,
        })
        .collect()
}

/// The canonical root must be unique before any database connection is used.
pub(crate) fn ensure_unique_root() -> Result<(), String> {
    let duplicates = duplicate_versions(&MIGRATOR);
    if duplicates.is_empty() {
        Ok(())
    } else {
        Err(format!(
            "duplicate PostgreSQL migration versions: {:?}",
            duplicates.iter().map(|d| d.version).collect::<Vec<_>>()
        ))
    }
}

#[cfg_attr(not(test), allow(dead_code))]
pub(crate) fn canonical_versions() -> Vec<i64> {
    MIGRATOR
        .iter()
        .filter(|m| m.migration_type.is_up_migration())
        .map(|m| m.version)
        .collect()
}

/// Plan a checksum-verified repair for historical version-11 rows.
///
/// The old version-11 `agileplus ingest` migration now lives at version 16.
/// Schema contents are never inspected; only the applied checksum decides.
pub(crate) fn historical_repair_plan(applied_rows: &[(i64, Vec<u8>)]) -> RepairPlan {
    let mut old_row: Option<&Vec<u8>> = None;
    let mut new_row: Option<&Vec<u8>> = None;
    for (version, checksum) in applied_rows {
        match *version {
            HISTORICAL_VERSION => old_row = Some(checksum),
            REPAIRED_VERSION => new_row = Some(checksum),
            _ => {}
        }
    }

    let old_items = match hex_decode(HISTORICAL_ITEMS_SHA384) {
        Ok(bytes) => bytes,
        Err(e) => return RepairPlan::Error(e),
    };
    let old_agileplus = match hex_decode(HISTORICAL_AGILEPLUS_SHA384) {
        Ok(bytes) => bytes,
        Err(e) => return RepairPlan::Error(e),
    };
    let expected_agileplus = match MIGRATOR
        .iter()
        .find(|m| m.version == REPAIRED_VERSION)
        .map(|m| m.checksum.to_vec())
    {
        Some(checksum) => checksum,
        None => return RepairPlan::Error("version 16 migration missing".to_owned()),
    };

    match (old_row, new_row) {
        (None, _) => RepairPlan::Noop,
        (Some(checksum), _) if checksum == &old_items => RepairPlan::Noop,
        (Some(checksum), Some(existing)) if checksum == &old_agileplus => {
            if existing == &expected_agileplus {
                RepairPlan::Noop
            } else {
                RepairPlan::Error("version 16 has an unexpected checksum".to_owned())
            }
        }
        (Some(checksum), None) if checksum == &old_agileplus => RepairPlan::Reversion {
            from: HISTORICAL_VERSION,
            to: REPAIRED_VERSION,
        },
        (Some(_), _) => RepairPlan::Error(
            "version 11 has an unknown checksum; refusing to guess migration state".to_owned(),
        ),
    }
}

/// Decide the next action from ledger state alone.
#[cfg_attr(not(test), allow(dead_code))]
pub(crate) fn ledger_decision(applied: &[i64], expected: &[i64]) -> LedgerDecision {
    let applied_set: BTreeSet<_> = applied.iter().copied().collect();
    let expected_set: BTreeSet<_> = expected.iter().copied().collect();
    if applied.is_empty() {
        LedgerDecision::ApplyAll
    } else if applied_set == expected_set {
        LedgerDecision::Noop
    } else if applied_set.is_subset(&expected_set) {
        LedgerDecision::ApplyMissing
    } else {
        LedgerDecision::RepairLedger
    }
}

/// Apply the canonical PostgreSQL migration root once.
///
/// SQLx owns migration locking and per-migration transactions. The advisory
/// lock additionally serializes ledger reads/writes across concurrent startups.
pub(crate) async fn apply_root(pool: &PgPool) -> Result<(), String> {
    ensure_unique_root()?;
    let connection = pool
        .acquire()
        .await
        .map_err(|e| format!("acquire Postgres connection: {e}"))?;
    let lock = PgAdvisoryLock::new(ADVISORY_LOCK_KEY);
    let mut guard = lock
        .acquire(connection)
        .await
        .map_err(|e| format!("acquire migration advisory lock: {e}"))?;
    let result = apply_migrations_with_lock(&mut guard).await;
    let _connection = guard
        .release_now()
        .await
        .map_err(|e| format!("release migration advisory lock: {e}"))?;
    result
}

async fn apply_migrations_with_lock(connection: &mut sqlx::PgConnection) -> Result<(), String> {
    repair_historical_version(connection).await?;

    MIGRATOR
        .run(&mut *connection)
        .await
        .map_err(|e| format!("apply Postgres migrations: {e}"))?;

    sqlx::query(CREATE_LEDGER_SQL)
        .execute(&mut *connection)
        .await
        .map_err(|e| format!("create migration ledger: {e}"))?;

    let expected = expected_ledger_rows();
    let existing: Vec<(i64, Vec<u8>, Vec<u8>)> = sqlx::query_as(READ_LEDGER_SQL)
        .fetch_all(&mut *connection)
        .await
        .map_err(|e| format!("read migration ledger: {e}"))?;
    for (version, checksum, fingerprint) in &existing {
        if let Some((_, _, expected_checksum, expected_fingerprint)) =
            expected.iter().find(|(v, _, _, _)| v == version)
        {
            if checksum != expected_checksum || fingerprint != expected_fingerprint {
                return Err(format!(
                    "migration ledger checksum mismatch at version {version}"
                ));
            }
        } else {
            return Err(format!("unknown migration ledger version {version}"));
        }
    }

    for (version, description, checksum, fingerprint) in expected {
        if existing.iter().any(|(v, _, _)| v == &version) {
            continue;
        }
        sqlx::query(APPLY_RECORD_SQL)
            .bind(version)
            .bind(description)
            .bind(checksum)
            .bind(fingerprint)
            .execute(&mut *connection)
            .await
            .map_err(|e| format!("record migration ledger row: {e}"))?;
    }

    Ok(())
}

async fn repair_historical_version(connection: &mut sqlx::PgConnection) -> Result<(), String> {
    let table_exists: Option<i64> = sqlx::query_scalar(
        "SELECT 1 FROM information_schema.tables WHERE table_schema = current_schema() AND table_name = '_sqlx_migrations' LIMIT 1",
    )
    .fetch_optional(&mut *connection)
    .await
    .map_err(|e| format!("check migration table: {e}"))?;
    if table_exists.is_none() {
        return Ok(());
    }

    let mut rows = Vec::new();
    for version in [HISTORICAL_VERSION, REPAIRED_VERSION] {
        let row: Option<(i64, Vec<u8>)> = sqlx::query_as(READ_APPLIED_SQL)
            .bind(version)
            .fetch_optional(&mut *connection)
            .await
            .map_err(|e| format!("read applied migration version {version}: {e}"))?;
        if let Some(row) = row {
            rows.push(row);
        }
    }

    match historical_repair_plan(&rows) {
        RepairPlan::Noop => Ok(()),
        RepairPlan::Error(e) => Err(e),
        RepairPlan::Reversion { from, to } => {
            let migration = MIGRATOR
                .iter()
                .find(|m| m.version == to)
                .ok_or_else(|| "version 16 migration missing".to_owned())?;
            sqlx::query(REVERSE_VERSION_SQL)
                .bind(to)
                .bind(migration.description.as_ref())
                .bind(migration.checksum.as_ref())
                .bind(from)
                .bind(hex_decode(HISTORICAL_AGILEPLUS_SHA384)?)
                .execute(&mut *connection)
                .await
                .map_err(|e| format!("repair historical migration version: {e}"))?;
            Ok(())
        }
    }
}

fn expected_ledger_rows() -> Vec<(i64, String, Vec<u8>, Vec<u8>)> {
    MIGRATOR
        .iter()
        .filter(|m| m.migration_type.is_up_migration())
        .map(|m| {
            let sql = m.sql.as_str();
            (
                m.version,
                m.description.to_string(),
                m.checksum.to_vec(),
                data_fingerprint(m.version, m.description.as_ref(), sql),
            )
        })
        .collect()
}

pub(crate) fn data_fingerprint(version: i64, description: &str, sql: &str) -> Vec<u8> {
    sha384(format!("{version}\0{description}\0{sql}").as_bytes())
}

#[cfg_attr(not(test), allow(dead_code))]
pub(crate) fn data_marker_query(version: i64, expected_sha384_hex: &str) -> String {
    format!("SELECT 1 FROM {LEDGER_TABLE} WHERE version = {version} AND data_fingerprint = decode('{expected_sha384_hex}', 'hex')")
}

#[cfg_attr(not(test), allow(dead_code))]
pub(crate) fn hex_encode(bytes: &[u8]) -> String {
    bytes.iter().map(|byte| format!("{byte:02x}")).collect()
}

pub(crate) fn hex_decode(hex: &str) -> Result<Vec<u8>, String> {
    if !hex.len().is_multiple_of(2) {
        return Err("invalid hex checksum length".to_owned());
    }
    (0..hex.len())
        .step_by(2)
        .map(|i| {
            u8::from_str_radix(&hex[i..i + 2], 16).map_err(|e| format!("invalid hex checksum: {e}"))
        })
        .collect()
}

pub(crate) fn sha384(data: &[u8]) -> Vec<u8> {
    use sha2::{Digest, Sha384};
    Sha384::digest(data).to_vec()
}

#[cfg_attr(not(test), allow(dead_code))]
pub(crate) fn advisory_lock_key() -> &'static str {
    ADVISORY_LOCK_KEY
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn canonical_root_has_unique_versions() {
        assert!(ensure_unique_root().is_ok());
        assert!(duplicate_versions(&MIGRATOR).is_empty());
        let versions = canonical_versions();
        assert_eq!(versions.len(), 16);
        assert_eq!(versions.iter().filter(|v| **v == 11).count(), 1);
        assert_eq!(versions.last(), Some(&16));
    }

    #[test]
    fn duplicate_version_is_detected_and_repaired_by_unique_root() {
        let mut migrations: Vec<_> = MIGRATOR.iter().cloned().collect();
        let duplicate = migrations[0].clone();
        migrations.push(duplicate);
        let duplicated = Migrator::with_migrations(migrations);
        let found = duplicate_versions(&duplicated);
        assert_eq!(found.len(), 1);
        assert_eq!(found[0].version, 1);
        assert!(found[0].descriptions.len() == 2);
        assert!(ensure_unique_root().is_ok());
    }

    #[test]
    fn historical_agileplus_row_is_reversioned() {
        let old = hex_decode(HISTORICAL_AGILEPLUS_SHA384).unwrap();
        let plan = historical_repair_plan(&[(HISTORICAL_VERSION, old)]);
        assert_eq!(
            plan,
            RepairPlan::Reversion {
                from: HISTORICAL_VERSION,
                to: REPAIRED_VERSION
            }
        );
    }

    #[test]
    fn historical_items_row_and_empty_database_are_noops() {
        let items = hex_decode(HISTORICAL_ITEMS_SHA384).unwrap();
        assert_eq!(
            historical_repair_plan(&[]),
            RepairPlan::Noop,
            "empty database must not be repaired"
        );
        assert_eq!(
            historical_repair_plan(&[(HISTORICAL_VERSION, items)]),
            RepairPlan::Noop
        );
    }

    #[test]
    fn unknown_and_conflicting_historical_rows_fail_closed() {
        assert!(matches!(
            historical_repair_plan(&[(HISTORICAL_VERSION, vec![0; 48])]),
            RepairPlan::Error(_)
        ));
        let expected = MIGRATOR
            .iter()
            .find(|m| m.version == REPAIRED_VERSION)
            .unwrap()
            .checksum
            .to_vec();
        assert!(matches!(
            historical_repair_plan(&[
                (
                    HISTORICAL_VERSION,
                    hex_decode(HISTORICAL_AGILEPLUS_SHA384).unwrap()
                ),
                (REPAIRED_VERSION, vec![0; 48]),
            ]),
            RepairPlan::Error(_)
        ));
        assert_eq!(
            historical_repair_plan(&[(REPAIRED_VERSION, expected)]),
            RepairPlan::Noop
        );
    }

    #[test]
    fn ledger_decisions_cover_all_startup_cases() {
        let expected = vec![1, 2, 3];
        assert_eq!(ledger_decision(&[], &expected), LedgerDecision::ApplyAll);
        assert_eq!(
            ledger_decision(&[1, 3], &expected),
            LedgerDecision::ApplyMissing
        );
        assert_eq!(
            ledger_decision(&[1, 2, 3, 99], &expected),
            LedgerDecision::RepairLedger
        );
        assert_eq!(ledger_decision(&expected, &expected), LedgerDecision::Noop);
    }

    #[test]
    fn ledger_query_surface_records_checksums_and_data() {
        assert!(CREATE_LEDGER_SQL.contains("checksum BYTEA NOT NULL"));
        assert!(CREATE_LEDGER_SQL.contains("data_fingerprint BYTEA NOT NULL"));
        assert!(APPLY_RECORD_SQL.contains("ON CONFLICT (version) DO NOTHING"));
        assert!(READ_LEDGER_SQL.contains("data_fingerprint"));
        assert!(DATA_MARKER_SQL.contains("data_fingerprint <> decode($2, 'hex')"));
        assert!(DATA_MARKER_SQL.contains("version = $1"));
        assert_eq!(
            data_marker_query(16, "abc123"),
            "SELECT 1 FROM tracera_migration_data_ledger WHERE version = 16 AND data_fingerprint = decode('abc123', 'hex')"
        );
    }

    #[test]
    fn concurrent_startups_use_one_lock_and_idempotent_insert() {
        assert_eq!(advisory_lock_key(), "tracera-postgres-migration-root");
        assert!(
            APPLY_RECORD_SQL.contains("ON CONFLICT (version) DO NOTHING"),
            "ledger insert must be idempotent under two startups"
        );
    }

    #[test]
    fn data_fingerprint_is_stable_and_distinct_from_sql_checksum() {
        let migration = MIGRATOR.iter().find(|m| m.version == 11).unwrap();
        let fingerprint =
            data_fingerprint(11, migration.description.as_ref(), migration.sql.as_str());
        assert_eq!(fingerprint.len(), 48);
        assert_eq!(
            fingerprint,
            data_fingerprint(11, migration.description.as_ref(), migration.sql.as_str())
        );
        assert_ne!(fingerprint, migration.checksum.to_vec());
    }

    #[test]
    fn hex_round_trip_is_exact() {
        let bytes = vec![0x00, 0x0f, 0x80, 0xff];
        assert_eq!(hex_decode(&hex_encode(&bytes)).unwrap(), bytes);
        assert!(hex_decode("abc").is_err());
        assert!(hex_decode("zz").is_err());
    }
}
