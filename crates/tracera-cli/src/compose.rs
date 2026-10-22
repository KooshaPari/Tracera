//! Compose command construction and execution.
//!
//! All compose invocations go through this module so the runtime-selection
//! logic stays in one place. The argv layout is:
//!
//!   <backend-binary> [wsl-distro-and-docker] compose --env-file <env>
//!     -f <compose-file> <subcommand...>

use std::path::{Path, PathBuf};
use std::process::Stdio;

use anyhow::Context;

use crate::runtime::{run_capture, run_inherited as run_cmd_inherited, Backend};

/// Build the compose argv for a given backend + action.
///
/// Returns `(program, args)`. For non-WSL backends, `program` is the backend
/// binary (e.g. `docker`) and `args` is the rest. For WSL2, `program` is
/// `wsl` and `args` includes the distro flag + `docker compose ...`.
pub fn compose_argv(
    backend: Backend,
    project_name: &str,
    compose_file: &Path,
    env_file: &Path,
    subcommand: &[&str],
) -> (String, Vec<String>) {
    let wsl_distro = if matches!(backend, Backend::WslDocker) {
        crate::runtime::wsl_distro()
    } else {
        None
    };
    compose_argv_with_wsl_distro(
        backend,
        project_name,
        compose_file,
        env_file,
        subcommand,
        wsl_distro.as_deref(),
    )
}

fn compose_argv_with_wsl_distro(
    backend: Backend,
    project_name: &str,
    compose_file: &Path,
    env_file: &Path,
    subcommand: &[&str],
    wsl_distro: Option<&str>,
) -> (String, Vec<String>) {
    let mut args: Vec<String> = Vec::with_capacity(10 + subcommand.len());

    if matches!(backend, Backend::WslDocker) {
        if let Some(distro) = wsl_distro {
            args.push("--distribution".into());
            args.push(distro.to_string());
        }
    }

    for a in backend.compose_argv() {
        args.push((*a).into());
    }

    // Lock the project name so the bundled stack is named consistently
    // regardless of cwd. Without this, compose resolves the project from a
    // `.env` file next to the cwd, which we don't ship in the bundle.
    args.push("--project-name".into());
    args.push(project_name.to_string());

    args.push("--env-file".into());
    args.push(env_file.display().to_string());
    args.push("-f".into());
    args.push(compose_file.display().to_string());

    for s in subcommand {
        args.push((*s).into());
    }

    let program = if matches!(backend, Backend::WslDocker) {
        "wsl".to_string()
    } else {
        backend.binary().to_string()
    };

    (program, args)
}

/// Run a compose command inheriting stdio (so users see docker output).
pub async fn run_inherited(
    backend: Backend,
    project_name: &str,
    compose_file: &Path,
    env_file: &Path,
    cwd: PathBuf,
    subcommand: &[&str],
) -> anyhow::Result<i32> {
    let (program, argv) = compose_argv(backend, project_name, compose_file, env_file, subcommand);
    run_cmd_inherited(&program, argv, Some(cwd)).await
}

/// Probe compose for whether a given service is running.
pub async fn ps(
    backend: Backend,
    project_name: &str,
    compose_file: &Path,
    env_file: &Path,
    _cwd: PathBuf,
) -> anyhow::Result<String> {
    let (program, argv) = compose_argv(
        backend,
        project_name,
        compose_file,
        env_file,
        &["ps", "--format", "json"],
    );
    run_capture(&program, argv).await
}

/// Tail logs (inherits stdio).
pub async fn logs(
    backend: Backend,
    project_name: &str,
    compose_file: &Path,
    env_file: &Path,
    cwd: PathBuf,
    service: Option<&str>,
    follow: bool,
) -> anyhow::Result<i32> {
    let mut sub: Vec<&str> = vec!["logs"];
    if follow {
        sub.push("--follow");
    } else {
        sub.push("--tail=200");
    }
    if let Some(s) = service {
        sub.push(s);
    }
    run_inherited(backend, project_name, compose_file, env_file, cwd, &sub).await
}

/// Drop `.env.local` next to the compose file as a symlink to the data-dir
/// env file. docker compose v2 unconditionally stats `<compose-dir>/.env.local`
/// at startup to derive the project name; without this symlink it errors out
/// with "env file ... not found" even when --env-file points at the real file.
pub fn sync_bundle_env_symlink(compose_dir: &Path, env_file: &Path) -> anyhow::Result<()> {
    let link = compose_dir.join(".env.local");
    match std::fs::symlink_metadata(&link) {
        Ok(_) => {
            if link == env_file || std::fs::read_link(&link).ok().as_deref() == Some(env_file) {
                return Ok(());
            }
            anyhow::bail!("existing compose configuration {} conflicts with {}; preserve it and reconcile explicitly", link.display(), env_file.display());
        }
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
        Err(error) => return Err(error).with_context(|| format!("checking {}", link.display())),
    }
    #[cfg(unix)]
    std::os::unix::fs::symlink(env_file, &link)
        .with_context(|| format!("symlinking {} -> {}", link.display(), env_file.display()))?;
    #[cfg(windows)]
    {
        use std::io::Write;
        let body =
            std::fs::read(env_file).with_context(|| format!("reading {}", env_file.display()))?;
        let mut file = std::fs::OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&link)
            .with_context(|| format!("creating {}", link.display()))?;
        file.write_all(&body)
            .with_context(|| format!("writing {}", link.display()))?;
    }
    tracing::info!(link = %link.display(), target = %env_file.display(), "created bundle env symlink");
    Ok(())
}

pub use crate::env_config::ensure_env_file;

/// Poll the bundled frontend until /health and /ready both return 200 OK.
pub async fn wait_ready(url: &str, timeout_seconds: u64) -> anyhow::Result<()> {
    use std::time::{Duration, Instant};
    let deadline = Instant::now() + Duration::from_secs(timeout_seconds);
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(3))
        .build()?;
    let health_url = format!("{url}/health");
    let ready_url = format!("{url}/ready");
    while Instant::now() < deadline {
        let h = client.get(&health_url).send().await;
        let r = client.get(&ready_url).send().await;
        if let (Ok(h), Ok(r)) = (h, r) {
            if h.status().is_success() && r.status().is_success() {
                let hb = h.json::<serde_json::Value>().await.unwrap_or_default();
                let rb = r.json::<serde_json::Value>().await.unwrap_or_default();
                if hb.get("status").and_then(|v| v.as_str()) == Some("ok")
                    && rb.get("status").and_then(|v| v.as_str()) == Some("ready")
                {
                    return Ok(());
                }
            }
        }
        tokio::time::sleep(Duration::from_secs(2)).await;
    }
    anyhow::bail!("Tracera backend did not become ready at {url} within {timeout_seconds}s")
}

/// Forward a process stderr stream to tracing::info while running.
#[allow(dead_code)]
pub fn spawn_with_log(cmd: &mut tokio::process::Command) -> &mut tokio::process::Command {
    cmd.stdout(Stdio::piped()).stderr(Stdio::piped())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[cfg(unix)]
    use std::os::unix::fs::symlink;

    #[test]
    fn compose_argv_locks_project_name_and_env_file() {
        let (prog, args) = compose_argv(
            Backend::Docker,
            "tracera-bundle",
            Path::new("/tmp/docker-compose.bundle.yml"),
            Path::new("/tmp/.env.local"),
            &["up", "-d"],
        );
        assert_eq!(prog, "docker");
        let project_idx = args.iter().position(|a| a == "--project-name").unwrap();
        assert_eq!(args[project_idx + 1], "tracera-bundle");
        let env_idx = args.iter().position(|a| a == "--env-file").unwrap();
        assert_eq!(args[env_idx + 1], "/tmp/.env.local");
        assert!(args
            .windows(2)
            .any(|w| w[0] == "-f" && w[1] == "/tmp/docker-compose.bundle.yml"));
        assert_eq!(args[args.len() - 2..], ["up", "-d"]);
    }

    #[test]
    fn compose_argv_wsl_prefixes_docker_with_distribution() {
        let (prog, args) = compose_argv_with_wsl_distro(
            Backend::WslDocker,
            "tracera-bundle",
            Path::new("/mnt/c/docker-compose.bundle.yml"),
            Path::new("/mnt/c/.env.local"),
            &["ps"],
            Some("Ubuntu-22.04"),
        );
        assert_eq!(prog, "wsl");
        assert_eq!(args[0], "--distribution");
        assert_eq!(args[1], "Ubuntu-22.04");
        assert_eq!(args[2], "docker");
        assert_eq!(args[3], "compose");

        let (_prog, args_without_distro) = compose_argv_with_wsl_distro(
            Backend::WslDocker,
            "tracera-bundle",
            Path::new("/mnt/c/docker-compose.bundle.yml"),
            Path::new("/mnt/c/.env.local"),
            &["ps"],
            None,
        );
        assert_eq!(args_without_distro[0], "docker");
        assert_eq!(args_without_distro[1], "compose");
    }

    // Symlink semantics only exist on unix: the `#[cfg(windows)]` branch of
    // `sync_bundle_env_symlink` copies the env file instead of linking it.
    #[cfg(unix)]
    #[test]
    fn sync_bundle_env_symlink_creates_link_when_missing() {
        let tmp = std::env::temp_dir().join(format!("tracera-test-{}", std::process::id()));
        std::fs::create_dir_all(&tmp).unwrap();
        let target = tmp.join("envfile");
        std::fs::write(&target, "POSTGRES_PASSWORD=abc\n").unwrap();

        let compose_dir = tmp.join("bundle");
        std::fs::create_dir_all(&compose_dir).unwrap();

        sync_bundle_env_symlink(&compose_dir, &target).unwrap();
        let link = compose_dir.join(".env.local");
        assert!(link.is_symlink(), "expected symlink at {}", link.display());
        let read = std::fs::read_link(&link).unwrap();
        assert_eq!(read, target);

        // Idempotent — second call does not fail and does not change the link target.
        sync_bundle_env_symlink(&compose_dir, &target).unwrap();
        assert_eq!(std::fs::read_link(&link).unwrap(), target);

        std::fs::remove_dir_all(&tmp).unwrap();
    }

    #[test]
    fn sync_bundle_env_symlink_leaves_user_provided_file_alone() {
        let tmp = std::env::temp_dir().join(format!("tracera-test-user-{}", std::process::id()));
        std::fs::create_dir_all(&tmp).unwrap();
        let target = tmp.join("envfile");
        std::fs::write(&target, "POSTGRES_PASSWORD=abc\n").unwrap();

        let compose_dir = tmp.join("bundle");
        std::fs::create_dir_all(&compose_dir).unwrap();
        // User dropped a real file (not a symlink) — leave it alone.
        std::fs::write(compose_dir.join(".env.local"), "POSTGRES_PASSWORD=USER\n").unwrap();

        assert!(sync_bundle_env_symlink(&compose_dir, &target).is_err());
        let body = std::fs::read_to_string(compose_dir.join(".env.local")).unwrap();
        assert_eq!(
            body, "POSTGRES_PASSWORD=USER\n",
            "user file was overwritten"
        );

        std::fs::remove_dir_all(&tmp).unwrap();
    }

    #[cfg(unix)]
    #[test]
    fn sync_bundle_env_symlink_rejects_and_preserves_stale_symlink() {
        let tmp = std::env::temp_dir().join(format!("tracera-test-stale-{}", std::process::id()));
        std::fs::create_dir_all(&tmp).unwrap();

        let old = tmp.join("old-env");
        std::fs::write(&old, "OLD=1\n").unwrap();
        let new = tmp.join("new-env");
        std::fs::write(&new, "NEW=1\n").unwrap();

        let compose_dir = tmp.join("bundle");
        std::fs::create_dir_all(&compose_dir).unwrap();
        let link = compose_dir.join(".env.local");
        symlink(&old, &link).unwrap();

        assert!(sync_bundle_env_symlink(&compose_dir, &new).is_err());
        assert_eq!(std::fs::read_link(&link).unwrap(), old);

        std::fs::remove_dir_all(&tmp).unwrap();
    }
}
