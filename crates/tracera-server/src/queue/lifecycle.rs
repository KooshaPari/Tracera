//! TRC-PHENO-003: Release / done / fail lifecycle.
//!
//! Ported from phenodag v0.3.0 `cmdRelease`, `cmdDone`, `cmdFail` (Go).
//! Reference: github.com/KooshaPari/phenodag/blob/main/phenodag.go

use chrono::Utc;
use sqlx::{Pool, Sqlite};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum LifecycleError {
    #[error("database error: {0}")]
    Db(#[from] sqlx::Error),
    #[error("agent and task are required")]
    MissingArgs,
    #[error("task {0:?} not assigned to {1:?}")]
    NotAssigned(String, String),
}

/// Release a task. Sets status back to 'ready' and clears the assigned agent.
///
/// SQL semantics (port of phenodag cmdRelease):
/// - UPDATE tasks SET status='ready', assigned_agent=NULL, updated_at=? WHERE id=? AND assigned_agent=?
pub async fn release_task(
    pool: &Pool<Sqlite>,
    task_id: &str,
    agent: &str,
) -> Result<(), LifecycleError> {
    if task_id.is_empty() || agent.is_empty() {
        return Err(LifecycleError::MissingArgs);
    }
    let now = Utc::now().to_rfc3339();
    let res = sqlx::query(
        "UPDATE tasks SET status = 'ready', assigned_agent = NULL, updated_at = ? \
         WHERE id = ? AND assigned_agent = ?",
    )
    .bind(&now)
    .bind(task_id)
    .bind(agent)
    .execute(pool)
    .await?;
    if res.rows_affected() == 0 {
        return Err(LifecycleError::NotAssigned(task_id.into(), agent.into()));
    }
    sqlx::query("DELETE FROM claims WHERE task_id = ?")
        .bind(task_id)
        .execute(pool)
        .await?;
    Ok(())
}

/// Mark a task as `done`. Removes its claim row.
///
/// SQL semantics (port of phenodag cmdDone):
/// - tx.Exec: UPDATE tasks SET status='done', updated_at=? WHERE id=? AND assigned_agent=?
/// - tx.Exec: DELETE FROM claims WHERE task_id=?
pub async fn complete_task(
    pool: &Pool<Sqlite>,
    task_id: &str,
    agent: &str,
) -> Result<(), LifecycleError> {
    if task_id.is_empty() || agent.is_empty() {
        return Err(LifecycleError::MissingArgs);
    }
    let now = Utc::now().to_rfc3339();
    let mut tx = pool.begin().await?;
    let res = sqlx::query(
        "UPDATE tasks SET status = 'done', updated_at = ? \
         WHERE id = ? AND assigned_agent = ?",
    )
    .bind(&now)
    .bind(task_id)
    .bind(agent)
    .execute(&mut *tx)
    .await?;
    if res.rows_affected() == 0 {
        tx.rollback().await.ok();
        return Err(LifecycleError::NotAssigned(task_id.into(), agent.into()));
    }
    sqlx::query("DELETE FROM claims WHERE task_id = ?")
        .bind(task_id)
        .execute(&mut *tx)
        .await?;
    tx.commit().await?;
    Ok(())
}

/// Mark a task as `failed` (non-transactional in original phenodag).
///
/// SQL semantics (port of phenodag cmdFail):
/// - db.Exec: UPDATE tasks SET status='failed', updated_at=? WHERE id=? AND assigned_agent=?
pub async fn fail_task(
    pool: &Pool<Sqlite>,
    task_id: &str,
    agent: &str,
) -> Result<(), LifecycleError> {
    if task_id.is_empty() || agent.is_empty() {
        return Err(LifecycleError::MissingArgs);
    }
    let now = Utc::now().to_rfc3339();
    let res = sqlx::query(
        "UPDATE tasks SET status = 'failed', updated_at = ? \
         WHERE id = ? AND assigned_agent = ?",
    )
    .bind(&now)
    .bind(task_id)
    .bind(agent)
    .execute(pool)
    .await?;
    if res.rows_affected() == 0 {
        return Err(LifecycleError::NotAssigned(task_id.into(), agent.into()));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    async fn make_pool() -> sqlx::SqlitePool {
        let pool = sqlx::SqlitePool::connect("sqlite::memory:").await.unwrap();
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

    async fn ready_task(pool: &sqlx::SqlitePool, id: &str) {
        sqlx::query("INSERT INTO tasks (id, status) VALUES (?, ?)")
            .bind(id)
            .bind("ready")
            .execute(pool)
            .await
            .unwrap();
    }

    async fn claim_for(pool: &sqlx::SqlitePool, id: &str, agent: &str) {
        sqlx::query(
            "UPDATE tasks SET status = 'in_progress', assigned_agent = ? WHERE id = ?",
        )
        .bind(agent)
        .bind(id)
        .execute(pool)
        .await
        .unwrap();
        sqlx::query("INSERT INTO claims (task_id, agent_id, claimed_at) VALUES (?, ?, ?)")
            .bind(id)
            .bind(agent)
            .bind("2026-07-05T00:00:00Z")
            .execute(pool)
            .await
            .unwrap();
    }

    #[sqlx::test]
    async fn release_returns_to_ready() {
        let pool = make_pool().await;
        ready_task(&pool, "T1").await;
        claim_for(&pool, "T1", "A1").await;
        release_task(&pool, "T1", "A1").await.unwrap();
        let (status, agent,): (String, Option<String>) =
            sqlx::query_as("SELECT status, assigned_agent FROM tasks WHERE id = ?")
                .bind("T1")
                .fetch_one(&pool)
                .await
                .unwrap();
        assert_eq!(status, "ready");
        assert_eq!(agent, None);
    }

    #[sqlx::test]
    async fn done_marks_done_and_clears_claim() {
        let pool = make_pool().await;
        ready_task(&pool, "T1").await;
        claim_for(&pool, "T1", "A1").await;
        complete_task(&pool, "T1", "A1").await.unwrap();
        let (status,): (String,) = sqlx::query_as("SELECT status FROM tasks WHERE id = ?")
            .bind("T1")
            .fetch_one(&pool)
            .await
            .unwrap();
        assert_eq!(status, "done");
        let n: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM claims WHERE task_id = ?")
            .bind("T1")
            .fetch_one(&pool)
            .await
            .unwrap();
        assert_eq!(n.0, 0);
    }

    #[sqlx::test]
    async fn fail_marks_failed() {
        let pool = make_pool().await;
        ready_task(&pool, "T1").await;
        claim_for(&pool, "T1", "A1").await;
        fail_task(&pool, "T1", "A1").await.unwrap();
        let (status,): (String,) = sqlx::query_as("SELECT status FROM tasks WHERE id = ?")
            .bind("T1")
            .fetch_one(&pool)
            .await
            .unwrap();
        assert_eq!(status, "failed");
    }

    #[sqlx::test]
    async fn wrong_agent_errors() {
        let pool = make_pool().await;
        ready_task(&pool, "T1").await;
        claim_for(&pool, "T1", "A1").await;
        let r = complete_task(&pool, "T1", "WRONG").await;
        assert!(matches!(r, Err(LifecycleError::NotAssigned(_, _))));
    }
}
