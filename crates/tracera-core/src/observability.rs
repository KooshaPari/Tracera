//! Tracing helpers for per-bus observability.

use std::env;
use tracing::{info_span, Span};
use tracing_subscriber::{fmt, layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

/// Initialize process-wide tracing from `RUST_LOG`.
///
/// Repeated calls are harmless; initialization is skipped if a subscriber is
/// already installed by a binary or test harness.
pub fn init_tracing() {
    let filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info"));
    let subscriber = tracing_subscriber::registry()
        .with(filter)
        .with(fmt::layer());

    let _ = subscriber.try_init();
}

/// Return the configured OTLP collector endpoint, if one is present.
pub fn otlp_endpoint() -> Option<String> {
    [
        "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "OTEL_COLLECTOR_ENDPOINT",
        "OTEL_COLLECTOR_HTTP_ENDPOINT",
        "TRACERA_OTLP_ENDPOINT",
    ]
    .into_iter()
    .find_map(|key| env::var(key).ok().filter(|value| !value.trim().is_empty()))
}

/// Create a tracing span for work on one bus envelope.
pub fn make_span(envelope_id: &str) -> Span {
    info_span!("tracera.bus", envelope_id = %envelope_id)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn make_span_has_bus_metadata() {
        let span = make_span("env-123");

        let metadata = span.metadata().expect("span metadata");
        assert_eq!(metadata.name(), "tracera.bus");
        assert_eq!(metadata.target(), "tracera_core::observability");
    }

    #[test]
    fn make_span_accepts_empty_envelope_id() {
        let span = make_span("");

        let metadata = span.metadata().expect("span metadata");
        assert_eq!(metadata.name(), "tracera.bus");
    }
}
