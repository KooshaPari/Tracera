//! Bundle path resolution.
//!
//! The CLI runs in two modes:
//!
//! 1. **Standalone** — invoked from a developer worktree at
//!    `/path/to/Tracera/`. Repo root is the parent of the binary, and the
//!    compose file is `docker-compose.local.yml` at the repo root.
//!
//! 2. **Bundled** — invoked from inside `Tracera.app/Contents/Resources/`
//!    by the desktop app. The compose file and bundle metadata are siblings
//!    of the CLI at `Contents/Resources/tracera-bundle/`. The repo root is
//!    the user data directory (`~/Library/Application Support/Tracera/`) —
//!    that is where `.env.local` and the postgres volume live.
//!
//! The user data directory is created on first run.

use std::path::{Path, PathBuf};

use anyhow::Context;

#[derive(Debug, Clone)]
pub struct BundleLayout {
    /// Root of the Tracera installation (the worktree, or `~/.tracera` for
    /// the bundled app).
    pub root: PathBuf,
    /// Directory holding docker-compose.bundle.yml and assets.
    pub compose_dir: PathBuf,
    /// Path to the compose file (image-based, no build directives).
    pub compose_file: PathBuf,
    /// Path to the generated `.env.local` file.
    pub env_file: PathBuf,
    /// Local URL the frontend binds to.
    pub local_url: String,
    /// Local port the frontend binds to.
    pub local_port: u16,
    /// Whether we're running from a `.app` bundle (vs a dev worktree).
    pub bundled: bool,
    /// Compose project name (stable across cwd).
    pub project_name: String,
}

impl BundleLayout {
    /// Resolve the bundle layout given the path to the CLI binary.
    ///
    /// `argv0` is the resolved path of the current executable. When unset,
    /// we fall back to `std::env::current_exe()`.
    pub fn resolve(argv0: Option<&Path>) -> anyhow::Result<Self> {
        let exe = argv0
            .map(Path::to_path_buf)
            .or_else(|| std::env::current_exe().ok())
            .context("could not resolve current_exe")?;

        // Bundle case: <App>/Contents/Resources/tracera-bundle/bin/tracera
        // We test the canonical layout by walking up until we find a `tracera-bundle` dir.
        let mut cursor = exe.as_path();
        loop {
            let candidate = cursor.join("docker-compose.bundle.yml");
            if candidate.exists() {
                return Self::from_bundle_dir(cursor.to_path_buf());
            }
            match cursor.parent() {
                Some(p) => cursor = p,
                None => break,
            }
        }

        // Standalone case: <repo>/target/release/tracera or similar.
        Self::from_repo_root(exe)
    }

    fn from_bundle_dir(bundle_dir: PathBuf) -> anyhow::Result<Self> {
        let compose_file = bundle_dir.join("docker-compose.bundle.yml");
        anyhow::ensure!(
            compose_file.exists(),
            "bundle compose file missing at {}",
            compose_file.display()
        );

        let home = std::env::var_os("HOME")
            .map(PathBuf::from)
            .context("HOME not set")?;
        let root = home.join("Library").join("Application Support").join("Tracera");
        std::fs::create_dir_all(&root)
            .with_context(|| format!("creating {}", root.display()))?;

        let env_file = root.join(".env.local");
        let local_port: u16 = std::env::var("TRACERA_LOCAL_PORT")
            .ok()
            .and_then(|s| s.parse().ok())
            .unwrap_or(18081);

        Ok(Self {
            root,
            compose_dir: bundle_dir,
            compose_file,
            env_file,
            local_url: format!("http://127.0.0.1:{local_port}"),
            local_port,
            bundled: true,
            project_name: "tracera-bundle".into(),
        })
    }

    fn from_repo_root(exe: PathBuf) -> anyhow::Result<Self> {
        // Walk up from the binary looking for a `docker-compose.local.yml`.
        let mut cursor = exe.as_path();
        loop {
            let candidate = cursor.join("docker-compose.local.yml");
            if candidate.exists() {
                let env_file = cursor.join(".env.local");
                let local_port: u16 = std::env::var("TRACERA_LOCAL_PORT")
                    .ok()
                    .and_then(|s| s.parse().ok())
                    .unwrap_or(18081);
                return Ok(Self {
                    root: cursor.to_path_buf(),
                    compose_dir: cursor.to_path_buf(),
                    compose_file: candidate,
                    env_file,
                    local_url: format!("http://127.0.0.1:{local_port}"),
                    local_port,
                    bundled: false,
                    project_name: "tracera-local".into(),
                });
            }
            match cursor.parent() {
                Some(p) => cursor = p,
                None => break,
            }
        }
        anyhow::bail!(
            "could not locate a Tracera bundle (no docker-compose.bundle.yml near {}) \
             or a Tracera worktree (no docker-compose.local.yml in any parent dir).",
            exe.display()
        );
    }
}
