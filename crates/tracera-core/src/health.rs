// SPDX-License-Identifier: MIT OR Apache-2.0
// Copyright 2026 Koosha Pari

//! Process-level health-check registry used by `/healthz`, `/readyz`, and
//! `/startupz` HTTP probes.
//!
//! Each check is an object-safe trait (`HealthCheck`) so the registry can hold
//! a heterogeneous set of probes behind one mutex. The `check` method returns
//! a pinned, boxed future to stay compatible with the stable `async fn` in
//! trait story on Rust 1.82.

use std::collections::BTreeMap;
use std::future::Future;
use std::pin::Pin;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

use serde::{Deserialize, Serialize};
use thiserror::Error;

/// Kubernetes-style probe category.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ProbeType {
    /// Process is alive (cheap, never fails on dependencies).
    Liveness,
    /// Process is ready to serve traffic (may depend on downstream caches,
    /// DB pool, etc.).
    Readiness,
    /// Process has finished its first-time initialization (one-shot
    /// readiness variant used at boot).
    Startup,
}

/// Result of an individual health check.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "status", rename_all = "lowercase")]
pub enum HealthStatus {
    Healthy,
    Degraded,
    Unhealthy,
}

impl Default for HealthStatus {
    fn default() -> Self {
        Self::Healthy
    }
}

impl HealthStatus {
    /// True when the probe can accept traffic.
    pub fn is_serving(&self) -> bool {
        matches!(self, Self::Healthy | Self::Degraded)
    }
}

/// Failure modes for an individual health check.
#[derive(Debug, Error)]
pub enum HealthError {
    #[error("health check failed: {0}")]
    Failed(String),
    #[error("health check timed out after {0:?}")]
    Timeout(Duration),
    #[error("health check panicked: {0}")]
    Panicked(String),
}

/// Object-safe async health probe.
///
/// Implementors return a pinned, boxed future so the trait stays dyn-safe
/// even though `check` is logically async.
pub trait HealthCheck: Send + Sync {
    /// Stable identifier for the check (used as a key in [`HealthReport`]).
    fn name(&self) -> &str;

    /// Probe category; the registry uses this to group results.
    fn probe_type(&self) -> ProbeType;

    /// Run the check, returning a future that resolves to the status.
    fn check(
        &self,
    ) -> Pin<Box<dyn Future<Output = Result<HealthStatus, HealthError>> + Send + '_>>;
}

/// A single probe outcome, as reported back to operators.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProbeResult {
    pub name: String,
    pub probe_type: ProbeType,
    pub status: HealthStatus,
    pub latency_ms: u64,
    pub error: Option<String>,
}

/// Aggregated report for a category of probe (or all categories).
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct HealthReport {
    pub probes: BTreeMap<String, ProbeResult>,
    /// Highest-severity status across `probes` (`Unhealthy` > `Degraded` >
    /// `Healthy`).
    pub overall: HealthStatus,
}

impl HealthReport {
    /// Fold a single probe result into the report, updating the overall
    /// status to the most-severe entry seen so far.
    pub fn record(&mut self, result: ProbeResult) {
        self.overall = match (&self.overall, &result.status) {
            (HealthStatus::Unhealthy, _) | (_, HealthStatus::Unhealthy) => {
                HealthStatus::Unhealthy
            }
            (HealthStatus::Degraded, _) | (_, HealthStatus::Degraded) => {
                HealthStatus::Degraded
            }
            _ => HealthStatus::Healthy,
        };
        self.probes.insert(result.name.clone(), result);
    }
}

/// Registry of health checks. All mutations are guarded by a `Mutex`; reads
/// (via `run`) snapshot an `Arc` clone of each registered check and release
/// the lock before running the async work, so slow checks don't block
/// `register` calls.
pub struct HealthRegistry {
    checks: Mutex<Vec<Arc<dyn HealthCheck>>>,
}

impl Default for HealthRegistry {
    fn default() -> Self {
        Self::new()
    }
}

impl HealthRegistry {
    /// Create an empty registry.
    pub fn new() -> Self {
        Self {
            checks: Mutex::new(Vec::new()),
        }
    }

    /// Register a new health check. Replaces any prior check with the same
    /// `name()`.
    pub fn register<C: HealthCheck + 'static>(&self, check: C) {
        let mut checks = self.checks.lock().expect("health registry poisoned");
        checks.retain(|c| c.name() != check.name());
        checks.push(Arc::new(check));
    }

    /// Run every check of the given probe type, returning an aggregated
    /// [`HealthReport`].
    pub async fn run(&self, probe_type: ProbeType) -> HealthReport {
        // Snapshot the relevant checks as Arc clones so we can release the
        // registry mutex before awaiting any of them.
        let snapshot: Vec<Arc<dyn HealthCheck>> = {
            let checks = self.checks.lock().expect("health registry poisoned");
            checks
                .iter()
                .filter(|c| c.probe_type() == probe_type)
                .cloned()
                .collect()
        };

        let mut report = HealthReport::default();
        for c in snapshot {
            let started = Instant::now();
            let outcome = c.check().await;
            let latency_ms = started.elapsed().as_millis() as u64;
            let result = match outcome {
                Ok(status) => ProbeResult {
                    name: c.name().to_string(),
                    probe_type: c.probe_type(),
                    status,
                    latency_ms,
                    error: None,
                },
                Err(err) => ProbeResult {
                    name: c.name().to_string(),
                    probe_type: c.probe_type(),
                    status: HealthStatus::Unhealthy,
                    latency_ms,
                    error: Some(err.to_string()),
                },
            };
            report.record(result);
        }
        report
    }
}

// Concrete check adapters ------------------------------------------------

/// Adapt any `Fn() -> Future` into a `HealthCheck`. Useful for tests and for
/// wrapping ad-hoc probes without writing a new struct per probe.
pub struct FnCheck {
    name: String,
    probe_type: ProbeType,
    func: Box<
        dyn Fn() -> Pin<Box<dyn Future<Output = Result<HealthStatus, HealthError>> + Send>>
            + Send
            + Sync,
    >,
}

impl FnCheck {
    /// Create a new `FnCheck` from a name, probe type, and async closure.
    pub fn new<F, Fut>(name: impl Into<String>, probe_type: ProbeType, func: F) -> Self
    where
        F: Fn() -> Fut + Send + Sync + 'static,
        Fut: Future<Output = Result<HealthStatus, HealthError>> + Send + 'static,
    {
        Self {
            name: name.into(),
            probe_type,
            func: Box::new(move || {
                let fut = func();
                Box::pin(fut)
            }),
        }
    }
}

impl HealthCheck for FnCheck {
    fn name(&self) -> &str {
        &self.name
    }

    fn probe_type(&self) -> ProbeType {
        self.probe_type
    }

    fn check(
        &self,
    ) -> Pin<Box<dyn Future<Output = Result<HealthStatus, HealthError>> + Send + '_>> {
        (self.func)()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn block_on<F: std::future::Future>(fut: F) -> F::Output {
        // Tiny hand-rolled executor sufficient for the trivial async tests
        // below; avoids pulling tokio in just for two unit tests.
        use std::sync::Arc as StdArc;
        use std::task::{Context, Poll, Wake, Waker};

        struct Noop;
        impl Wake for Noop {
            fn wake(self: StdArc<Self>) {}
        }

        let waker = Waker::from(StdArc::new(Noop));
        let mut cx = Context::from_waker(&waker);
        let mut fut = Box::pin(fut);
        loop {
            if let Poll::Ready(v) = fut.as_mut().poll(&mut cx) {
                return v;
            }
        }
    }

    #[test]
    fn empty_registry_reports_healthy() {
        let registry = HealthRegistry::new();
        let report = block_on(registry.run(ProbeType::Liveness));
        assert_eq!(report.overall, HealthStatus::Healthy);
        assert!(report.probes.is_empty());
    }

    #[test]
    fn startup_probe_distinct_from_readiness() {
        let registry = HealthRegistry::new();
        registry.register(FnCheck::new("boot", ProbeType::Startup, || async {
            Ok(HealthStatus::Healthy)
        }));
        let startup = block_on(registry.run(ProbeType::Startup));
        assert_eq!(startup.overall, HealthStatus::Healthy);
        assert_eq!(startup.probes.len(), 1);
        // Readiness should not include startup probes.
        let readiness = block_on(registry.run(ProbeType::Readiness));
        assert!(readiness.probes.is_empty());
    }

    #[test]
    fn degraded_still_serves_traffic() {
        assert!(HealthStatus::Degraded.is_serving());
        assert!(HealthStatus::Healthy.is_serving());
        assert!(!HealthStatus::Unhealthy.is_serving());
    }

    #[test]
    fn default_status_is_healthy() {
        assert_eq!(HealthStatus::default(), HealthStatus::Healthy);
        assert!(HealthStatus::default().is_serving());
    }

    #[test]
    fn mixed_probes_produce_correct_overall() {
        let registry = HealthRegistry::new();
        registry.register(FnCheck::new("always_ok", ProbeType::Readiness, || async {
            Ok(HealthStatus::Healthy)
        }));
        registry.register(FnCheck::new("degraded", ProbeType::Readiness, || async {
            Ok(HealthStatus::Degraded)
        }));
        registry.register(FnCheck::new("broken", ProbeType::Readiness, || async {
            Err::<HealthStatus, _>(HealthError::Failed("nope".into()))
        }));
        // Liveness should be empty (we only registered readiness probes).
        let liveness = block_on(registry.run(ProbeType::Liveness));
        assert_eq!(liveness.overall, HealthStatus::Healthy);
        assert!(liveness.probes.is_empty());

        let readiness = block_on(registry.run(ProbeType::Readiness));
        assert_eq!(readiness.overall, HealthStatus::Unhealthy);
        assert_eq!(readiness.probes.len(), 3);
        let broken = readiness.probes.get("broken").unwrap();
        assert!(broken.error.is_some());
    }
}
