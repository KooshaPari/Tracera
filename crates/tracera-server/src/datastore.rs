//! Canonical database connection and migration entry points for non-HTTP consumers.

use thiserror::Error;

use crate::{db, pg_store::PgStore, sqlite_store::SqliteStore};

#[derive(Debug, Error)]
pub enum DatastoreError {
    #[error("database connection failed: {0}")]
    Connect(#[from] sqlx::Error),
    #[error("database migration failed: {0}")]
    Migrate(#[from] sqlx::migrate::MigrateError),
}

/// Connect to PostgreSQL, apply the canonical migrations, and return its store.
pub async fn connect_postgres(url: &str) -> Result<PgStore, DatastoreError> {
    let pool = db::connect_postgres(url).await?;
    sqlx::migrate!("./migrations").run(&pool).await?;
    Ok(PgStore::new(pool))
}

/// Connect to SQLite, apply the canonical migrations, and return its store.
pub async fn connect_sqlite(url: &str) -> Result<SqliteStore, DatastoreError> {
    let pool = db::connect_sqlite(url).await?;
    sqlx::migrate!("./migrations-sqlite").run(&pool).await?;
    Ok(SqliteStore::new(pool))
}
