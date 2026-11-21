use axum::{
    body::Body,
    extract::State,
    http::{header::AUTHORIZATION, Request, StatusCode},
    middleware::Next,
    response::{IntoResponse, Response},
};
use std::sync::Arc;

pub(crate) type AuthToken = Option<Arc<str>>;

/// The authentication profile accepted by this server.
///
/// A router must be built with exactly one of the two supported profiles.
/// An unset profile explicitly defaults to the browser profile; an
/// unrecognised profile name is rejected before any request is served.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum AuthProfile {
    /// Browser clients: WorkOS AuthKit at the ingress, canonical Origin and
    /// a process-issued CSRF token for state-mutating requests.
    BrowserCsrfOrigin,
    /// Declared MCP service clients: a bearer token configured for this
    /// process. Browser CSRF checks do not apply to this profile.
    BearerService,
}

impl AuthProfile {
    pub(crate) const BROWSER_CSRF_ORIGIN: &'static str = "browser-csrf-origin";
    pub(crate) const BEARER_SERVICE: &'static str = "bearer-service";
    pub(crate) const ENV: &'static str = "TRACERA_AUTH_PROFILE";

    pub(crate) fn as_str(self) -> &'static str {
        match self {
            Self::BrowserCsrfOrigin => Self::BROWSER_CSRF_ORIGIN,
            Self::BearerService => Self::BEARER_SERVICE,
        }
    }

    /// Resolve the profile from the environment. An unset profile explicitly
    /// defaults to the browser profile. An invalid value is still rejected.
    pub(crate) fn from_env() -> Result<Self, String> {
        match std::env::var(Self::ENV) {
            Ok(raw) => Self::parse(&raw),
            Err(std::env::VarError::NotPresent) => {
                tracing::info!(
                    env = Self::ENV,
                    profile = Self::BROWSER_CSRF_ORIGIN,
                    "auth profile unset; using default browser profile"
                );
                Ok(Self::BrowserCsrfOrigin)
            }
            Err(std::env::VarError::NotUnicode(_)) => Err(format!(
                "{} must be valid Unicode when set to `{}` or `{}`",
                Self::ENV,
                Self::BROWSER_CSRF_ORIGIN,
                Self::BEARER_SERVICE
            )),
        }
    }

    pub(crate) fn parse(raw: &str) -> Result<Self, String> {
        match raw.trim() {
            Self::BROWSER_CSRF_ORIGIN => Ok(Self::BrowserCsrfOrigin),
            Self::BEARER_SERVICE => Ok(Self::BearerService),
            other => Err(format!(
                "unknown {} `{other}`; expected `{}` or `{}`",
                Self::ENV,
                Self::BROWSER_CSRF_ORIGIN,
                Self::BEARER_SERVICE
            )),
        }
    }
}

/// Protects application routes in the declared bearer service profile.
///
/// In the browser profile this middleware is not installed at all, so there
/// is no code path where a missing token can silently disable protection.
pub(crate) async fn require_bearer(
    State(expected): State<AuthToken>,
    request: Request<Body>,
    next: Next,
) -> Response {
    let Some(expected) = expected.as_ref() else {
        return (
            StatusCode::SERVICE_UNAVAILABLE,
            "auth profile bearer-service is not configured",
        )
            .into_response();
    };

    let valid = request
        .headers()
        .get(AUTHORIZATION)
        .and_then(|value| value.to_str().ok())
        .and_then(|value| value.strip_prefix("Bearer "))
        .is_some_and(|provided| constant_time_equal(provided.as_bytes(), expected.as_bytes()));

    if valid {
        next.run(request).await
    } else {
        (
            StatusCode::UNAUTHORIZED,
            [("www-authenticate", "Bearer")],
            "unauthorized",
        )
            .into_response()
    }
}

fn constant_time_equal(left: &[u8], right: &[u8]) -> bool {
    let mut difference = left.len() ^ right.len();
    for index in 0..left.len().max(right.len()) {
        difference |= usize::from(left.get(index).copied().unwrap_or_default())
            ^ usize::from(right.get(index).copied().unwrap_or_default());
    }
    difference == 0
}

#[cfg(test)]
mod tests {
    use super::{constant_time_equal, AuthProfile};

    #[test]
    fn constant_time_comparison_requires_exact_bytes() {
        assert!(constant_time_equal(b"token", b"token"));
        assert!(!constant_time_equal(b"token", b"Token"));
        assert!(!constant_time_equal(b"token", b"token-extra"));
    }

    #[test]
    fn only_two_explicit_profiles_parse() {
        assert_eq!(
            AuthProfile::parse("browser-csrf-origin"),
            Ok(AuthProfile::BrowserCsrfOrigin)
        );
        assert_eq!(
            AuthProfile::parse("bearer-service"),
            Ok(AuthProfile::BearerService)
        );
        assert!(AuthProfile::parse("").is_err());
        assert!(AuthProfile::parse("none").is_err());
        assert!(AuthProfile::parse("bearer").is_err());
    }
}
