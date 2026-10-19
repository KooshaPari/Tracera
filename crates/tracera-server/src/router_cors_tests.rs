use super::{collect_cors_allowed_origins, CANONICAL_CORS_ORIGINS};
use http::HeaderValue;

fn origin_strings(origins: &[HeaderValue]) -> Vec<String> {
    origins
        .iter()
        .map(|value| {
            value
                .to_str()
                .expect("origin must be valid UTF-8")
                .to_string()
        })
        .collect()
}

#[test]
fn unset_env_allows_canonical_origins_only() {
    let origins = collect_cors_allowed_origins(None);
    let strings = origin_strings(&origins);

    assert_eq!(origins.len(), CANONICAL_CORS_ORIGINS.len());
    for canonical in CANONICAL_CORS_ORIGINS {
        assert!(
            strings.contains(&(*canonical).to_string()),
            "missing canonical origin {canonical}"
        );
    }
}

#[test]
fn production_regression_local_env_does_not_drop_deployed_frontends() {
    let origins = collect_cors_allowed_origins(Some("http://127.0.0.1:18000"));
    let strings = origin_strings(&origins);

    assert!(strings.contains(&"https://tracera-kappa.vercel.app".to_string()));
    assert!(strings.contains(&"https://tracera.pheno.studio".to_string()));
    assert!(strings.contains(&"http://127.0.0.1:18000".to_string()));
    assert_eq!(
        strings
            .iter()
            .filter(|origin| *origin == "http://127.0.0.1:18000")
            .count(),
        1,
        "duplicate local origin should be removed"
    );
}

#[test]
fn env_adds_comma_separated_origins() {
    let origins =
        collect_cors_allowed_origins(Some("https://staging.example, https://preview.example"));
    let strings = origin_strings(&origins);

    assert!(strings.contains(&"https://tracera-kappa.vercel.app".to_string()));
    assert!(strings.contains(&"https://staging.example".to_string()));
    assert!(strings.contains(&"https://preview.example".to_string()));
}

#[test]
fn invalid_env_origin_is_skipped_without_panicking() {
    let origins = collect_cors_allowed_origins(Some(
        "https://extra.example, bad\norigin, https://another.example",
    ));
    let strings = origin_strings(&origins);

    assert!(strings.contains(&"https://tracera-kappa.vercel.app".to_string()));
    assert!(strings.contains(&"https://extra.example".to_string()));
    assert!(strings.contains(&"https://another.example".to_string()));
    assert!(
        !strings.iter().any(|origin| origin.contains('\n')),
        "invalid origin must not appear in allow list"
    );
}
