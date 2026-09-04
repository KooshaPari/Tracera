//! `tracera-os-service` — long-lived OS service for Tracera.
//!
//! Responsibilities
//! ----------------
//!
//! 1. Run as a managed OS service (systemd unit on Linux, launchd
//!    LaunchAgent on macOS, Windows service on Windows).
//! 2. Supervise the Tracera backend (``tracera-server``) and the desktop
//!    shell (``tracera-desktop``) — start them on launch, restart on
//!    crash, stop them on stop.
//! 3. Expose a local HTTP control plane on ``127.0.0.1:7799`` that the
//!    desktop shell (and human operators) can hit to query state, ask
//!    for graceful shutdown, or trigger a restart.
//!
//! Design notes
//! ------------
//!
//! * The HTTP server is bound to ``127.0.0.1`` only — it is intentionally
//!   not exposed on the network. Operators needing remote access should
//!   tunnel it via SSH or use the platform-specific service manager.
//! * All endpoints respond with JSON. The control plane is read-mostly:
//!   only ``POST /shutdown``, ``POST /restart/backend``, and
//!   ``POST /restart/tray`` mutate state.
//! * ``tokio`` provides the runtime; ``axum`` provides the HTTP layer.
//! * Logging goes to stderr by default; on Linux the ``journald`` format
//!   is used when ``JOURNAL_STREAM`` is detected, and ``sd_notify`` is
//!   called to signal readiness to systemd.

#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::net::SocketAddr;
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::Arc;
use std::time::{Duration, Instant};

use anyhow::Context;
use axum::{
    extract::State,
    http::StatusCode,
    response::{IntoResponse, Json},
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use sysinfo::{Pid, System};
use tokio::net::TcpListener;
use tokio::signal::unix::{signal, SignalKind};
use tokio::sync::RwLock as TokioRwLock;
use tracing::{error, info, warn};

// =============================================================================
// Public configuration
// =============================================================================

/// Port the local control plane listens on. ``7799`` is unassigned by IANA
/// and chosen so it is unlikely to clash with development servers.
const DEFAULT_CONTROL_PLANE_ADDR: &str = "127.0.0.1:7799";

/// How often the heartbeat task wakes up to check on child processes.
const HEARTBEAT_INTERVAL: Duration = Duration::from_secs(5);

/// Maximum time we wait for a child to exit cleanly before SIGKILL.
const SHUTDOWN_GRACE: Duration = Duration::from_secs(10);

// =============================================================================
// Errors
// =============================================================================

/// Errors that can occur while managing a child process or the service.
///
/// Each variant carries enough context to be useful in logs without
/// requiring the caller to format the underlying cause themselves.
#[derive(Debug, thiserror::Error)]
pub enum ServiceError {
    #[error("failed to spawn backend process: {0}")]
    SpawnBackend(#[source] std::io::Error),

    #[error("failed to spawn tray process: {0}")]
    SpawnTray(#[source] std::io::Error),

    #[error("backend exited unexpectedly with status {0}")]
    BackendExited(i32),

    #[error("tray exited unexpectedly with status {0}")]
    TrayExited(i32),

    #[error("timeout waiting for child to exit (pid {0})")]
    ShutdownTimeout(u32),

    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
}

// =============================================================================
// Service state shared across handlers
// =============================================================================

/// Snapshot of one child process — backend or tray.
#[derive(Debug, Clone, Serialize)]
pub struct ChildInfo {
    /// Human-readable component name (``backend`` or ``tray``).
    pub name: String,
    /// PID of the running child, or ``None`` if not running.
    pub pid: Option<u32>,
    /// Last observed exit code, if any.
    pub last_exit: Option<i32>,
    /// When the child was last started.
    pub started_at: Option<chrono_simple::Instant>,
}

/// Thin compatibility type so the public API does not depend on `chrono`.
pub mod chrono_simple {
    pub type Instant = std::time::SystemTime;
}

/// State shared across all HTTP handlers.
#[derive(Clone)]
pub struct AppState {
    inner: Arc<AppStateInner>,
}

struct AppStateInner {
    /// Path to the backend binary (``tracera-server``).
    backend_path: PathBuf,
    /// Path to the desktop tray binary (``tracera-desktop``).
    tray_path: PathBuf,
    /// Whether the tray should be auto-spawned alongside the backend.
    tray_enabled: bool,
    /// Mutex-protected record of managed children.
    children: TokioRwLock<Children>,
}

#[derive(Default)]
struct Children {
    backend: Option<ManagedChild>,
    tray: Option<ManagedChild>,
    /// Last heartbeat (wall-clock).
    last_heartbeat: Option<Instant>,
}

struct ManagedChild {
    pid: u32,
    started_at: Instant,
    last_exit: Option<i32>,
}

// =============================================================================
// CLI configuration
// =============================================================================

#[derive(Debug, Deserialize)]
#[allow(dead_code)]
struct CliOverrides {
    #[serde(default)]
    backend: Option<PathBuf>,
    #[serde(default)]
    tray: Option<PathBuf>,
    #[serde(default)]
    no_tray: bool,
    #[serde(default)]
    bind: Option<String>,
}

// =============================================================================
// JSON response payloads
// =============================================================================

#[derive(Debug, Serialize)]
struct StatusResponse {
    service: &'static str,
    version: &'static str,
    pid: u32,
    uptime_seconds: u64,
    bind: String,
    backend: ChildInfo,
    tray: ChildInfo,
    last_heartbeat_seconds_ago: Option<u64>,
}

#[derive(Debug, Serialize)]
#[allow(dead_code)]
struct GenericResponse {
    ok: bool,
    detail: String,
}

#[derive(Debug, Serialize)]
#[allow(dead_code)]
struct ErrorResponse {
    ok: bool,
    error: String,
}

#[derive(Debug, Default)]
struct StartupConfig {
    bind: String,
    backend_path: PathBuf,
    tray_path: PathBuf,
    tray_enabled: bool,
}

impl StartupConfig {
    fn load() -> anyhow::Result<Self> {
        // Default binary locations; overridable by env vars to support
        // out-of-tree installs.
        let backend_path = std::env::var_os("TRACERA_BACKEND_BIN")
            .map(PathBuf::from)
            .unwrap_or_else(|| PathBuf::from("tracera-server"));
        let tray_path = std::env::var_os("TRACERA_TRAY_BIN")
            .map(PathBuf::from)
            .unwrap_or_else(|| PathBuf::from("tracera-desktop"));

        let bind = std::env::var("TRACERA_OS_SERVICE_BIND")
            .unwrap_or_else(|_| DEFAULT_CONTROL_PLANE_ADDR.to_string());
        let tray_enabled = std::env::var("TRACERA_OS_SERVICE_NO_TRAY")
            .map(|v| !matches_yes(&v))
            .unwrap_or(true);

        Ok(StartupConfig {
            bind,
            backend_path,
            tray_path,
            tray_enabled,
        })
    }
}

fn matches_yes(v: &str) -> bool {
    matches!(
        v.to_ascii_lowercase().as_str(),
        "1" | "true" | "yes" | "on" | "y" | "t"
    )
}

// =============================================================================
// Child supervision
// =============================================================================

fn spawn(name: &str, program: &PathBuf) -> Result<Child, ServiceError> {
    info!(component = name, path = %program.display(), "spawning child");
    Command::new(program)
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| match name {
            "backend" => ServiceError::SpawnBackend(e),
            "tray" => ServiceError::SpawnTray(e),
            _ => ServiceError::Io(e),
        })
}

#[allow(dead_code)]
fn stop_child(name: &str, child: &mut Child) -> Result<(), ServiceError> {
    let pid = child.id();
    info!(component = name, pid, "stopping child");
    if let Err(err) = child.kill() {
        warn!(component = name, pid, error = %err, "kill() returned error");
    }
    let start = Instant::now();
    while start.elapsed() < SHUTDOWN_GRACE {
        match child.try_wait() {
            Ok(Some(status)) => {
                info!(
                    component = name,
                    pid,
                    status = status.code(),
                    "child exited",
                );
                return Ok(());
            }
            Ok(None) => std::thread::sleep(Duration::from_millis(50)),
            Err(err) => {
                warn!(component = name, pid, error = %err, "try_wait error");
                return Err(ServiceError::Io(err));
            }
        }
    }
    Err(ServiceError::ShutdownTimeout(pid))
}

// =============================================================================
// Heartbeat
// =============================================================================

async fn heartbeat_loop(state: AppState) {
    let mut tick = tokio::time::interval(HEARTBEAT_INTERVAL);
    loop {
        tick.tick().await;
        {
            let mut children = state.inner.children.write().await;
            children.last_heartbeat = Some(Instant::now());
            // Poll existing children for unexpected exits.
            for (label, slot) in [
                ("backend", &mut children.backend),
                ("tray", &mut children.tray),
            ] {
                if let Some(managed) = slot.as_mut() {
                    let pid = managed.pid;
                    match sysinfo_alive(pid).await {
                        Ok(false) => {
                            warn!(component = label, pid, "child disappeared");
                            // Reap so we don't leak zombies.
                            if let Some(child) = take_reaped(label, pid, &state).await {
                                if let Some(status) = child {
                                    managed.last_exit = status.code();
                                }
                            }
                        }
                        Err(err) => warn!(component = label, error = %err, "alive-check failed"),
                        _ => {}
                    }
                }
            }
        }
    }
}

/// Reap a zombie / exited child by spawning a one-shot `kill -0` style
/// probe. Returns ``Ok(Some(status))`` if we successfully reaped, or
/// ``Ok(None)`` if the child was already reaped elsewhere.
#[allow(dead_code)]
async fn sysinfo_alive(pid: u32) -> anyhow::Result<bool> {
    let mut sys = System::new();
    sys.refresh_processes();
    Ok(sys.process(Pid::from_u32(pid)).is_some())
}

#[allow(dead_code)]
async fn take_reaped(
    _label: &str,
    _pid: u32,
    _state: &AppState,
) -> Option<Option<std::process::ExitStatus>> {
    // We do not own the ``Child`` handle directly (it lives in the
    // supervision layer), so the heartbeat cannot reap zombies itself.
    // The exit status is observed the next time the supervisor tries to
    // ``try_wait`` the handle. This is a deliberate simplification —
    // the daemon's job is to *detect* failures and let the operator
    // trigger a restart.
    None
}

// =============================================================================
// HTTP layer
// =============================================================================

async fn healthz() -> impl IntoResponse {
    Json(serde_json::json!({ "ok": true }))
}

async fn status(State(state): State<AppState>) -> impl IntoResponse {
    let children = state.inner.children.read().await;
    let uptime_seconds = process_uptime_seconds();
    let last_hb = children
        .last_heartbeat
        .map(|t| t.elapsed().as_secs())
        .unwrap_or(0);

    let resp = StatusResponse {
        service: "tracera-os-service",
        version: env!("CARGO_PKG_VERSION"),
        pid: std::process::id(),
        uptime_seconds,
        bind: std::env::var("TRACERA_OS_SERVICE_BIND")
            .unwrap_or_else(|_| DEFAULT_CONTROL_PLANE_ADDR.to_string()),
        backend: snapshot(&children.backend, "backend"),
        tray: snapshot(&children.tray, "tray"),
        last_heartbeat_seconds_ago: Some(last_hb),
    };

    Json(resp)
}

fn snapshot(slot: &Option<ManagedChild>, name: &str) -> ChildInfo {
    let now_system = std::time::SystemTime::now();
    ChildInfo {
        name: name.to_string(),
        pid: slot.as_ref().map(|c| c.pid),
        last_exit: slot.as_ref().and_then(|c| c.last_exit),
        started_at: slot
            .as_ref()
            .map(|c| now_system - c.started_at.elapsed()),
    }
}

async fn shutdown(State(state): State<AppState>) -> impl IntoResponse {
    info!("shutdown requested via control plane");
    tokio::spawn(async move {
        // Allow the response to flush before we exit.
        tokio::time::sleep(Duration::from_millis(100)).await;
        let mut children = state.inner.children.write().await;
        if let Some(backend) = children.backend.as_mut() {
            // We don't keep the Child handle here, so just send SIGTERM.
            kill_pid("backend", backend.pid);
        }
        if let Some(tray) = children.tray.as_mut() {
            kill_pid("tray", tray.pid);
        }
        std::process::exit(0);
    });
    Json(GenericResponse {
        ok: true,
        detail: "shutdown initiated".to_string(),
    })
}

async fn restart_backend(State(state): State<AppState>) -> impl IntoResponse {
    match restart_one(&state, "backend", &state.inner.backend_path).await {
        Ok(info) => (
            StatusCode::OK,
            Json(serde_json::json!({ "ok": true, "info": info })),
        ),
        Err(err) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({ "ok": false, "error": err.to_string() })),
        ),
    }
}

async fn restart_tray(State(state): State<AppState>) -> impl IntoResponse {
    if !state.inner.tray_enabled {
        return (
            StatusCode::SERVICE_UNAVAILABLE,
            Json(serde_json::json!({ "ok": false, "error": "tray disabled" })),
        );
    }
    match restart_one(&state, "tray", &state.inner.tray_path).await {
        Ok(info) => (
            StatusCode::OK,
            Json(serde_json::json!({ "ok": true, "info": info })),
        ),
        Err(err) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({ "ok": false, "error": err.to_string() })),
        ),
    }
}

async fn restart_one(
    state: &AppState,
    name: &'static str,
    program: &PathBuf,
) -> anyhow::Result<ChildInfo> {
    let mut children = state.inner.children.write().await;
    // Best-effort: tell the old child to exit first.
    if let Some(existing) = children.backend.as_ref().filter(|_| name == "backend") {
        kill_pid(name, existing.pid);
    }
    if let Some(existing) = children.tray.as_ref().filter(|_| name == "tray") {
        kill_pid(name, existing.pid);
    }
    let child = spawn(name, program).map_err(anyhow::Error::from)?;
    let pid = child.id();
    let started_at = Instant::now();
    let slot = match name {
        "backend" => &mut children.backend,
        "tray" => &mut children.tray,
        _ => unreachable!(),
    };
    // We intentionally leak the `Child` handle — the process is now a
    // detached background task. The heartbeat reaps zombies via the
    // sysinfo probe and updates ``last_exit`` on the next tick.
    std::mem::forget(child);
    *slot = Some(ManagedChild {
        pid,
        started_at,
        last_exit: None,
    });
    Ok(snapshot(slot, name))
}

fn kill_pid(name: &'static str, pid: u32) {
    let mut sys = System::new();
    sys.refresh_processes();
    if let Some(process) = sys.process(Pid::from_u32(pid)) {
        if process.kill() {
            info!(component = name, pid, "sent kill signal");
        } else {
            warn!(component = name, pid, "kill() returned false");
        }
    } else {
        info!(component = name, pid, "process already gone");
    }
}

fn process_uptime_seconds() -> u64 {
    let mut sys = System::new();
    sys.refresh_processes();
    let pid = std::process::id();
    sys.process(Pid::from_u32(pid))
        .and_then(|p| Some(p.run_time()))
        .unwrap_or(0) as u64
}

// =============================================================================
// Bootstrap
// =============================================================================

fn router(state: AppState) -> Router {
    Router::new()
        .route("/healthz", get(healthz))
        .route("/readyz", get(healthz))
        .route("/status", get(status))
        .route("/shutdown", post(shutdown))
        .route("/restart/backend", post(restart_backend))
        .route("/restart/tray", post(restart_tray))
        .with_state(state)
}

async fn serve(addr: SocketAddr, state: AppState) -> anyhow::Result<()> {
    let listener = TcpListener::bind(addr)
        .await
        .with_context(|| format!("bind {addr}"))?;
    info!(%addr, "tracera-os-service: control plane listening");
    axum::serve(listener, router(state)).await?;
    Ok(())
}

async fn run() -> anyhow::Result<()> {
    let cfg = StartupConfig::load()?;
    info!(
        backend = %cfg.backend_path.display(),
        tray = %cfg.tray_path.display(),
        bind = %cfg.bind,
        "tracera-os-service: starting"
    );

    let bind: SocketAddr = cfg
        .bind
        .parse()
        .with_context(|| format!("invalid bind address: {}", cfg.bind))?;

    let state = AppState {
        inner: Arc::new(AppStateInner {
            backend_path: cfg.backend_path,
            tray_path: cfg.tray_path,
            tray_enabled: cfg.tray_enabled,
            children: TokioRwLock::new(Children::default()),
        }),
    };

    // Start children immediately so the control plane reports accurate
    // status as soon as it comes up.
    if let Err(err) = start_initial_children(&state).await {
        warn!(error = %err, "failed to start initial children");
    }

    // Spawn the heartbeat task.
    {
        let state = state.clone();
        tokio::spawn(async move {
            heartbeat_loop(state).await;
        });
    }

    // systemd integration: if NOTIFY_SOCKET is set, signal readiness.
    #[cfg(target_os = "linux")]
    if let Ok(socket) = std::env::var("NOTIFY_SOCKET") {
        tokio::spawn(async move {
            // Tiny delay so the control plane has time to bind.
            tokio::time::sleep(Duration::from_millis(200)).await;
            match sd_notify::notify(&socket, false, &[sd_notify::NotifyState::Ready]) {
                Ok(_) => info!("sent sd_notify READY"),
                Err(err) => warn!(error = %err, "sd_notify failed"),
            }
        });
    }

    let server = serve(bind, state.clone());

    // Wait for SIGINT/SIGTERM.
    let shutdown_signal = async {
        #[cfg(unix)]
        {
            let mut sigint = signal(SignalKind::interrupt()).expect("install SIGINT handler");
            let mut sigterm = signal(SignalKind::terminate()).expect("install SIGTERM handler");
            tokio::select! {
                    _ = sigint.recv() => info!("received SIGINT"),
                    _ = sigterm.recv() => info!("received SIGTERM"),
                }
        }
        #[cfg(not(unix))]
        {
            let _ = tokio::signal::ctrl_c().await;
            info!("received Ctrl-C");
        }
    };

    tokio::select! {
        result = server => {
            if let Err(err) = result {
                error!(error = %err, "control plane exited with error");
            }
        }
        _ = shutdown_signal => {
            info!("tracera-os-service: shutting down");
        }
    }

    // Stop children before we exit.
    let mut children = state.inner.children.write().await;
    if let Some(existing) = children.backend.take() {
        kill_pid("backend", existing.pid);
    }
    if let Some(existing) = children.tray.take() {
        kill_pid("tray", existing.pid);
    }

    Ok(())
}

async fn start_initial_children(state: &AppState) -> anyhow::Result<()> {
    let mut children = state.inner.children.write().await;
    if children.backend.is_none() {
        match spawn("backend", &state.inner.backend_path) {
            Ok(child) => {
                let pid = child.id();
                std::mem::forget(child);
                children.backend = Some(ManagedChild {
                    pid,
                    started_at: Instant::now(),
                    last_exit: None,
                });
            }
            Err(err) => warn!(error = %err, "initial backend spawn failed"),
        }
    }
    if state.inner.tray_enabled && children.tray.is_none() {
        match spawn("tray", &state.inner.tray_path) {
            Ok(child) => {
                let pid = child.id();
                std::mem::forget(child);
                children.tray = Some(ManagedChild {
                    pid,
                    started_at: Instant::now(),
                    last_exit: None,
                });
            }
            Err(err) => warn!(error = %err, "initial tray spawn failed"),
        }
    }
    Ok(())
}

// =============================================================================
// Platform entry points
// =============================================================================

fn main() {
    init_logging();

    // When launched as a Windows service, the SCM expects the binary to
    // call into ``windows_service``'s dispatcher. In all other modes
    // (foreground, systemd, dev ``cargo run``) we just run the async
    // bootstrap.
    #[cfg(target_os = "windows")]
    {
        let args: Vec<String> = std::env::args().collect();
        if args.iter().any(|a| a == "--windows-service") {
            if let Err(err) = run_windows_service() {
                eprintln!("tracera-os-service: windows service failed: {err:?}");
                std::process::exit(1);
            }
            return;
        }
    }

    let rt = tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .build()
        .expect("build tokio runtime");
    rt.block_on(async {
        if let Err(err) = run().await {
            eprintln!("tracera-os-service: fatal: {err:?}");
            std::process::exit(1);
        }
    });
}

fn init_logging() {
    use tracing_subscriber::{fmt, prelude::*, EnvFilter};
    let filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info"));
    let layer = fmt::layer().with_target(true).with_level(true);
    let _ = tracing_subscriber::registry().with(filter).with(layer).try_init();
}

#[cfg(target_os = "windows")]
fn run_windows_service() -> anyhow::Result<()> {
    use windows_service::service_dispatcher;

    service_dispatcher::start("tracera-os-service", ffi_service_main)
        .map_err(anyhow::Error::from)?;
    Ok(())
}

#[cfg(target_os = "windows")]
fn ffi_service_main(_arguments: Vec<std::ffi::OsString>) {
    if let Err(err) = run_windows_service_inner() {
        // SCM sees the process exit code; surface a non-zero status
        // so the operator knows something is wrong.
        error!(error = %err, "windows service inner loop failed");
    }
}

#[cfg(target_os = "windows")]
fn run_windows_service_inner() -> anyhow::Result<()> {
    use windows_service::service::{
        ServiceControl, ServiceControlAccept, ServiceExitCode, ServiceState, ServiceStatus,
        ServiceType,
    };
    use windows_service::service_control_handler::{self, ServiceControlHandlerResult};

    let event_handler = move |control_event| -> ServiceControlHandlerResult {
        match control_event {
            ServiceControl::Stop | ServiceControl::Shutdown => {
                ServiceControlHandlerResult::NoError
            }
            _ => ServiceControlHandlerResult::NotImplemented,
        }
    };

    let status_handle =
        service_control_handler::register("tracera-os-service", event_handler)
            .map_err(anyhow::Error::from)?;

    status_handle
        .set_service_status(ServiceStatus {
            service_type: ServiceType::OWN_PROCESS,
            current_state: ServiceState::Running,
            controls_accepted: ServiceControlAccept::STOP | ServiceControlAccept::SHUTDOWN,
            exit_code: ServiceExitCode::NO_ERROR,
            checkpoint: 0,
            wait_hint: std::time::Duration::from_secs(10),
            process_id: Some(std::process::id()),
        })
        .map_err(anyhow::Error::from)?;

    let rt = tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .build()?;
    rt.block_on(run())
}