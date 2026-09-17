mod auth;
mod db;
mod events;
mod graph;
mod handlers;
mod health;
mod ingest;
mod memory;
mod middleware;
mod observability;
mod pg_store;
#[cfg(feature = "phenodag-queue")]
mod queue;
mod router;
mod sqlite_store;
mod store;
mod swee;
mod traceability;
mod validation;

use axum::response::IntoResponse;
use axum::Json;
use std::env;
use std::net::SocketAddr;
use std::path::PathBuf;
use std::sync::Arc;
use std::time::Instant;
use tower_http::services::{ServeDir, ServeFile};
use tracing::info;
use tracing_subscriber::EnvFilter;

static PROM_HANDLE: std::sync::OnceLock<metrics_exporter_prometheus::PrometheusHandle> =
    std::sync::OnceLock::new();

const PUBLIC_BIND_MODE_ENV: &str = "TRACERA_PUBLIC_BIND_MODE";
const AUTH_TOKEN_ENV: &str = "TRACERA_AUTH_TOKEN";
const AUTHENTICATED_PROXY_MODE: &str = "authenticated-proxy";
const LOOPBACK_PUBLISHED_MODE: &str = "loopback-published";
const PRIVATE_NETWORK_MODE: &str = "private-network";

use store::Store;

// ---------------------------------------------------------------------------
// App state
// ---------------------------------------------------------------------------
#[derive(Clone)]
#[allow(dead_code)]
pub(crate) struct AppState {
    pub(crate) version: String,
    pub(crate) backend: &'static str,
    pub(crate) started_at: Instant,
    pub(crate) store: Arc<dyn Store>,
    pub(crate) workos_client: tracera_workos::WorkOSClient,
    pub(crate) cache: Option<Arc<tracera_server::cache::CacheClient>>,
    pub(crate) neo4j: Option<Arc<tracera_server::neo4j::Neo4jClient>>,
    pub(crate) r2: Option<Arc<tracera_server::r2::R2Client>>,
}

impl axum::extract::FromRef<AppState> for tracera_workos::WorkOSClient {
    fn from_ref(state: &AppState) -> Self {
        state.workos_client.clone()
    }
}

fn validate_bind_address(
    addr: SocketAddr,
    public_bind_mode: Option<&str>,
    auth_token: Option<&str>,
) -> Result<(), String> {
    if addr.ip().is_loopback() {
        return Ok(());
    }
    if !matches!(
        public_bind_mode,
        Some(AUTHENTICATED_PROXY_MODE | LOOPBACK_PUBLISHED_MODE | PRIVATE_NETWORK_MODE)
    ) {
        return Err(format!(
            "refusing non-loopback bind to {addr}; set {PUBLIC_BIND_MODE_ENV} to an explicit authenticated-proxy, loopback-published, or private-network deployment mode"
        ));
    }
    if auth_token.is_some_and(|token| !token.is_empty()) {
        return Ok(());
    }
    Err(format!(
        "refusing non-loopback bind to {addr}; {AUTH_TOKEN_ENV} must contain a bearer token"
    ))
}

// ---------------------------------------------------------------------------
// Response helpers
// ---------------------------------------------------------------------------
#[derive(serde::Serialize)]
pub(crate) struct ErrorResponse {
    pub(crate) error: &'static str,
}

pub(crate) fn bad_request(field: &'static str) -> (axum::http::StatusCode, Json<ErrorResponse>) {
    (
        axum::http::StatusCode::BAD_REQUEST,
        Json(ErrorResponse { error: field }),
    )
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------
#[derive(serde::Serialize)]
pub(crate) struct AuthMeUser {
    pub(crate) id: String,
    pub(crate) email: String,
    pub(crate) name: String,
    pub(crate) role: String,
}

pub(crate) async fn auth_me(
    axum_extra::typed_header::TypedHeader(authorization): axum_extra::typed_header::TypedHeader<
        headers::Authorization<headers::authorization::Bearer>,
    >,
) -> Json<AuthMeUser> {
    let token = authorization.token();
    // Use a simple hash of the bearer token as synthetic user id
    let synthetic_id = {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        let mut hasher = DefaultHasher::new();
        token.hash(&mut hasher);
        format!("{:x}", hasher.finish())
    };
    Json(AuthMeUser {
        id: synthetic_id,
        email: "local@tracera.dev".to_string(),
        name: "Local Developer".to_string(),
        role: "admin".to_string(),
    })
}

#[derive(serde::Serialize)]
struct CsrfTokenResponse {
    token: String,
    valid: bool,
}

pub(crate) async fn csrf_token() -> Json<CsrfTokenResponse> {
    Json(CsrfTokenResponse {
        token: middleware::issue_csrf_token().await,
        valid: true,
    })
}

// ---------------------------------------------------------------------------
// Prometheus metrics
// ---------------------------------------------------------------------------
pub(crate) async fn prom_metrics_handler() -> impl IntoResponse {
    let recorder = PROM_HANDLE.get_or_init(|| {
        metrics_exporter_prometheus::PrometheusBuilder::new()
            .install_recorder()
            .expect("install prometheus recorder")
            .clone()
    });
    (
        [(
            axum::http::header::CONTENT_TYPE,
            "text/plain; version=0.0.4",
        )],
        recorder.render(),
    )
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::from_default_env().add_directive("tracera_server=info".parse().unwrap()),
        )
        .init();

    let database_url = env::var("DATABASE_URL").unwrap_or_else(|_| {
        eprintln!(
            "FATAL: DATABASE_URL environment variable is not set.\n\
             Set it to a connection string, e.g.:\n\
             DATABASE_URL=postgres://user:pass@localhost:5432/tracera\n\
             DATABASE_URL=sqlite:///path/to/tracera.db\n\
             DATABASE_URL=sqlite::memory:"
        );
        std::process::exit(1);
    });

    let (store, backend): (Arc<dyn Store>, &'static str) =
        if database_url.starts_with("postgres://") || database_url.starts_with("postgresql://") {
            info!("Backend: Postgres (server tier)");
            let pool = db::connect_postgres(&database_url)
                .await
                .unwrap_or_else(|e| {
                    eprintln!("FATAL: Cannot connect to Postgres: {e}");
                    std::process::exit(1);
                });
            sqlx::migrate!("./migrations-postgres")
                .run(&pool)
                .await
                .unwrap_or_else(|e| {
                    eprintln!("FATAL: Postgres migration failed: {e}");
                    std::process::exit(1);
                });
            info!("Postgres migrations applied successfully");
            (Arc::new(pg_store::PgStore::new(pool)), "postgres")
        } else if database_url.starts_with("sqlite://")
            || database_url.starts_with("sqlite:")
            || database_url.ends_with(".db")
        {
            info!("Backend: SQLite (on-device tier)");
            let pool = db::connect_sqlite(&database_url).await.unwrap_or_else(|e| {
                eprintln!("FATAL: Cannot open SQLite: {e}");
                std::process::exit(1);
            });
            sqlx::migrate!("./migrations-sqlite")
                .run(&pool)
                .await
                .unwrap_or_else(|e| {
                    eprintln!("FATAL: SQLite migration failed: {e}");
                    std::process::exit(1);
                });
            info!("SQLite migrations applied successfully");
            (Arc::new(sqlite_store::SqliteStore::new(pool)), "sqlite")
        } else {
            eprintln!("FATAL: Unrecognised DATABASE_URL scheme.");
            std::process::exit(1);
        };

    let state = AppState {
        version: env!("CARGO_PKG_VERSION").to_string(),
        backend,
        started_at: Instant::now(),
        store,
        workos_client: tracera_workos::WorkOSClient::default_for_router(),
        cache: tracera_server::cache::CacheClient::from_env().map(Arc::new),
        neo4j: tracera_server::neo4j::Neo4jClient::from_env().await.map(Arc::new),
        r2: tracera_server::r2::R2Client::from_env().map(Arc::new),
    };

    let auth_token = env::var(AUTH_TOKEN_ENV)
        .ok()
        .filter(|token| !token.is_empty())
        .map(Arc::<str>::from);
    let app = router::build_router_with_auth(state, auth_token.clone());

    let frontend_dist = env::var("TRACERA_FRONTEND_DIST")
        .map(PathBuf::from)
        .unwrap_or_else(|_| PathBuf::from("frontend/dist"));
    let index_html = frontend_dist.join("index.html");
    let serve_dir = ServeDir::new(&frontend_dist).fallback(ServeFile::new(&index_html));
    let app = app.fallback_service(serve_dir);

    let addr = env::var("TRACERA_BIND_ADDR")
        .ok()
        .and_then(|v| v.parse().ok())
        .or_else(|| {
            env::var("PORT")
                .ok()
                .and_then(|p| p.parse().ok())
                .map(|port| SocketAddr::from(([0, 0, 0, 0], port)))
        })
        .unwrap_or_else(|| SocketAddr::from(([127, 0, 0, 1], 8080)));

    let public_bind_mode = env::var(PUBLIC_BIND_MODE_ENV).ok();
    if let Err(error) =
        validate_bind_address(addr, public_bind_mode.as_deref(), auth_token.as_deref())
    {
        eprintln!("FATAL: {error}");
        std::process::exit(1);
    }

    let listener = tokio::net::TcpListener::bind(addr)
        .await
        .unwrap_or_else(|error| {
            eprintln!("FATAL: cannot bind to {addr}: {error}");
            std::process::exit(1);
        });
    info!("tracera-server listening on {addr}");
    if let Err(error) = axum::serve(listener, app).await {
        eprintln!("FATAL: server stopped: {error}");
        std::process::exit(1);
    }
}
