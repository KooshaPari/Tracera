use tracing::info;

mod domain;
mod application;
mod infrastructure;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();
    info!("Starting hexagonal Rust application");
    Ok(())
}
