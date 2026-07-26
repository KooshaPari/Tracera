//! Tracera CLI entrypoint.
//!
//! Manages the bundled Tracera Compose stack across multiple container
//! runtimes: Apple Container (macOS 26+), Docker, Podman, and WSL2 Docker.
//! Designed to run both standalone (from a developer worktree) and bundled
//! inside `Tracera.app/Contents/Resources/tracera-bundle/` (when invoked by
//! the desktop app).

#![deny(unsafe_code)]
#![warn(missing_debug_implementations)]

use std::process::ExitCode;

use clap::Parser;

mod bundle;
mod commands;
mod compose;
mod runtime;

use commands::Cli;

#[tokio::main(flavor = "current_thread")]
async fn main() -> ExitCode {
    init_tracing();
    let cli = Cli::parse();
    match commands::run(cli).await {
        Ok(()) => ExitCode::SUCCESS,
        Err(err) => {
            tracing::error!("{err:#}");
            // Also print a single-line summary to stderr for non-log users.
            eprintln!("tracera: {err}");
            ExitCode::FAILURE
        }
    }
}

fn init_tracing() {
    use tracing_subscriber::{fmt, EnvFilter};
    let filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info"));
    let _ = fmt().with_env_filter(filter).with_target(false).try_init();
}
