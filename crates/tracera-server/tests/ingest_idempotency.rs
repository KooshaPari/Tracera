//! Store-level transaction and idempotency tests for ingest.
//!
//! These run against the real SQLite migrations and the `Store` trait, which is
//! the same persistence path every ingest handler funnels through.

use chrono::{TimeZone, Utc};
use serde_json::json;
use sqlx::{sqlite::SqlitePoolOptions, SqlitePool};

use tracera_server::sqlite_store::SqliteStore;
use tracera_server::store::{IngestEvidence, IngestRecord, IngestTraceLink, Store};

async fn mem_store() -> SqliteStore {
    let pool: SqlitePool = SqlitePoolOptions::new()
        .max_connections(1)
        .connect("sqlite::memory:")
        .await
        .expect("open in-memory sqlite");
    sqlx::migrate!("./migrations-sqlite")
        .run(&pool)
        .await
        .expect("apply sqlite migrations");
    SqliteStore::new(pool)
}

fn now() -> chrono::DateTime<Utc> {
    Utc.timestamp_opt(1_752_000_000, 0).unwrap()
}

fn record(external_id: &str, title: &str, status: &str) -> IngestRecord {
    IngestRecord {
        story_id: format!("story-{external_id}"),
        title: title.to_string(),
        description: format!("closes REQ-001 and SPEC-002 ({external_id})"),
        status: status.to_string(),
        evidence: Some(IngestEvidence {
            id: format!("ev-github-{external_id}"),
            kind: "github_issue".to_string(),
            url: format!("https://example.test/issues/{external_id}"),
            metadata: json!({
                "source": "github",
                "external_id": external_id,
                "status": status,
            }),
        }),
        trace_links: vec![
            IngestTraceLink {
                id: format!("tl-story-{external_id}-REQ-001"),
                target_id: "REQ-001".to_string(),
                relationship: "satisfies".to_string(),
                confidence: 0.8,
                source: "github".to_string(),
            },
            IngestTraceLink {
                id: format!("tl-story-{external_id}-SPEC-002"),
                target_id: "SPEC-002".to_string(),
                relationship: "satisfies".to_string(),
                confidence: 0.8,
                source: "github".to_string(),
            },
        ],
    }
}

#[tokio::test]
async fn repeated_batch_ingest_does_not_duplicate_rows() {
    let store = mem_store().await;
    let batch = vec![record("gh-1", "Fix login", "open")];

    let first = store
        .persist_ingest_batch(batch.clone(), now())
        .await
        .expect("first ingest");
    assert_eq!(first.stories_created, 1);
    assert_eq!(first.evidence_created, 1);
    assert_eq!(first.trace_links_created, 2);

    let second = store
        .persist_ingest_batch(batch, now())
        .await
        .expect("replay ingest");
    assert_eq!(second.stories_created, 0);
    assert_eq!(second.stories_unchanged, 1);
    assert_eq!(second.evidence_created, 0);
    assert_eq!(second.evidence_unchanged, 1);
    assert_eq!(second.trace_links_created, 0);
    assert_eq!(second.trace_links_unchanged, 2);

    assert_eq!(store.list_stories().await.unwrap().len(), 1);
    assert_eq!(store.list_evidence().await.unwrap().len(), 1);
    assert_eq!(
        store
            .list_trace_links_for_artifact("story-gh-1".to_string())
            .await
            .unwrap()
            .len(),
        2
    );
}

#[tokio::test]
async fn replay_updates_changed_story_without_duplicating() {
    let store = mem_store().await;
    store
        .persist_ingest_batch(vec![record("gh-7", "Old title", "open")], now())
        .await
        .expect("first ingest");

    let outcome = store
        .persist_ingest_batch(vec![record("gh-7", "New title", "closed")], now())
        .await
        .expect("replay ingest");
    assert_eq!(outcome.stories_created, 0);
    assert_eq!(outcome.stories_updated, 1);
    assert_eq!(outcome.evidence_updated, 1);

    let stories = store.list_stories().await.unwrap();
    assert_eq!(stories.len(), 1);
    assert_eq!(stories[0].id, "story-gh-7");
    assert_eq!(stories[0].title, "New title");
    assert_eq!(stories[0].status, "closed");
    assert_eq!(store.list_evidence().await.unwrap().len(), 1);
}

#[tokio::test]
async fn batch_rolls_back_every_row_on_write_failure() {
    let store = mem_store().await;

    // Fail the evidence insert for the second record only. The first record's
    // story/evidence/links have already been written inside the transaction
    // when this fires, so a missing rollback would leave partial state.
    sqlx::query(
        "CREATE TRIGGER fail_bomb_evidence BEFORE INSERT ON evidence \
         WHEN NEW.kind = 'bomb_issue' \
         BEGIN SELECT RAISE(ABORT, 'injected evidence failure'); END",
    )
    .execute(&store.pool)
    .await
    .expect("install failure trigger");

    let good = record("gh-1", "good issue", "open");
    let mut bad = record("gh-2", "bad issue", "open");
    bad.evidence.as_mut().unwrap().kind = "bomb_issue".to_string();

    let err = store
        .persist_ingest_batch(vec![good, bad], now())
        .await
        .expect_err("batch must fail");
    assert!(
        err.to_string().contains("injected evidence failure"),
        "unexpected error: {err}"
    );

    assert!(store.list_stories().await.unwrap().is_empty());
    assert!(store.list_evidence().await.unwrap().is_empty());
    assert!(store
        .list_trace_links_for_artifact("story-gh-1".to_string())
        .await
        .unwrap()
        .is_empty());
    assert!(store
        .list_trace_links_for_artifact("story-gh-2".to_string())
        .await
        .unwrap()
        .is_empty());
}

#[tokio::test]
async fn identical_link_with_legacy_random_id_is_not_duplicated() {
    let store = mem_store().await;
    store
        .persist_ingest_batch(vec![record("gh-3", "Legacy link", "open")], now())
        .await
        .expect("first ingest");

    // Simulate a pre-idempotency row: same natural edge, random id, no natural
    // key yet. The transaction must treat the edge as already present.
    let outcome = store
        .persist_ingest_batch(
            vec![IngestRecord {
                story_id: "story-gh-3".to_string(),
                title: "Legacy link".to_string(),
                description: "closes REQ-001 and SPEC-002 (gh-3)".to_string(),
                status: "open".to_string(),
                evidence: None,
                trace_links: vec![IngestTraceLink {
                    id: "tl-legacy-random".to_string(),
                    target_id: "REQ-001".to_string(),
                    relationship: "satisfies".to_string(),
                    confidence: 0.8,
                    source: "github".to_string(),
                }],
            }],
            now(),
        )
        .await
        .expect("replay ingest");
    assert_eq!(outcome.trace_links_created, 0);
    assert_eq!(outcome.trace_links_unchanged, 1);

    assert_eq!(
        store
            .list_trace_links_for_artifact("story-gh-3".to_string())
            .await
            .unwrap()
            .len(),
        2
    );
}
