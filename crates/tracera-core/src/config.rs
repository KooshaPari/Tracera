//! Environment-driven configuration loader.
//!
//! Phase 5 of the 2026-06-09 Tracera decouple plan.
//! Ported from `Tracera/backend/internal/config/config.go` (245 LOC).
//!
//! Provides:
//! - `Config` (top-level) with: HTTP, Neo4j, S3, ServiceToken, Observability, Sentry, Embeddings
//! - `EmbeddingsConfig`: provider, voyage/openrouter, rerank, perf, indexer
//! - `ObservabilityConfig`: OTLP endpoints, tracing toggle, env, service name
//! - `SentryConfig`: DSN, env, release, sample rate, debug
//! - `load_from_env()`: env-driven loader with typed defaults + required-key panic
//! - Helpers: `get_env`, `get_env_int`, `get_env_bool`, `get_env_float`, `get_required_env`
//!
//! All values are plain Strings, ints, bools, f64 — no external deps beyond `std::env`.

use serde::{Deserialize, Serialize};
use std::env;

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct HTTPConfig {
    pub port: u16,
    pub host: String,
    pub read_timeout_seconds: u32,
    pub write_timeout_seconds: u32,
    pub shutdown_timeout_seconds: u32,
    pub cors_allowed_origins: Vec<String>,
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct Neo4jConfig {
    pub uri: String,
    pub user: String,
    pub password: String,
    pub database: String,
    pub max_connection_pool_size: u32,
    pub connection_timeout_seconds: u32,
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct S3Config {
    pub bucket: String,
    pub region: String,
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct ObservabilityConfig {
    pub collector_endpoint: String,
    pub collector_http_endpoint: String,
    pub tracing_enabled: bool,
    pub tracing_environment: String,
    pub tracing_service_name: String,
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct SentryConfig {
    pub dsn: String,
    pub environment: String,
    pub release: String,
    pub traces_sample_rate: f64,
    pub debug: bool,
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct EmbeddingsConfig {
    pub provider: String,
    pub voyage_api_key: String,
    pub voyage_model: String,
    pub voyage_dimensions: u32,
    pub openrouter_api_key: String,
    pub openrouter_model: String,
    pub rerank_enabled: bool,
    pub rerank_model: String,
    pub rate_limit_per_minute: u32,
    pub timeout_seconds: u32,
    pub max_retries: u32,
    pub max_batch_size: u32,
    pub indexer_enabled: bool,
    pub indexer_workers: u32,
    pub indexer_batch_size: u32,
    pub indexer_poll_interval: u32,
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct Config {
    pub http: HTTPConfig,
    pub neo4j: Neo4jConfig,
    pub s3: S3Config,
    pub python_backend_url: String,
    pub python_backend_grpc_addr: String,
    pub service_token: String,
    pub observability: ObservabilityConfig,
    pub sentry: SentryConfig,
    pub embeddings: EmbeddingsConfig,
    pub env: String,
}

// Defaults (from Go config.go)
fn default_http_port() -> u16 {
    8080
}
fn default_http_host() -> String {
    "127.0.0.1".to_string()
}
fn default_http_read_timeout() -> u32 {
    30
}
fn default_http_write_timeout() -> u32 {
    30
}
fn default_http_shutdown_timeout() -> u32 {
    15
}
fn default_neo4j_max_pool() -> u32 {
    50
}
fn default_neo4j_timeout() -> u32 {
    30
}
fn default_s3_region() -> String {
    "us-east-1".to_string()
}
fn default_collector_endpoint() -> String {
    "127.0.0.1:4317".to_string()
}
fn default_collector_http_endpoint() -> String {
    "http://127.0.0.1:4318".to_string()
}
fn default_sentry_traces_sample_rate() -> f64 {
    0.1
}
fn default_voyage_dimensions() -> u32 {
    1024
}
fn default_embedding_rate_limit() -> u32 {
    60
}
fn default_embedding_timeout() -> u32 {
    30
}
fn default_embedding_max_retries() -> u32 {
    3
}
fn default_embedding_batch_size() -> u32 {
    100
}
fn default_indexer_workers() -> u32 {
    4
}
fn default_indexer_batch_size() -> u32 {
    32
}
fn default_indexer_poll_interval() -> u32 {
    10
}
fn default_env() -> String {
    "development".to_string()
}

/// Errors from config loading.
#[derive(Debug, thiserror::Error)]
pub enum ConfigError {
    #[error("required environment variable {key} is not set: {description}")]
    RequiredMissing { key: String, description: String },
    #[error("invalid int in {key}: {value} ({source})")]
    InvalidInt {
        key: String,
        value: String,
        #[source]
        source: std::num::ParseIntError,
    },
    #[error("invalid bool in {key}: {value} ({source})")]
    InvalidBool {
        key: String,
        value: String,
        #[source]
        source: std::str::ParseBoolError,
    },
    #[error("invalid float in {key}: {value} ({source})")]
    InvalidFloat {
        key: String,
        value: String,
        #[source]
        source: std::num::ParseFloatError,
    },
}

/// Load the full config from the process environment.
pub fn load_from_env() -> Result<Config, ConfigError> {
    let env_value = get_env("ENV", &default_env());

    let cfg = Config {
        env: env_value.clone(),
        http: HTTPConfig {
            port: get_env_u16("HTTP_PORT", default_http_port())?,
            host: get_env("HTTP_HOST", &default_http_host()),
            read_timeout_seconds: get_env_u32("HTTP_READ_TIMEOUT_SECONDS", default_http_read_timeout())?,
            write_timeout_seconds: get_env_u32("HTTP_WRITE_TIMEOUT_SECONDS", default_http_write_timeout())?,
            shutdown_timeout_seconds: get_env_u32("HTTP_SHUTDOWN_TIMEOUT_SECONDS", default_http_shutdown_timeout())?,
            cors_allowed_origins: get_env_list("CORS_ALLOWED_ORIGINS"),
        },
        neo4j: Neo4jConfig {
            uri: get_env("NEO4J_URI", ""),
            user: get_env("NEO4J_USER", ""),
            password: get_env("NEO4J_PASSWORD", ""),
            database: get_env("NEO4J_DATABASE", "neo4j"),
            max_connection_pool_size: get_env_u32("NEO4J_MAX_POOL_SIZE", default_neo4j_max_pool())?,
            connection_timeout_seconds: get_env_u32("NEO4J_CONNECTION_TIMEOUT_SECONDS", default_neo4j_timeout())?,
        },
        s3: S3Config {
            bucket: get_env("S3_BUCKET", ""),
            region: get_env("S3_REGION", &default_s3_region()),
        },
        python_backend_url: get_env("PYTHON_BACKEND_URL", "http://127.0.0.1:8000"),
        python_backend_grpc_addr: get_env("PYTHON_BACKEND_GRPC_ADDR", "127.0.0.1:9092"),
        service_token: get_env("SERVICE_TOKEN", ""),
        observability: ObservabilityConfig {
            collector_endpoint: get_env(
                "PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT",
                &get_env("OTLP_ENDPOINT", &default_collector_endpoint()),
            ),
            collector_http_endpoint: get_env(
                "PHENO_OBSERVABILITY_OTLP_HTTP_ENDPOINT",
                &get_env("OTLP_HTTP_ENDPOINT", &default_collector_http_endpoint()),
            ),
            tracing_enabled: get_env_bool("TRACING_ENABLED", true)?,
            tracing_environment: get_env("TRACING_ENVIRONMENT", &get_env("ENV", &default_env())),
            tracing_service_name: get_env("OTEL_SERVICE_NAME", "tracera-live-backend"),
        },
        sentry: SentryConfig {
            dsn: get_env("SENTRY_DSN", ""),
            environment: get_env("SENTRY_ENVIRONMENT", &get_env("ENV", &default_env())),
            release: get_env("SENTRY_RELEASE", "unknown"),
            traces_sample_rate: get_env_f64("SENTRY_TRACES_SAMPLE_RATE", default_sentry_traces_sample_rate())?,
            debug: get_env_bool("SENTRY_DEBUG", false)?,
        },
        embeddings: load_embeddings_config()?,
    };
    let _ = env_value;
    Ok(cfg)
}

fn load_embeddings_config() -> Result<EmbeddingsConfig, ConfigError> {
    Ok(EmbeddingsConfig {
        provider: get_env("EMBEDDING_PROVIDER", "voyage"),
        voyage_api_key: get_env("VOYAGE_API_KEY", ""),
        voyage_model: get_env("VOYAGE_MODEL", "voyage-3.5"),
        voyage_dimensions: get_env_u32("VOYAGE_DIMENSIONS", default_voyage_dimensions())?,
        openrouter_api_key: get_env("OPENROUTER_API_KEY", ""),
        openrouter_model: get_env("OPENROUTER_MODEL", "openai/text-embedding-3-small"),
        rerank_enabled: get_env_bool("RERANK_ENABLED", true)?,
        rerank_model: get_env("RERANK_MODEL", "rerank-2.5"),
        rate_limit_per_minute: get_env_u32("EMBEDDING_RATE_LIMIT", default_embedding_rate_limit())?,
        timeout_seconds: get_env_u32("EMBEDDING_TIMEOUT", default_embedding_timeout())?,
        max_retries: get_env_u32("EMBEDDING_MAX_RETRIES", default_embedding_max_retries())?,
        max_batch_size: get_env_u32("EMBEDDING_BATCH_SIZE", default_embedding_batch_size())?,
        indexer_enabled: get_env_bool("INDEXER_ENABLED", true)?,
        indexer_workers: get_env_u32("INDEXER_WORKERS", default_indexer_workers())?,
        indexer_batch_size: get_env_u32("INDEXER_BATCH_SIZE", default_indexer_batch_size())?,
        indexer_poll_interval: get_env_u32("INDEXER_POLL_INTERVAL", default_indexer_poll_interval())?,
    })
}

pub fn get_required_env(key: &str, description: &str) -> Result<String, ConfigError> {
    match env::var(key) {
        Ok(v) if !v.is_empty() => Ok(v),
        _ => Err(ConfigError::RequiredMissing {
            key: key.to_string(),
            description: description.to_string(),
        }),
    }
}

pub fn get_env(key: &str, default_value: &str) -> String {
    env::var(key)
        .ok()
        .filter(|v| !v.is_empty())
        .unwrap_or_else(|| default_value.to_string())
}

fn get_env_list(key: &str) -> Vec<String> {
    env::var(key)
        .ok()
        .map(|v| v.split(',').map(|s| s.trim().to_string()).filter(|s| !s.is_empty()).collect())
        .unwrap_or_default()
}

pub fn get_env_int(key: &str, default_value: i64) -> Result<i64, ConfigError> {
    match env::var(key) {
        Ok(v) if !v.is_empty() => v.parse::<i64>().map_err(|e| ConfigError::InvalidInt {
            key: key.to_string(),
            value: v,
            source: e,
        }),
        _ => Ok(default_value),
    }
}

pub fn get_env_u32(key: &str, default_value: u32) -> Result<u32, ConfigError> {
    match env::var(key) {
        Ok(v) if !v.is_empty() => v.parse::<u32>().map_err(|e| ConfigError::InvalidInt {
            key: key.to_string(),
            value: v,
            source: e,
        }),
        _ => Ok(default_value),
    }
}

pub fn get_env_u16(key: &str, default_value: u16) -> Result<u16, ConfigError> {
    match env::var(key) {
        Ok(v) if !v.is_empty() => v.parse::<u16>().map_err(|e| ConfigError::InvalidInt {
            key: key.to_string(),
            value: v,
            source: e,
        }),
        _ => Ok(default_value),
    }
}

pub fn get_env_bool(key: &str, default_value: bool) -> Result<bool, ConfigError> {
    match env::var(key) {
        Ok(v) if !v.is_empty() => v.parse::<bool>().map_err(|e| ConfigError::InvalidBool {
            key: key.to_string(),
            value: v,
            source: e,
        }),
        _ => Ok(default_value),
    }
}

pub fn get_env_f64(key: &str, default_value: f64) -> Result<f64, ConfigError> {
    match env::var(key) {
        Ok(v) if !v.is_empty() => v.parse::<f64>().map_err(|e| ConfigError::InvalidFloat {
            key: key.to_string(),
            value: v,
            source: e,
        }),
        _ => Ok(default_value),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Mutex;

    // Env vars are process-global, so serialize tests that mutate them.
    static ENV_LOCK: Mutex<()> = Mutex::new(());

    fn with_env<F: FnOnce()>(vars: &[(&str, &str)], f: F) {
        let _guard = ENV_LOCK.lock().unwrap();
        let mut previous: Vec<(&str, Option<String>)> = Vec::new();
        for (k, _) in vars {
            previous.push((k, env::var(k).ok()));
        }
        for (k, v) in vars {
            env::set_var(k, v);
        }
        f();
        for (k, prev) in previous {
            match prev {
                Some(v) => env::set_var(k, v),
                None => env::remove_var(k),
            }
        }
    }

    #[test]
    fn defaults_apply_when_no_env() {
        with_env(&[], || {
            let cfg = load_from_env().unwrap();
            assert_eq!(cfg.http.port, 8080);
            assert_eq!(cfg.http.host, "127.0.0.1");
            assert_eq!(cfg.http.read_timeout_seconds, 30);
            assert_eq!(cfg.observability.tracing_enabled, true);
            assert_eq!(cfg.observability.tracing_service_name, "tracera-live-backend");
            assert_eq!(cfg.embeddings.provider, "voyage");
            assert_eq!(cfg.embeddings.voyage_model, "voyage-3.5");
            assert_eq!(cfg.embeddings.voyage_dimensions, 1024);
            assert_eq!(cfg.embeddings.rerank_model, "rerank-2.5");
            assert_eq!(cfg.embeddings.indexer_workers, 4);
            assert_eq!(cfg.sentry.traces_sample_rate, 0.1);
            assert_eq!(cfg.s3.region, "us-east-1");
            assert_eq!(cfg.python_backend_url, "http://127.0.0.1:8000");
        });
    }

    #[test]
    fn env_overrides_defaults() {
        with_env(
            &[
                ("HTTP_PORT", "9999"),
                ("TRACING_ENABLED", "false"),
                ("EMBEDDING_PROVIDER", "openrouter"),
                ("S3_REGION", "eu-west-1"),
                ("CORS_ALLOWED_ORIGINS", "https://a.com, https://b.com"),
                ("SENTRY_TRACES_SAMPLE_RATE", "0.42"),
            ],
            || {
                let cfg = load_from_env().unwrap();
                assert_eq!(cfg.http.port, 9999);
                assert_eq!(cfg.observability.tracing_enabled, false);
                assert_eq!(cfg.embeddings.provider, "openrouter");
                assert_eq!(cfg.s3.region, "eu-west-1");
                assert_eq!(cfg.http.cors_allowed_origins, vec!["https://a.com", "https://b.com"]);
                assert!((cfg.sentry.traces_sample_rate - 0.42).abs() < 1e-9);
            },
        );
    }

    #[test]
    fn invalid_int_returns_error() {
        with_env(&[("HTTP_PORT", "not-a-number")], || {
            let err = load_from_env().unwrap_err();
            match err {
                ConfigError::InvalidInt { key, value, .. } => {
                    assert_eq!(key, "HTTP_PORT");
                    assert_eq!(value, "not-a-number");
                }
                other => panic!("expected InvalidInt, got {:?}", other),
            }
        });
    }

    #[test]
    fn invalid_bool_returns_error() {
        with_env(&[("TRACING_ENABLED", "maybe")], || {
            let err = load_from_env().unwrap_err();
            match err {
                ConfigError::InvalidBool { key, value, .. } => {
                    assert_eq!(key, "TRACING_ENABLED");
                    assert_eq!(value, "maybe");
                }
                other => panic!("expected InvalidBool, got {:?}", other),
            }
        });
    }

    #[test]
    fn invalid_float_returns_error() {
        with_env(&[("SENTRY_TRACES_SAMPLE_RATE", "half")], || {
            let err = load_from_env().unwrap_err();
            match err {
                ConfigError::InvalidFloat { key, value, .. } => {
                    assert_eq!(key, "SENTRY_TRACES_SAMPLE_RATE");
                    assert_eq!(value, "half");
                }
                other => panic!("expected InvalidFloat, got {:?}", other),
            }
        });
    }

    #[test]
    fn required_env_errors_when_missing() {
        with_env(&[("SOME_KEY", "")], || {
            let err = get_required_env("SOME_KEY", "for unit test").unwrap_err();
            match err {
                ConfigError::RequiredMissing { key, description } => {
                    assert_eq!(key, "SOME_KEY");
                    assert_eq!(description, "for unit test");
                }
                other => panic!("expected RequiredMissing, got {:?}", other),
            }
        });
    }

    #[test]
    fn required_env_returns_value() {
        with_env(&[("SOME_SET_KEY", "hello")], || {
            let v = get_required_env("SOME_SET_KEY", "ok").unwrap();
            assert_eq!(v, "hello");
        });
    }

    #[test]
    fn get_env_returns_default_on_empty() {
        with_env(&[("EMPTY_KEY", "")], || {
            let v = get_env("EMPTY_KEY", "fallback");
            assert_eq!(v, "fallback");
        });
    }

    #[test]
    fn env_priority_observability_overrides() {
        with_env(
            &[
                ("OTLP_ENDPOINT", "internal:4317"),
                ("PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT", "pheno:4317"),
            ],
            || {
                let cfg = load_from_env().unwrap();
                assert_eq!(cfg.observability.collector_endpoint, "pheno:4317");
            },
        );
    }

    #[test]
    fn env_priority_observability_falls_back() {
        with_env(
            &[("OTLP_ENDPOINT", "internal:4317")],
            || {
                env::remove_var("PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT");
                let cfg = load_from_env().unwrap();
                assert_eq!(cfg.observability.collector_endpoint, "internal:4317");
            },
        );
    }

    #[test]
    fn list_parses_comma_separated() {
        with_env(&[("CORS_ALLOWED_ORIGINS", "a,b, c ,")], || {
            let cfg = load_from_env().unwrap();
            assert_eq!(cfg.http.cors_allowed_origins, vec!["a", "b", "c"]);
        });
    }

    #[test]
    fn embeddings_full_env_load() {
        with_env(
            &[
                ("EMBEDDING_PROVIDER", "voyage"),
                ("VOYAGE_MODEL", "voyage-3"),
                ("VOYAGE_DIMENSIONS", "2048"),
                ("RERANK_ENABLED", "true"),
                ("RERANK_MODEL", "rerank-3"),
                ("EMBEDDING_RATE_LIMIT", "120"),
                ("INDEXER_WORKERS", "8"),
            ],
            || {
                let cfg = load_from_env().unwrap();
                assert_eq!(cfg.embeddings.voyage_model, "voyage-3");
                assert_eq!(cfg.embeddings.voyage_dimensions, 2048);
                assert_eq!(cfg.embeddings.rerank_model, "rerank-3");
                assert_eq!(cfg.embeddings.rate_limit_per_minute, 120);
                assert_eq!(cfg.embeddings.indexer_workers, 8);
            },
        );
    }

    #[test]
    fn sentry_full_env_load() {
        with_env(
            &[
                ("SENTRY_DSN", "https://k@sentry.io/1"),
                ("SENTRY_ENVIRONMENT", "staging"),
                ("SENTRY_RELEASE", "v0.1.0"),
                ("SENTRY_TRACES_SAMPLE_RATE", "0.5"),
                ("SENTRY_DEBUG", "true"),
            ],
            || {
                let cfg = load_from_env().unwrap();
                assert_eq!(cfg.sentry.dsn, "https://k@sentry.io/1");
                assert_eq!(cfg.sentry.environment, "staging");
                assert_eq!(cfg.sentry.release, "v0.1.0");
                assert!((cfg.sentry.traces_sample_rate - 0.5).abs() < 1e-9);
                assert!(cfg.sentry.debug);
            },
        );
    }
}
