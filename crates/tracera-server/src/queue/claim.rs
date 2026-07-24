//! TRC-PHENO-001: Atomic SQLite claim.
//!
//! Ported from phenodag v0.3.0 `cmdClaim` (Go).
//! Reference: github.com/KooshaPari/phenodag/blob/main/phenodag.go (cmdClaim, line 1313)

use chrono::Utc;
use sqlx::{Pool, Sqlite, Transaction};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum ClaimError {
    #[error("database error: {0}")]
    Db(#[from] sqlx::Error),
    #[error("agent and task are required")]
    MissingArgs,
    #[error("task {0:?} not found")]
    TaskNotFound(String),
    #[error("task {0:?} not in 'ready' state")]
    NotReady(String),
}

/// Atomic claim. Marks a task as `in_progress` for the given agent.
///
/// SQL semantics (port of phenodag):
/// - tx.Exec: UPDATE tasks SET status='in_progress', assigned_agent=?, updated_at=? WHERE id=?
///   AND status='ready' (atomic via the row-level write)
pub async fn atomic_claim(
    pool: &Pool<Sqlite>,
    task_id: &str,
    agent: &str,
) -> Result<(), ClaimError> {
    if task_id.is_empty() || agent.is_empty() {
        return Err(ClaimError::MissingArgs);
    }
    let now = Utc::now().to_rfc3339();
    let mut tx: Transaction<'_, Sqlite> = pool.begin().await?;
    let res = sqlx::query(
        "UPDATE tasks SET status = 'in_progress', assigned_agent = ?, updated_at = ? \
         WHERE id = ? AND status = 'ready'",
    )
    .bind(agent)
    .bind(&now)
    .bind(task_id)
    .execute(&mut *tx)
    .await?;
    if res.rows_affected() == 0 {
        // Either task doesn't exist or wasn't 'ready'.
        let exists: Option<(String,)> = sqlx::query_as("SELECT status FROM tasks WHERE id = ?")
            .bind(task_id)
            .fetch_optional(&mut *tx)
            .await?;
        tx.rollback().await.ok();
        return match exists {
            None => Err(ClaimError::TaskNotFound(task_id.into())),
            Some((status,)) if status != "ready" => Err(ClaimError::NotReady(task_id.into())),
            _ => Err(ClaimError::TaskNotFound(task_id.into())),
        };
    }
    sqlx::query("INSERT OR REPLACE INTO claims (task_id, agent_id, claimed_at) VALUES (?, ?, ?)")
        .bind(task_id)
        .bind(agent)
        .bind(&now)
        .execute(&mut *tx)
        .await?;
    tx.commit().await?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    async fn make_pool() -> SqlitePool {
        let pool = SqlitePool::connect("sqlite::memory:").await.unwrap();
        sqlx::query(
            "CREATE TABLE tasks (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                assigned_agent TEXT,
                updated_at TEXT
             )",
        )
        .execute(&pool)
        .await
        .unwrap();
        sqlx::query(
            "CREATE TABLE claims (
                task_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                claimed_at TEXT NOT NULL
             )",
        )
        .execute(&pool)
        .await
        .unwrap();
        pool
    }

    #[sqlx::test]
    async fn claim_happy_path() {
        let pool = make_pool().await;
        sqlx::query("INSERT INTO tasks (id, status) VALUES (?, ?)")
            .bind("T1")
            .bind("ready")
            .execute(&pool)
            .await
            .unwrap();
        atomic_claim(&pool, "T1", "agent-a").await.unwrap();
        let (status, agent): (String, Option<String>) =
            sqlx::query_as("SELECT status, assigned_agent FROM tasks WHERE id = ?")
                .bind("T1")
                .fetch_one(&pool)
                .await
                .unwrap();
        assert_eq!(status, "in_progress");
        assert_eq!(agent.as_deref(), Some("agent-a"));
    }

    #[sqlx::test]
    async fn claim_twice_second_fails() {
        let pool = make_pool().await;
        sqlx::query("INSERT INTO tasks (id, status) VALUES (?, ?)")
            .bind("T1")
            .bind("ready")
            .execute(&pool)
            .await
            .unwrap();
        atomic_claim(&pool, "T1", "agent-a").await.unwrap();
        let r = atomic_claim(&pool, "T1", "agent-b").await;
        assert!(r.is_err());
    }

    #[sqlx::test]
    async fn claim_missing_task() {
        let pool = make_pool().await;
        let r = atomic_claim(&pool, "NOPE", "agent-a").await;
        assert!(matches!(r, Err(ClaimError::TaskNotFound(_))));
    }
}
