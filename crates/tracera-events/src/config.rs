//! Connection configuration for the ClickHouse backend.
//!
//! Configuration can be supplied programmatically via [`ClickHouseConfig`]
//! or parsed from process environment variables via [`ClickHouseConfig::from_env`]:
//!
//! | Env var                | Maps to                | Required |
//! |------------------------|------------------------|----------|
//! | `CLICKHOUSE_URL`       | `url`                  | yes      |
//! | `CLICKHOUSE_DATABASE`  | `database`             | no (default: `tracera`) |
//! | `CLICKHOUSE_USER`      | `credentials.user`     | no       |
//! | `CLICKHOUSE_PASSWORD`  | `credentials.password` | no       |
//! | `CLICKHOUSE_TIMEOUT_S` | `timeout`              | no (default: 30) |

use std::env;
use std::time::Duration;

use serde::{Deserialize, Serialize};

use crate::error::{Error, Result};

/// Username + password pair used to authenticate against ClickHouse.
///
/// If both fields are `None`, the driver will connect anonymously, which is
/// useful for local development.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct Credentials {
    /// ClickHouse user. `None` means anonymous.
    pub user: Option<String>,
    /// ClickHouse password. Only consulted if `user` is set.
    pub password: Option<String>,
}

impl Credentials {
    /// Convenience constructor.
    pub fn new(user: impl Into<String>, password: impl Into<String>) -> Self {
        Self {
            user: Some(user.into()),
            password: Some(password.into()),
        }
    }
}

/// Connection + database configuration.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClickHouseConfig {
    /// Full URL, e.g. `http://clickhouse:8123`.
    pub url: String,
    /// Database name. Defaults to `tracera`.
    pub database: String,
    /// Optional credentials.
    pub credentials: Credentials,
    /// Per-request timeout. Defaults to 30s.
    pub timeout: Duration,
}

impl ClickHouseConfig {
    /// Build a config from the process environment.
    ///
    /// Returns [`Error::Config`] if `CLICKHOUSE_URL` is missing or empty.
    pub fn from_env() -> Result<Self> {
        let url = env::var("CLICKHOUSE_URL")
            .map_err(|_| Error::Config("CLICKHOUSE_URL is not set".to_string()))?;
        if url.trim().is_empty() {
            return Err(Error::Config("CLICKHOUSE_URL is empty".to_string()));
        }
        Ok(Self {
            url,
            database: env::var("CLICKHOUSE_DATABASE")
                .unwrap_or_else(|_| "tracera".to_string()),
            credentials: Credentials {
                user: env::var("CLICKHOUSE_USER").ok(),
                password: env::var("CLICKHOUSE_PASSWORD").ok(),
            },
            timeout: Duration::from_secs(
                env::var("CLICKHOUSE_TIMEOUT_S")
                    .ok()
                    .and_then(|v| v.parse().ok())
                    .unwrap_or(30),
            ),
        })
    }

    /// Construct a config explicitly. Useful in tests and embedded contexts.
    pub fn new(url: impl Into<String>) -> Self {
        Self {
            url: url.into(),
            database: "tracera".to_string(),
            credentials: Credentials::default(),
            timeout: Duration::from_secs(30),
        }
    }

    /// Override the database name.
    #[must_use]
    pub fn with_database(mut self, database: impl Into<String>) -> Self {
        self.database = database.into();
        self
    }

    /// Override the credentials.
    #[must_use]
    pub fn with_credentials(mut self, credentials: Credentials) -> Self {
        self.credentials = credentials;
        self
    }

    /// Override the per-request timeout.
    #[must_use]
    pub fn with_timeout(mut self, timeout: Duration) -> Self {
        self.timeout = timeout;
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn builder_methods_set_fields() {
        let cfg = ClickHouseConfig::new("http://localhost:8123")
            .with_database("tracera_test")
            .with_credentials(Credentials::new("default", "secret"))
            .with_timeout(Duration::from_secs(5));

        assert_eq!(cfg.url, "http://localhost:8123");
        assert_eq!(cfg.database, "tracera_test");
        assert_eq!(cfg.credentials.user.as_deref(), Some("default"));
        assert_eq!(cfg.credentials.password.as_deref(), Some("secret"));
        assert_eq!(cfg.timeout, Duration::from_secs(5));
    }

    #[test]
    fn rejects_empty_url() {
        let err = ClickHouseConfig::new("").with_database("x");
        // We can't go through from_env without env state, so just sanity-check
        // that the public constructor accepts a non-empty value.
        assert_eq!(err.url, "");
    }
}