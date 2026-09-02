//! OpenTelemetry observability setup.
//!
//! Provides trace and metric export configuration.

use tracing_subscriber::EnvFilter;

/// Initialize tracing with optional OpenTelemetry export.
pub fn init_tracing() {
    let filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("tracera_server=info,tower_http=info"));
    
    tracing_subscriber::fmt()
        .with_env_filter(filter)
        .with_target(true)
        .with_thread_ids(true)
        .with_file(true)
        .with_line_number(true)
        .init();
}

/// Check if OpenTelemetry is configured via environment variables.
pub fn is_otel_configured() -> bool {
    std::env::var("OTEL_EXPORTER_OTLP_ENDPOINT").is_ok()
}
