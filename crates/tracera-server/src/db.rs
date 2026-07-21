use sqlx::{postgres::PgPoolOptions, sqlite::SqlitePoolOptions, PgPool, SqlitePool};
use std::time::Duration;

const POSTGRES_MAX_CONNECTIONS: u32 = 16;
const SQLITE_MAX_CONNECTIONS: u32 = 8;
const ACQUIRE_TIMEOUT: Duration = Duration::from_secs(5);
const IDLE_TIMEOUT: Duration = Duration::from_secs(600);

pub(crate) async fn connect_postgres(url: &str) -> Result<PgPool, sqlx::Error> {
    PgPoolOptions::new()
        .max_connections(POSTGRES_MAX_CONNECTIONS)
        .acquire_timeout(ACQUIRE_TIMEOUT)
        .idle_timeout(Some(IDLE_TIMEOUT))
        .connect(url)
        .await
}

pub(crate) async fn connect_sqlite(url: &str) -> Result<SqlitePool, sqlx::Error> {
    let pool = SqlitePoolOptions::new()
        .max_connections(SQLITE_MAX_CONNECTIONS)
        .acquire_timeout(ACQUIRE_TIMEOUT)
        .idle_timeout(Some(IDLE_TIMEOUT))
        .connect(url)
        .await?;

    if !url.contains(":memory:") {
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

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn sqlite_pool_applies_contention_and_integrity_pragmas() {
        let pool = connect_sqlite("sqlite::memory:").await.unwrap();
        let (busy_timeout,): (i64,) = sqlx::query_as("PRAGMA busy_timeout")
            .fetch_one(&pool)
            .await
            .unwrap();
        let (foreign_keys,): (i64,) = sqlx::query_as("PRAGMA foreign_keys")
            .fetch_one(&pool)
            .await
            .unwrap();
        assert_eq!(busy_timeout, 5000);
        assert_eq!(foreign_keys, 1);
    }
}
