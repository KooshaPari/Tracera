//! Subcommand implementations and CLI surface.

use std::path::{Path, PathBuf};

use anyhow::Context;
use clap::{Args, Parser, Subcommand};

use crate::bundle::BundleLayout;
use crate::compose::{self, ensure_env_file, ps, sync_bundle_env_symlink, wait_ready};
use crate::runtime::{self, Backend};

#[derive(Debug, Parser)]
#[command(
    name = "tracera",
    version,
    about = "Tracera CLI — manage the bundled/local Tracera Compose stack",
    long_about = None,
)]
pub struct Cli {
    /// Container runtime to use. Defaults to auto-detected best available.
    ///
    /// Choices: `docker`, `podman`, `apple-container`, `wsl+docker`.
    #[arg(long, env = "TRACERA_BACKEND")]
    backend: Option<BackendArg>,

    /// Override the path to the Tracera bundle (or worktree root).
    /// Default: derived from the location of this binary.
    #[arg(long, env = "TRACERA_ROOT")]
    root: Option<PathBuf>,

    /// Increase verbosity (`-v` info, `-vv` debug, `-vvv` trace).
    #[arg(short, long, action = clap::ArgAction::Count)]
    verbose: u8,

    #[command(subcommand)]
    command: Command,
}

#[derive(Debug, Clone, Subcommand)]
pub enum Command {
    /// Start the Tracera Compose stack and wait until /ready.
    Up(UpArgs),
    /// Stop the Tracera Compose stack (containers stay on disk).
    Down(DownArgs),
    /// Show container status (one row per service).
    Status,
    /// Tail logs from one or all services.
    Logs(LogsArgs),
    /// Print the local frontend URL and exit (used by the desktop app).
    Url,
    /// Print the resolved backend label and exit.
    Backend,
    /// Open the local frontend in the default browser.
    Open,
    /// Health probe — exits 0 if /health and /ready both return ok.
    Doctor(DoctorArgs),
    /// Generate or refresh the `.env.local` file (POSTGRES_PASSWORD).
    Init,
}

#[derive(Debug, Clone, Args)]
pub struct UpArgs {
    /// Skip the readiness wait (return immediately after `compose up -d`).
    #[arg(long)]
    no_wait: bool,
    /// Rebuild images before starting (compose `up --build`).
    #[arg(long)]
    build: bool,
    /// Readiness timeout in seconds.
    #[arg(long, default_value_t = 180)]
    timeout_seconds: u64,
}

#[derive(Debug, Clone, Args)]
pub struct DownArgs {
    /// Also remove named volumes (postgres data).
    #[arg(long)]
    volumes: bool,
}

#[derive(Debug, Clone, Args)]
pub struct LogsArgs {
    /// Only follow a specific service (e.g. `tracera-server`).
    service: Option<String>,
    /// Follow log output (default: true).
    #[arg(long, default_value_t = true)]
    follow: bool,
}

#[derive(Debug, Clone, Default, Args)]
pub struct DoctorArgs {
    /// Print JSON instead of human-readable text.
    #[arg(long)]
    json: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, clap::ValueEnum)]
#[clap(rename_all = "kebab-case")]
pub enum BackendArg {
    Docker,
    Podman,
    #[clap(name = "apple-container")]
    AppleContainer,
    #[clap(name = "wsl+docker")]
    WslDocker,
}

impl From<BackendArg> for Backend {
    fn from(value: BackendArg) -> Self {
        match value {
            BackendArg::Docker => Backend::Docker,
            BackendArg::Podman => Backend::Podman,
            BackendArg::AppleContainer => Backend::AppleContainer,
            BackendArg::WslDocker => Backend::WslDocker,
        }
    }
}

pub async fn run(cli: Cli) -> anyhow::Result<()> {
    bump_log_level(&cli);

    let backend = runtime::detect(cli.backend.map(Into::into))?;
    let layout = resolve_layout(&cli)?;
    let cwd = layout.compose_dir.as_path();

    match cli.command {
        Command::Up(args) => cmd_up(backend, &layout, cwd, args).await,
        Command::Down(args) => cmd_down(backend, &layout, cwd, args).await,
        Command::Status => cmd_status(backend, &layout, cwd).await,
        Command::Logs(args) => cmd_logs(backend, &layout, cwd, args).await,
        Command::Url => {
            println!("{}", layout.local_url);
            Ok(())
        }
        Command::Backend => {
            println!("{backend}");
            Ok(())
        }
        Command::Open => cmd_open(&layout),
        Command::Doctor(args) => cmd_doctor(backend, &layout, cwd, args).await,
        Command::Init => cmd_init(&layout),
    }
}

fn resolve_layout(cli: &Cli) -> anyhow::Result<BundleLayout> {
    if let Some(root) = &cli.root {
        // User override: behave as if the bundle lives at <root>/tracera-bundle
        // if <root>/tracera-bundle/docker-compose.bundle.yml exists, otherwise
        // treat <root> as the compose directory.
        let candidate = root
            .join("tracera-bundle")
            .join("docker-compose.bundle.yml");
        if candidate.exists() {
            return BundleLayout::resolve(Some(
                &root.join("tracera-bundle").join("bin").join("tracera"),
            ));
        }
        let standalone = root.join("docker-compose.local.yml");
        if standalone.exists() {
            // Reuse the standalone path by synthesizing a fake argv0.
            let fake = root.join("target").join("release").join("tracera");
            return BundleLayout::resolve(Some(&fake));
        }
        anyhow::bail!(
            "--root {} contains neither tracera-bundle/ nor docker-compose.local.yml",
            root.display()
        );
    }
    BundleLayout::resolve(None)
}

fn bump_log_level(cli: &Cli) {
    let level = match cli.verbose {
        0 => "info",
        1 => "info,tracera_cli=debug",
        _ => "debug",
    };
    // Override whatever the parent process set so flag wins.
    std::env::set_var("RUST_LOG", level);
}

async fn cmd_up(
    backend: Backend,
    layout: &BundleLayout,
    cwd: &Path,
    args: UpArgs,
) -> anyhow::Result<()> {
    ensure_env_file(&layout.env_file, layout.local_port)?;
    sync_bundle_env_symlink(&layout.compose_dir, &layout.env_file)?;
    let mut sub = vec!["up", "-d"];
    if args.build {
        sub.push("--build");
    }
    let code = compose::run_inherited(
        backend,
        &layout.project_name,
        &layout.compose_file,
        &layout.env_file,
        cwd.to_path_buf(),
        &sub,
    )
    .await?;
    if code != 0 {
        anyhow::bail!("compose up exited with code {code}");
    }
    if args.no_wait {
        println!("{}", layout.local_url);
        return Ok(());
    }
    wait_ready(&layout.local_url, args.timeout_seconds)
        .await
        .with_context(|| format!("waiting for {}", layout.local_url))?;
    println!("Tracera ready at {}", layout.local_url);
    Ok(())
}

async fn cmd_down(
    backend: Backend,
    layout: &BundleLayout,
    cwd: &Path,
    args: DownArgs,
) -> anyhow::Result<()> {
    ensure_env_file(&layout.env_file, layout.local_port)?;
    sync_bundle_env_symlink(&layout.compose_dir, &layout.env_file)?;
    let mut sub = vec!["down"];
    if args.volumes {
        sub.push("--volumes");
    }
    let code = compose::run_inherited(
        backend,
        &layout.project_name,
        &layout.compose_file,
        &layout.env_file,
        cwd.to_path_buf(),
        &sub,
    )
    .await?;
    if code != 0 {
        anyhow::bail!("compose down exited with code {code}");
    }
    Ok(())
}

async fn cmd_status(backend: Backend, layout: &BundleLayout, cwd: &Path) -> anyhow::Result<()> {
    ensure_env_file(&layout.env_file, layout.local_port)?;
    sync_bundle_env_symlink(&layout.compose_dir, &layout.env_file)?;
    let code = compose::run_inherited(
        backend,
        &layout.project_name,
        &layout.compose_file,
        &layout.env_file,
        cwd.to_path_buf(),
        &["ps"],
    )
    .await?;
    if code != 0 {
        anyhow::bail!("compose ps exited with code {code}");
    }
    Ok(())
}

async fn cmd_logs(
    backend: Backend,
    layout: &BundleLayout,
    cwd: &Path,
    args: LogsArgs,
) -> anyhow::Result<()> {
    ensure_env_file(&layout.env_file, layout.local_port)?;
    sync_bundle_env_symlink(&layout.compose_dir, &layout.env_file)?;
    let code = compose::logs(
        backend,
        &layout.project_name,
        &layout.compose_file,
        &layout.env_file,
        cwd.to_path_buf(),
        args.service.as_deref(),
        args.follow,
    )
    .await?;
    if code != 0 {
        anyhow::bail!("compose logs exited with code {code}");
    }
    Ok(())
}

fn cmd_open(layout: &BundleLayout) -> anyhow::Result<()> {
    #[cfg(target_os = "macos")]
    {
        let status = std::process::Command::new("open")
            .arg(&layout.local_url)
            .status()?;
        if !status.success() {
            anyhow::bail!("open {} failed", layout.local_url);
        }
        Ok(())
    }
    #[cfg(target_os = "windows")]
    {
        let status = std::process::Command::new("cmd")
            .args(["/c", "start", "", &layout.local_url])
            .status()?;
        if !status.success() {
            anyhow::bail!("start {} failed", layout.local_url);
        }
        Ok(())
    }
    #[cfg(all(unix, not(target_os = "macos")))]
    {
        let status = std::process::Command::new("xdg-open")
            .arg(&layout.local_url)
            .status()?;
        if !status.success() {
            anyhow::bail!("xdg-open {} failed", layout.local_url);
        }
        Ok(())
    }
}

async fn cmd_doctor(
    backend: Backend,
    layout: &BundleLayout,
    cwd: &Path,
    args: DoctorArgs,
) -> anyhow::Result<()> {
    ensure_env_file(&layout.env_file, layout.local_port)?;
    sync_bundle_env_symlink(&layout.compose_dir, &layout.env_file)?;
    let mut report = serde_json::Map::new();
    report.insert(
        "backend".into(),
        serde_json::Value::String(backend.to_string()),
    );
    report.insert(
        "compose_file".into(),
        serde_json::Value::String(layout.compose_file.display().to_string()),
    );
    report.insert(
        "env_file".into(),
        serde_json::Value::String(layout.env_file.display().to_string()),
    );
    report.insert(
        "local_url".into(),
        serde_json::Value::String(layout.local_url.clone()),
    );
    report.insert("bundled".into(), serde_json::Value::Bool(layout.bundled));

    let running_json = ps(
        backend,
        &layout.project_name,
        &layout.compose_file,
        &layout.env_file,
        cwd.to_path_buf(),
    )
    .await
    .unwrap_or_else(|_| "[]".to_string());
    let running: serde_json::Value =
        serde_json::from_str(&running_json).unwrap_or_else(|_| serde_json::Value::Array(vec![]));
    report.insert("running".into(), running);

    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(3))
        .build()?;
    let mut healthy = false;
    let mut detail = serde_json::Map::new();
    for path in ["/health", "/ready"] {
        let url = format!("{}{}", layout.local_url, path);
        match client.get(&url).send().await {
            Ok(r) => {
                let status = r.status();
                let body = r.text().await.unwrap_or_default();
                detail.insert(
                    path.trim_start_matches('/').into(),
                    serde_json::json!({ "status": status.as_u16(), "body": body }),
                );
                if status.is_success() {
                    healthy = true;
                }
            }
            Err(e) => {
                detail.insert(
                    path.trim_start_matches('/').into(),
                    serde_json::json!({ "error": e.to_string() }),
                );
            }
        }
    }
    report.insert("endpoints".into(), serde_json::Value::Object(detail));
    report.insert("healthy".into(), serde_json::Value::Bool(healthy));

    if args.json {
        println!("{}", serde_json::Value::Object(report));
    } else {
        println!("backend:   {backend}");
        println!("bundled:   {}", layout.bundled);
        println!("compose:   {}", layout.compose_file.display());
        println!("env:       {}", layout.env_file.display());
        println!("url:       {}", layout.local_url);
        println!("healthy:   {healthy}");
    }

    if healthy {
        Ok(())
    } else {
        anyhow::bail!("Tracera backend not healthy at {}", layout.local_url)
    }
}

fn cmd_init(layout: &BundleLayout) -> anyhow::Result<()> {
    ensure_env_file(&layout.env_file, layout.local_port)?;
    sync_bundle_env_symlink(&layout.compose_dir, &layout.env_file)?;
    println!("wrote {}", layout.env_file.display());
    Ok(())
}
