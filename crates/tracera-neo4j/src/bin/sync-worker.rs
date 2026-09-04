use std::time::Duration;

use neo4rs::Graph;
use sqlx::sqlite::SqlitePoolOptions;
use tracera_neo4j::{mirror, Error};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt::init();
    let sqlite_url = std::env::var("TRACERA_SQLITE_URL")
        .map_err(|_| Error::Configuration("TRACERA_SQLITE_URL is required".into()))?;
    let neo4j_uri = std::env::var("NEO4J_URI")
        .unwrap_or_else(|_| "neo4j://127.0.0.1:7687".into());
    let neo4j_user = std::env::var("NEO4J_USER").unwrap_or_else(|_| "neo4j".into());
    let neo4j_password = std::env::var("NEO4J_PASSWORD")
        .map_err(|_| Error::Configuration("NEO4J_PASSWORD is required".into()))?;
    let interval = std::env::var("SYNC_INTERVAL_SECONDS")
        .ok()
        .and_then(|v| v.parse::<u64>().ok())
        .unwrap_or(30);

    let pool = SqlitePoolOptions::new()
        .max_connections(1)
        .connect(&sqlite_url)
        .await?;
    let graph = Graph::new(&neo4j_uri, &neo4j_user, &neo4j_password).await?;

    loop {
        let count = mirror::sync_sqlite_to_neo4j(&pool, &graph).await?;
        tracing::info!(synced = count, "SWEE graph synchronized to Neo4j");
        tokio::time::sleep(Duration::from_secs(interval)).await;
    }
}
