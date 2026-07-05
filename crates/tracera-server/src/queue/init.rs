//! TRC-PHENO-010: Init / seed.

use sqlx::{Pool, Sqlite};
use thiserror::Error;

use crate::queue::sqlite_init::{open_with_wal, run_migrations, SqliteInitError};

#[derive(Debug, Error)]
pub enum InitError {
    #[error("sqlite init: {0}")]
    Sqlite(#[from] SqliteInitError),
    #[error("sqlx error: {0}")]
    Sqlx(#[from] sqlx::Error),
}

pub const DEFAULT_AGENT: &str = "default";

pub async fn init_queue(path: &str) -> Result<Pool<Sqlite>, InitError> {
    let pool = open_with_wal(path).await?;
    run_migrations(&pool).await?;
    Ok(pool)
}

pub async fn seed_default_agent(pool: &Pool<Sqlite>) -> Result<(), InitError> {
    sqlx::query(
        "CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'idle',
            last_heartbeat TEXT
         )",
    )
    .execute(pool).await?;
    let count: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM agents")
        .fetch_one(pool).await?;
    if count.0 == 0 {
        sqlx::query(
            "INSERT INTO agents (id, status, last_heartbeat) VALUES (?, 'active', ?)",
        )
        .bind(DEFAULT_AGENT)
        .bind(chrono::Utc::now().to_rfc3339())
        .execute(pool).await?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn init_and_seed() {
        let rt = tokio::runtime::Runtime::new().unwrap();
        rt.block_on(async {
            let pool = init_queue("sqlite::memory:").await.unwrap();
            seed_default_agent(&pool).await.unwrap();
            let n: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM agents")
                .fetch_one(&pool).await.unwrap();
            assert_eq!(n.0, 1);
        });
    }
}
