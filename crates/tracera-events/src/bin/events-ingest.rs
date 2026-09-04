//! `events-ingest` — bulk-ingest NDJSON event lines into ClickHouse.
//!
//! Reads newline-delimited [`Event`] rows (the same JSON shape used for
//! inter-service transport) and forwards them to the matching table:
//!
//! ```text
//! {"stream":"agent_run",...}
//! {"stream":"decision",...}
//! {"stream":"deploy",...}
//! {"stream":"trace",...}
//! {"stream":"llm_call",...}
//! ```
//!
//! Reads from `stdin` by default; pass `--file <path>` to read from a file
//! instead. With `--batch <N>`, rows are accumulated client-side and sent
//! in chunks of `N` (default: 500) to amortize round-trip costs.
//!
//! Connection settings are taken from the same `CLICKHOUSE_*` environment
//! variables documented in [`tracera_events::config::ClickHouseConfig`].

#![deny(unsafe_code)]
#![warn(missing_debug_implementations)]

use std::io::{self, BufRead, Write};
use std::path::PathBuf;
use std::process::ExitCode;

use anyhow::{Context, Result};
use tracing::{error, info};
use tracing_subscriber::{fmt, EnvFilter};

use tracera_events::{
    AgentRun, ClickHouseClient, Decision, Deploy, Event, LlmCall, TraceSpan,
};

/// Parsed CLI arguments.
#[derive(Debug)]
struct Args {
    /// Optional input file. `None` means stdin.
    file: Option<PathBuf>,
    /// Flush threshold per table.
    batch_size: usize,
    /// If true, parse but do not contact ClickHouse.
    dry_run: bool,
}

impl Default for Args {
    fn default() -> Self {
        Self {
            file: None,
            batch_size: 500,
            dry_run: false,
        }
    }
}

fn parse_args() -> Result<Args> {
    let mut args = Args::default();
    let mut iter = std::env::args().skip(1);
    while let Some(flag) = iter.next() {
        match flag.as_str() {
            "--file" | "-f" => {
                let value = iter
                    .next()
                    .ok_or_else(|| anyhow::anyhow!("--file requires a path"))?;
                args.file = Some(PathBuf::from(value));
            }
            "--batch" | "-b" => {
                let value = iter
                    .next()
                    .ok_or_else(|| anyhow::anyhow!("--batch requires a size"))?;
                args.batch_size = value
                    .parse()
                    .with_context(|| format!("invalid --batch value `{value}`"))?;
                if args.batch_size == 0 {
                    anyhow::anyhow!("--batch must be > 0");
                }
            }
            "--dry-run" => args.dry_run = true,
            "-h" | "--help" => {
                print_help();
                std::process::exit(0);
            }
            "-V" | "--version" => {
                println!("events-ingest {}", env!("CARGO_PKG_VERSION"));
                std::process::exit(0);
            }
            other => anyhow::anyhow!("unknown argument: {other}"),
        }
    }
    Ok(args)
}

fn print_help() {
    println!(
        "events-ingest {ver}

USAGE:
    events-ingest [--file <path>] [--batch <N>] [--dry-run]

OPTIONS:
    -f, --file <path>     Read NDJSON from <path> instead of stdin
    -b, --batch <N>       Flush every N rows (default: 500)
        --dry-run         Parse only, do not contact ClickHouse
    -h, --help            Print this help
    -V, --version         Print version

ENV:
    CLICKHOUSE_URL        ClickHouse HTTP endpoint (required unless --dry-run)
    CLICKHOUSE_DATABASE   Database name (default: tracera)
    CLICKHOUSE_USER       Username
    CLICKHOUSE_PASSWORD   Password
",
        ver = env!("CARGO_PKG_VERSION"),
    );
}

fn init_tracing() {
    let filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info"));
    let _ = fmt().with_env_filter(filter).with_target(true).try_init();
}

#[tokio::main(flavor = "current_thread")]
async fn main() -> ExitCode {
    init_tracing();
    let args = match parse_args() {
        Ok(a) => a,
        Err(e) => {
            eprintln!("events-ingest: {e:#}");
            print_help();
            return ExitCode::FAILURE;
        }
    };

    match ingest(args).await {
        Ok(stats) => {
            println!(
                "ok: {} rows ingested, {} empty lines, {} parse errors",
                stats.ingested, stats.empty, stats.errors
            );
            if stats.errors == 0 {
                ExitCode::SUCCESS
            } else {
                ExitCode::from(2)
            }
        }
        Err(e) => {
            error!("{e:#}");
            eprintln!("events-ingest: {e:#}");
            ExitCode::FAILURE
        }
    }
}

/// Ingest counters.
#[derive(Debug, Default)]
struct Stats {
    /// Successfully dispatched rows.
    ingested: usize,
    /// Empty lines skipped.
    empty: usize,
    /// Lines that failed to parse as an [`Event`].
    errors: usize,
}

/// Per-table accumulation. Each `Vec` only contains rows destined for the
/// matching ClickHouse table.
#[derive(Debug, Default)]
struct Buckets {
    agent_runs: Vec<AgentRun>,
    decisions: Vec<Decision>,
    deploys: Vec<Deploy>,
    traces: Vec<TraceSpan>,
    llm_calls: Vec<LlmCall>,
}

impl Buckets {
    /// True when any bucket has reached the configured batch size.
    fn needs_flush(&self, batch_size: usize) -> bool {
        self.agent_runs.len() >= batch_size
            || self.decisions.len() >= batch_size
            || self.deploys.len() >= batch_size
            || self.traces.len() >= batch_size
            || self.llm_calls.len() >= batch_size
    }
}

async fn ingest(args: Args) -> Result<Stats> {
    let client = if args.dry_run {
        None
    } else {
        Some(ClickHouseClient::from_env().context("building ClickHouse client from env")?)
    };

    let reader: Box<dyn BufRead> = match &args.file {
        Some(path) => {
            let f = std::fs::File::open(path)
                .with_context(|| format!("opening input file {}", path.display()))?;
            Box::new(io::BufReader::new(f))
        }
        None => Box::new(io::BufReader::new(io::stdin().lock())),
    };

    let mut stats = Stats::default();
    let mut buckets = Buckets::default();

    for (line_no, line) in reader.lines().enumerate() {
        let line = line.with_context(|| format!("reading line {}", line_no + 1))?;
        let trimmed = line.trim();
        if trimmed.is_empty() {
            stats.empty += 1;
            continue;
        }

        match serde_json::from_str::<Event>(trimmed) {
            Ok(event) => {
                route(event, &mut buckets);
                stats.ingested += 1;
            }
            Err(err) => {
                stats.errors += 1;
                tracing::warn!(
                    line = line_no + 1,
                    error = %err,
                    payload = trimmed,
                    "failed to parse event line"
                );
            }
        }

        if buckets.needs_flush(args.batch_size) {
            flush_all(&mut buckets, client.as_ref(), args.dry_run).await?;
        }
    }

    flush_all(&mut buckets, client.as_ref(), args.dry_run).await?;
    let _ = io::stdout().flush();
    Ok(stats)
}

/// Route an [`Event`] into its destination bucket.
fn route(event: Event, buckets: &mut Buckets) {
    match event {
        Event::AgentRun(row) => buckets.agent_runs.push(row),
        Event::Decision(row) => buckets.decisions.push(row),
        Event::Deploy(row) => buckets.deploys.push(row),
        Event::Trace(row) => buckets.traces.push(row),
        Event::LlmCall(row) => buckets.llm_calls.push(row),
    }
}

/// Flush every non-empty bucket to ClickHouse (or no-op on dry-run).
async fn flush_all(
    buckets: &mut Buckets,
    client: Option<&ClickHouseClient>,
    dry_run: bool,
) -> Result<()> {
    // Drain each bucket via `std::mem::take` so we can `await` the inserts
    // without holding a mutable borrow across the await point.
    let agent_runs = std::mem::take(&mut buckets.agent_runs);
    let decisions = std::mem::take(&mut buckets.decisions);
    let deploys = std::mem::take(&mut buckets.deploys);
    let traces = std::mem::take(&mut buckets.traces);
    let llm_calls = std::mem::take(&mut buckets.llm_calls);

    if let Some(client) = client {
        if !agent_runs.is_empty() {
            info!(rows = agent_runs.len(), "inserting agent_runs batch");
            client
                .insert_agent_run(&agent_runs)
                .await
                .context("inserting agent_runs")?;
        }
        if !decisions.is_empty() {
            info!(rows = decisions.len(), "inserting decisions batch");
            client
                .insert_decision(&decisions)
                .await
                .context("inserting decisions")?;
        }
        if !deploys.is_empty() {
            info!(rows = deploys.len(), "inserting deploys batch");
            client
                .insert_deploy(&deploys)
                .await
                .context("inserting deploys")?;
        }
        if !traces.is_empty() {
            info!(rows = traces.len(), "inserting traces batch");
            client
                .insert_trace(&traces)
                .await
                .context("inserting traces")?;
        }
        if !llm_calls.is_empty() {
            info!(rows = llm_calls.len(), "inserting llm_calls batch");
            client
                .insert_llm_call(&llm_calls)
                .await
                .context("inserting llm_calls")?;
        }
    } else if dry_run {
        let n = agent_runs.len() + decisions.len() + deploys.len() + traces.len() + llm_calls.len();
        if n > 0 {
            info!(rows = n, "dry-run: skipping insert");
        }
    }
    Ok(())
}