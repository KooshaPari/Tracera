use sqlx::{postgres::PgPoolOptions, sqlite::SqlitePoolOptions, PgPool, SqlitePool};
use std::time::Duration;

const POSTGRES_MAX_CONNECTIONS: u32 = 16;
const SQLITE_MAX_CONNECTIONS: u32 = 8;
const ACQUIRE_TIMEOUT: Duration = Duration::from_secs(5);
const IDLE_TIMEOUT: Duration = Duration::from_secs(600);

pub async fn connect_postgres(url: &str) -> Result<PgPool, sqlx::Error> {
    PgPoolOptions::new()
        .max_connections(POSTGRES_MAX_CONNECTIONS)
        .acquire_timeout(ACQUIRE_TIMEOUT)
        .idle_timeout(Some(IDLE_TIMEOUT))
        .connect(url)
        .await
}

pub async fn connect_sqlite(url: &str) -> Result<SqlitePool, sqlx::Error> {
    let max_connections = if url.contains(":memory:") {
        1
    } else {
        SQLITE_MAX_CONNECTIONS
    };
    let pool = SqlitePoolOptions::new()
        .max_connections(max_connections)
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

    #[tokio::test]
    async fn in_memory_sqlite_uses_one_connection_for_a_shared_schema() {
        let pool = connect_sqlite("sqlite::memory:").await.unwrap();
        assert_eq!(pool.options().get_max_connections(), 1);
        sqlx::query("CREATE TABLE replay_connection_contract (id INTEGER PRIMARY KEY)")
            .execute(&pool)
            .await
            .unwrap();

        let table_name: String = sqlx::query_scalar(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'replay_connection_contract'",
        )
        .fetch_one(&pool)
        .await
        .unwrap();

        assert_eq!(table_name, "replay_connection_contract");
    }
}
