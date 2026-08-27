//! Container-runtime detection and command construction.
//!
//! Order of preference:
//!   1. `apple-container` (macOS 26+ native; first-class when available)
//!   2. `docker` (Docker Desktop / colima / lima / docker-engine)
//!   3. `podman` (rootless OCI)
//!   4. WSL2-hosted `docker` (Windows host fallback)
//!
//! All backends are driven through the same docker-compatible compose
//! surface (`docker compose` / `podman compose`). Apple Container ships
//! `container` (its native CLI) which on macOS 26+ accepts the same
//! compose spec via `container compose` (when installed). When unavailable,
//! we fall back to the prior runtime.

use std::fmt;
use std::path::PathBuf;

use which::which;

#[cfg(target_os = "macos")]
const APPLE_CONTAINER_BINARY: &str = "/usr/local/bin/container";
#[cfg(not(target_os = "macos"))]
const APPLE_CONTAINER_BINARY: &str = "container";

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Backend {
    Docker,
    Podman,
    AppleContainer,
    WslDocker,
}

impl Backend {
    pub const ALL: &'static [Backend] = &[
        Backend::AppleContainer,
        Backend::Docker,
        Backend::Podman,
        Backend::WslDocker,
    ];

    pub fn label(self) -> &'static str {
        match self {
            Backend::Docker => "docker",
            Backend::Podman => "podman",
            Backend::AppleContainer => "apple-container",
            Backend::WslDocker => "wsl+docker",
        }
    }

    pub fn binary(self) -> &'static str {
        match self {
            Backend::Docker => "docker",
            Backend::Podman => "podman",
            Backend::AppleContainer => APPLE_CONTAINER_BINARY,
            Backend::WslDocker => "wsl",
        }
    }

    /// Compose invocation as argv (without file/env flags).
    pub fn compose_argv(self) -> &'static [&'static str] {
        match self {
            // `docker compose`, `podman compose`, `container compose` are all v2 subcommands.
            Backend::Docker | Backend::Podman | Backend::AppleContainer => &["compose"],
            // WSL2 case: `wsl docker compose ...` (handled separately by caller).
            Backend::WslDocker => &["docker", "compose"],
        }
    }

    /// Returns true when the backend's primary binary is on PATH (or, for
    /// WSL2, when `wsl` is present and reports a docker install inside).
    pub fn probe(self) -> bool {
        match self {
            Backend::WslDocker => probe_wsl_docker(),
            Backend::AppleContainer => {
                which(self.binary()).is_ok() || std::path::Path::new(self.binary()).is_file()
            }
            other => which(other.binary()).is_ok(),
        }
    }

    /// Returns true when this backend can actually drive a Compose file.
    ///
    /// `probe()` only checks for the binary on PATH; `compose_works()` runs
    /// `<backend> compose version` to confirm the compose subcommand is
    /// installed and functional. Apple Container on macOS 26+ ships the
    /// `container` binary but the `compose` subcommand lives in a separate
    /// plugin that is not always installed — this lets the auto-detect fall
    /// back to Docker in that case.
    pub fn compose_works(self) -> bool {
        if !self.probe() {
            return false;
        }
        if matches!(self, Backend::WslDocker) {
            // Already validated inside probe_wsl_docker.
            return true;
        }
        let program = self.binary();
        let mut argv: Vec<&str> = vec![program];
        if !matches!(self, Backend::WslDocker) {
            argv.extend(self.compose_argv());
        }
        argv.push("version");
        let result = std::process::Command::new(argv[0])
            .args(&argv[1..])
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .status();
        matches!(result, Ok(s) if s.success())
    }
}

impl fmt::Display for Backend {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(self.label())
    }
}

/// Detect the best available backend, honouring `$TRACERA_BACKEND` override.
///
/// Auto-detection tries each backend in preference order and verifies that
/// the backend can actually drive a Compose file (`compose_works()`). This
/// means Apple Container on macOS 26+ is preferred when its `compose`
/// subcommand is installed, but the CLI transparently falls back to Docker
/// (and then Podman, then WSL2+docker) when it's not.
pub fn detect(preferred: Option<Backend>) -> anyhow::Result<Backend> {
    if let Some(b) = preferred {
        if b.compose_works() {
            return Ok(b);
        }
        if !b.probe() {
            anyhow::bail!(
                "TRACERA_BACKEND={} requested but {} is not available",
                b.label(),
                b.binary()
            );
        }
        anyhow::bail!(
            "TRACERA_BACKEND={} is installed but its compose command is unavailable; install the backend's Compose integration or choose another runtime",
            b.label()
        );
    }

    for backend in Backend::ALL {
        if backend.compose_works() {
            tracing::info!(backend = backend.label(), "selected container runtime");
            return Ok(*backend);
        }
    }

    anyhow::bail!(
        "no container runtime found. Install one of: docker, podman, apple-container (macOS 26+), or WSL2 with docker."
    )
}

fn probe_wsl_docker() -> bool {
    if which("wsl").is_err() {
        return false;
    }
    // Cheap probe: ask wsl whether `docker` exists inside the default distro.
    // We swallow non-zero exit codes — failure just means "no docker in WSL".
    let output = std::process::Command::new("wsl")
        .args(["--status"])
        .output();
    match output {
        Ok(o) if o.status.success() => {
            // Verify docker is actually present inside.
            let probe = std::process::Command::new("wsl")
                .args(["docker", "version", "--format", "{{.Server.Version}}"])
                .output();
            matches!(probe, Ok(p) if p.status.success())
        }
        _ => false,
    }
}

/// Resolve a free TCP port by binding to port 0 and reading what the OS assigned.
pub fn pick_free_port() -> anyhow::Result<u16> {
    use std::net::TcpListener;
    let listener = TcpListener::bind("127.0.0.1:0")?;
    let port = listener.local_addr()?.port();
    Ok(port)
}

/// Returns the path to the `wsl.exe` distribution root (used only when
/// constructing `wsl --distribution <name> -- ...` invocations).
pub fn wsl_distro() -> Option<String> {
    let out = std::process::Command::new("wsl")
        .args(["-l", "-q"])
        .output()
        .ok()?;
    if !out.status.success() {
        return None;
    }
    let stdout = String::from_utf8_lossy(&out.stdout);
    stdout
        .lines()
        .map(str::trim)
        .find(|s| !s.is_empty() && *s != "(Default)")
        .map(str::to_owned)
}

/// Run a command, inheriting stdio (for human-facing output).
///
/// `program` is the binary path or name (resolved via the OS PATH).
pub async fn run_inherited<I, S>(
    program: &str,
    args: I,
    cwd: Option<PathBuf>,
) -> anyhow::Result<i32>
where
    I: IntoIterator<Item = S>,
    S: AsRef<std::ffi::OsStr>,
{
    use tokio::process::Command;

    let mut command = Command::new(program);
    for arg in args {
        command.arg(arg);
    }
    if let Some(c) = cwd {
        command.current_dir(c);
    }
    command.stdin(std::process::Stdio::inherit());
    command.stdout(std::process::Stdio::inherit());
    command.stderr(std::process::Stdio::inherit());
    let status = command.status().await?;
    Ok(status.code().unwrap_or(1))
}

/// Capture stdout as a string (for probe commands).
pub async fn run_capture<I, S>(program: &str, args: I) -> anyhow::Result<String>
where
    I: IntoIterator<Item = S>,
    S: AsRef<std::ffi::OsStr>,
{
    use tokio::process::Command;

    let mut command = Command::new(program);
    for arg in args {
        command.arg(arg);
    }
    command.stdin(std::process::Stdio::null());
    command.stdout(std::process::Stdio::piped());
    command.stderr(std::process::Stdio::piped());
    let output = command.output().await?;
    if !output.status.success() {
        anyhow::bail!(
            "command failed: stderr={}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
    Ok(String::from_utf8_lossy(&output.stdout).into_owned())
}

#[cfg(test)]
mod tests {
    use super::{Backend, APPLE_CONTAINER_BINARY};

    #[test]
    fn apple_container_uses_native_binary_path() {
        assert_eq!(Backend::AppleContainer.binary(), APPLE_CONTAINER_BINARY);
        assert_eq!(Backend::AppleContainer.compose_argv(), &["compose"]);
    }
}
