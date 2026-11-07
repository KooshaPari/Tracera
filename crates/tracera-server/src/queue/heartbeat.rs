//! TRC-PHENO-002: Heartbeat + reclaim.
//!
//! Ported from phenodag v0.3.0 `cmdHeartbeat` and `cmdReclaim` (Go).
//! Reference: github.com/KooshaPari/phenodag/blob/main/phenodag.go (cmdHeartbeat line 1385, cmdReclaim line 1410)

use chrono::{DateTime, Duration, Utc};
use sqlx::{Pool, Sqlite};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum HeartbeatError {
    #[error("database error: {0}")]
    Db(#[from] sqlx::Error),
    #[error("agent is required")]
    MissingAgent,
    #[error("agent {0:?} not found")]
    AgentNotFound(String),
}

#[derive(Debug, Clone, sqlx::FromRow)]
pub struct AgentHeartbeat {
    pub id: String,
    pub last_heartbeat: DateTime<Utc>,
}

/// Record a heartbeat for an agent. Updates `last_heartbeat` to now
/// and marks the agent as `active`.
///
/// SQL semantics (port of phenodag):
/// - UPDATE agents SET last_heartbeat=CURRENT_TIMESTAMP, status='active' WHERE id=?
pub async fn record_heartbeat(pool: &Pool<Sqlite>, agent: &str) -> Result<(), HeartbeatError> {
    if agent.is_empty() {
        return Err(HeartbeatError::MissingAgent);
    }
    let now = Utc::now();
    let res = sqlx::query("UPDATE agents SET last_heartbeat = ?, status = 'active' WHERE id = ?")
        .bind(now.to_rfc3339())
        .bind(agent)
        .execute(pool)
        .await?;
    if res.rows_affected() == 0 {
        return Err(HeartbeatError::AgentNotFound(agent.into()));
    }
    Ok(())
}

/// Reclaim tasks assigned to agents that have not heartbeat'd within
/// `stale_after`. The original phenodag port sets status='ready' and
/// assigned_agent=NULL for any task whose assigned_agent has not
/// heartbeat'd within the staleness window.
///
/// SQL semantics (port of phenodag):
/// - UPDATE tasks SET status='ready', assigned_agent=NULL WHERE assigned_agent=?
/// - for each agent with last_heartbeat < now - stale_after
pub async fn reclaim_stale(
    pool: &Pool<Sqlite>,
    stale_after: Duration,
) -> Result<u64, HeartbeatError> {
    let cutoff = (Utc::now() - stale_after).to_rfc3339();
    // Find stale agents
    let stale_agents: Vec<(String,)> =
        sqlx::query_as("SELECT id FROM agents WHERE last_heartbeat < ?")
            .bind(&cutoff)
            .fetch_all(pool)
            .await?;
    if stale_agents.is_empty() {
        return Ok(0);
    }
    let mut total: u64 = 0;
    for (agent,) in stale_agents {
        let res = sqlx::query(
            "UPDATE tasks SET status = 'ready', assigned_agent = NULL WHERE assigned_agent = ?",
        )
        .bind(&agent)
        .execute(pool)
        .await?;
        total += res.rows_affected();
    }
    Ok(total)
}

#[cfg(test)]
mod tests {
    use super::*;

    async fn make_pool() -> sqlx::SqlitePool {
        let pool = sqlx::SqlitePool::connect("sqlite::memory:").await.unwrap();
        sqlx::query(
            "CREATE TABLE agents (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                last_heartbeat TEXT
             )",
        )
        .execute(&pool)
        .await
        .unwrap();
        sqlx::query(
            "CREATE TABLE tasks (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                assigned_agent TEXT
             )",
        )
        .execute(&pool)
        .await
        .unwrap();
        pool
    }

    #[sqlx::test]
    async fn heartbeat_happy() {
        let pool = make_pool().await;
        sqlx::query("INSERT INTO agents (id, status, last_heartbeat) VALUES (?, ?, ?)")
            .bind("A1")
            .bind("idle")
            .bind("2020-01-01T00:00:00Z")
            .execute(&pool)
            .await
            .unwrap();
        record_heartbeat(&pool, "A1").await.unwrap();
        let (status,): (String,) = sqlx::query_as("SELECT status FROM agents WHERE id = ?")
            .bind("A1")
            .fetch_one(&pool)
            .await
            .unwrap();
        assert_eq!(status, "active");
    }

    #[sqlx::test]
    async fn heartbeat_missing_agent_errors() {
        let pool = make_pool().await;
        let r = record_heartbeat(&pool, "NOPE").await;
        assert!(matches!(r, Err(HeartbeatError::AgentNotFound(_))));
    }

    #[sqlx::test]
    async fn reclaim_stale_releases_old_assigned_tasks() {
        let pool = make_pool().await;
        // Stale agent (heartbeat in 2020)
        sqlx::query("INSERT INTO agents (id, status, last_heartbeat) VALUES (?, ?, ?)")
            .bind("STALE")
            .bind("active")
            .bind("2020-01-01T00:00:00Z")
            .execute(&pool)
            .await
            .unwrap();
        sqlx::query("INSERT INTO tasks (id, status, assigned_agent) VALUES (?, ?, ?)")
            .bind("T1")
            .bind("in_progress")
            .bind("STALE")
            .execute(&pool)
            .await
            .unwrap();
        let n = reclaim_stale(&pool, Duration::minutes(1)).await.unwrap();
        assert_eq!(n, 1);
        let (status, agent): (String, Option<String>) =
            sqlx::query_as("SELECT status, assigned_agent FROM tasks WHERE id = ?")
                .bind("T1")
                .fetch_one(&pool)
                .await
                .unwrap();
        assert_eq!(status, "ready");
        assert_eq!(agent, None);
    }
}
