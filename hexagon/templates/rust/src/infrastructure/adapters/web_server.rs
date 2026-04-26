use axum::{Router, routing::get};
use std::net::SocketAddr;

pub struct WebServer {
    router: Router,
}

impl WebServer {
    pub fn new() -> Self {
        let router = Router::new()
            .route("/health", get(health_check));
        
        Self { router }
    }
    
    pub async fn run(self, addr: SocketAddr) -> anyhow::Result<()> {
        let listener = tokio::net::TcpListener::bind(addr).await?;
        axum::serve(listener, self.router).await?;
        Ok(())
    }
}

async fn health_check() -> &'static str {
    "OK"
}
