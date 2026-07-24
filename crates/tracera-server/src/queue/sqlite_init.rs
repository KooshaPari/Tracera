//! TRC-PHENO-005: WAL SQLite init.

use sqlx::{sqlite::SqlitePoolOptions, Pool, Sqlite};
use std::time::Duration;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum SqliteInitError {
    #[error("sqlx error: {0}")]
    Sqlx(#[from] sqlx::Error),
}

/// Open a SQLite pool with WAL mode and busy_timeout.
/// In-memory databases cannot use WAL; the pragmas are skipped for those.
pub async fn open_with_wal(path: &str) -> Result<Pool<Sqlite>, SqliteInitError> {
    let pool = SqlitePoolOptions::new()
        .max_connections(8)
        .acquire_timeout(Duration::from_secs(5))
        .idle_timeout(Some(Duration::from_secs(600)))
        .connect(path)
        .await?;
    if !path.contains(":memory:") {
        sqlx::query("PRAGMA journal_mode = WAL")
            .execute(&pool)
            .await?;
        sqlx::query("PRAGMA synchronous = NORMAL")
            .execute(&pool)
            .await?;
    }
    sqlx::query("PRAGMA busy_timeout = 5000")
        .execute(&pool)
        .await?;
    sqlx::query("PRAGMA foreign_keys = ON")
        .execute(&pool)
        .await?;
    Ok(pool)
}

pub async fn run_migrations(_pool: &Pool<Sqlite>) -> Result<(), SqliteInitError> {
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn open_in_memory_works() {
        let rt = tokio::runtime::Runtime::new().unwrap();
        rt.block_on(async {
            let pool = open_with_wal("sqlite::memory:").await.unwrap();
            // busy_timeout should be set
            let timeout: (i64,) = sqlx::query_as("PRAGMA busy_timeout")
                .fetch_one(&pool)
                .await
                .unwrap();
            assert_eq!(timeout.0, 5000);
        });
    }
}
