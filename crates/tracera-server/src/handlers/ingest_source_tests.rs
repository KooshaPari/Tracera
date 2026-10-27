use super::*;
use axum::{body::Body, http::Request, routing::get, Router};
use std::sync::{
    atomic::{AtomicUsize, Ordering},
    Arc,
};
use tower::ServiceExt;

#[tokio::test]
async fn named_ingest_isolates_configured_producers() {
    const CHILD: &str = "TRACERA_INGEST_ISOLATION_CHILD";
    if std::env::var_os(CHILD).is_none() {
        // Isolate environment configuration from concurrently running tests.
        let output = std::process::Command::new(std::env::current_exe().unwrap())
            .args(["named_ingest_isolates_configured_producers", "--nocapture"])
            .env(CHILD, "1")
            .env("GITHUB_TOKEN", "invalid\nheader")
            .env("GITHUB_REPO", "fixture/foreign")
            .env("JIRA_URL", "http://127.0.0.1:1")
            .env("JIRA_EMAIL", "fixture@example.invalid")
            .env("JIRA_API_TOKEN", "fixture")
            .env("JIRA_PROJECT_KEY", "FOREIGN")
            .output()
            .unwrap();
        assert!(
            output.status.success(),
            "{}\n{}",
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        );
        return;
    }

    let requests = Arc::new(AtomicUsize::new(0));
    let agents_count = requests.clone();
    let tasks_count = requests.clone();
    let upstream = Router::new()
        .route(
            "/api/agents",
            get(move || async move {
                agents_count.fetch_add(1, Ordering::SeqCst);
                Json(serde_json::json!([{"id":"one","name":"selected-agent"}]))
            }),
        )
        .route(
            "/api/tasks",
            get(move || async move {
                tasks_count.fetch_add(1, Ordering::SeqCst);
                Json(serde_json::json!([{"id":"two","name":"selected-task"}]))
            }),
        );
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
    std::env::set_var(
        "AGCORD_URL",
        format!("http://{}", listener.local_addr().unwrap()),
    );
    let (shutdown, stopped) = tokio::sync::oneshot::channel::<()>();
    let server = tokio::spawn(async move {
        axum::serve(listener, upstream)
            .with_graceful_shutdown(async {
                stopped.await.ok();
            })
            .await
            .unwrap();
    });
    let pool = sqlx::sqlite::SqlitePoolOptions::new()
        .max_connections(1)
        .connect("sqlite::memory:")
        .await
        .unwrap();
    sqlx::migrate!("./migrations-sqlite")
        .run(&pool)
        .await
        .unwrap();
    let store: Arc<dyn crate::store::Store> = Arc::new(crate::sqlite_store::SqliteStore::new(pool));
    let state = AppState {
        version: "test".into(),
        backend: "sqlite",
        started_at: std::time::Instant::now(),
        store: store.clone(),
        workos_client: tracera_workos::WorkOSClient::default_for_router(),
        cache: None,
        neo4j: None,
        r2: None,
        frontend: crate::FrontendState::Disabled,
        frontend_dist: std::path::PathBuf::new(),
    };
    let app = Router::new()
        .route("/ingest/agileplus", axum::routing::post(ingest_agileplus))
        .with_state(state);
    let response = tokio::time::timeout(
        std::time::Duration::from_secs(5),
        app.oneshot(
            Request::builder()
                .method("POST")
                .uri("/ingest/agileplus")
                .header("content-type", "application/json")
                .body(Body::from("{}"))
                .unwrap(),
        ),
    )
    .await
    .unwrap()
    .unwrap();
    assert_eq!(response.status(), axum::http::StatusCode::OK);
    assert_eq!(requests.load(Ordering::SeqCst), 2);
    let stories = store.list_stories().await.unwrap();
    assert_eq!(stories.len(), 2);
    assert!(stories
        .iter()
        .all(|story| story.id.starts_with("story-agcord-")));
    let evidence = store.list_evidence().await.unwrap();
    assert_eq!(evidence.len(), 2);
    assert!(evidence
        .iter()
        .all(|item| item.metadata["source"] == "agcord"));

    // Missing the selected producer must not fall through to configured foreign sources.
    std::env::remove_var("JIRA_URL");
    assert!(matches!(
        ingest::ingest_live_source(&store, ingest::IngestSource::Jira).await,
        Err(ingest::IngestError::NoSourceConfigured)
    ));
    assert_eq!(requests.load(Ordering::SeqCst), 2);
    assert!(ingest::ingest_live(&store).await.is_err());
    assert_eq!(requests.load(Ordering::SeqCst), 2);
    assert_eq!(store.list_stories().await.unwrap().len(), 2);
    shutdown.send(()).unwrap();
    server.await.unwrap();
}
