use super::*;
use crate::{sqlite_store::SqliteStore, store::Store};
use axum::body::{to_bytes, Body};
use std::{sync::Arc, time::Instant};
use tower::ServiceExt;

async fn fixture() -> (Router, Arc<SqliteStore>) {
    let pool = sqlx::sqlite::SqlitePoolOptions::new()
        .max_connections(1)
        .connect("sqlite::memory:")
        .await
        .unwrap();
    sqlx::migrate!("./migrations-sqlite")
        .run(&pool)
        .await
        .unwrap();
    let store = Arc::new(SqliteStore::new(pool));
    // More than one store page, with unrelated types before and after the ADRs.
    for n in 0..115 {
        let kind = if (100..111).contains(&n) {
            "adr"
        } else {
            "requirement"
        };
        let item: Item = serde_json::from_value(json!({
            "id":format!("item-{n:03}"), "projectId":"TRACERA", "type":kind,
            "view":"specifications", "title":format!("Persisted decision {n}"),
            "status":"accepted", "priority":"high", "version":3,
            "createdAt":"2026-10-16", "updatedAt":"2026-10-16", "adrNumber":format!("ADR-{n}"),
            "context":"Persisted context", "decision":"Persisted decision", "consequences":"Persisted consequences",
            "complianceScore":80, "metadata":{"source":"test"}, "tags":["safety"],
            "relatedRequirements":["requirement-1"], "lastVerifiedAt":"2026-10-16"
        })).unwrap();
        store.create_item(item).await.unwrap();
    }
    for (id, kind, project) in [
        ("c", "contract", "TRACERA"),
        ("f", "feature", "TRACERA"),
        ("s", "scenario", "TRACERA"),
        ("other", "adr", "OTHER"),
    ] {
        let item: Item = serde_json::from_value(json!({"id":id, "projectId":project, "type":kind,
            "view":"specifications", "title":id, "status":"active", "priority":"high", "version":1,
            "createdAt":"2026-10-16", "updatedAt":"2026-10-16", "featureId":"f",
            "contractType":"precondition", "description":"stored content"}))
        .unwrap();
        store.create_item(item).await.unwrap();
    }
    let state = AppState {
        store: store.clone(),
        version: "test".into(),
        backend: "sqlite",
        started_at: Instant::now(),
        workos_client: tracera_workos::WorkOSClient::default_for_router(),
        cache: None,
        neo4j: None,
        r2: None,
    };
    (crate::router::build_router(state), store)
}
async fn request(app: Router, method: &str, path: &str) -> (StatusCode, Value) {
    let token = crate::middleware::issue_csrf_token().await;
    let response = app
        .oneshot(
            http::Request::builder()
                .method(method)
                .uri(path)
                .header("origin", "http://127.0.0.1:18000")
                .header("x-csrf-token", token)
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();
    let status = response.status();
    let bytes = to_bytes(response.into_body(), 1024 * 1024).await.unwrap();
    (
        status,
        serde_json::from_slice(&bytes)
            .unwrap_or_else(|_| json!({"raw":String::from_utf8_lossy(&bytes)})),
    )
}
#[tokio::test]
async fn all_eight_list_and_detail_routes_use_persisted_type() {
    let (app, store) = fixture().await;
    for (kind, id, total) in [
        ("adrs", "item-100", 11),
        ("contracts", "c", 1),
        ("features", "f", 1),
        ("scenarios", "s", 1),
    ] {
        let (status, body) = request(
            app.clone(),
            "GET",
            &format!("/api/v1/{kind}?project_id=TRACERA"),
        )
        .await;
        assert_eq!(status, StatusCode::OK, "{kind}: {body}");
        assert_eq!(body["total"], total);
        assert_eq!(body[kind].as_array().unwrap().len(), total as usize);
        assert_eq!(body["has_more"], false);
        assert!(body[kind]
            .as_array()
            .unwrap()
            .iter()
            .all(|i| i["project_id"] == "TRACERA"));
        let (status, body) = request(app.clone(), "GET", &format!("/api/v1/{kind}/{id}")).await;
        assert_eq!(status, StatusCode::OK);
        assert_eq!(
            body,
            document(&store.get_item(id.into()).await.unwrap().unwrap())
        );
        assert_eq!(body["id"], id);
    }
}
#[tokio::test]
async fn all_three_stats_routes_match_actual_project_items() {
    let (app, _) = fixture().await;
    for (kind, total, status) in [
        ("adrs", 11, "accepted"),
        ("contracts", 1, "active"),
        ("features", 1, "active"),
    ] {
        let (code, body) = request(
            app.clone(),
            "GET",
            &format!("/api/v1/projects/TRACERA/{kind}/stats"),
        )
        .await;
        assert_eq!(code, StatusCode::OK, "{body}");
        assert_eq!(body["project_id"], "TRACERA");
        assert_eq!(body["total"], total);
        assert_eq!(body["by_status"][status], total);
        if kind == "adrs" {
            assert_eq!(body["average_compliance_score"], 80.0);
            assert_eq!(body["pending_verification"], 0);
            assert_eq!(body["requirements_linked"], 1);
        }
    }
}
#[tokio::test]
async fn project_scenario_route_filters_real_relationships() {
    let (app, _) = fixture().await;
    let (status, body) = request(
        app.clone(),
        "GET",
        "/api/v1/specifications/projects/TRACERA/scenarios?feature_id=f",
    )
    .await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(body["scenarios"][0]["id"], "s");
    assert_eq!(body["total"], 1);
    let (_, body) = request(app.clone(), "GET", "/api/v1/scenarios?feature_id=absent").await;
    assert_eq!(body["total"], 0);
    let (status, _) = request(
        app,
        "GET",
        "/api/v1/specifications/projects/TRACERA/scenarios?project_id=OTHER",
    )
    .await;
    assert_eq!(status, StatusCode::BAD_REQUEST);
}
#[tokio::test]
async fn all_ten_unavailable_templates_have_exact_501_contract() {
    let (app, _) = fixture().await;
    for (template, method) in [
        ("/api/v1/contracts/{id}/verify", "POST"),
        ("/api/v1/contracts/{id}/activities", "GET"),
        ("/api/v1/features/{id}/activities", "GET"),
        ("/api/v1/scenarios/{id}/run", "POST"),
        ("/api/v1/specifications/scenarios/{id}/activities", "GET"),
        (
            "/api/v1/specifications/projects/{project_id}/scenarios/activities",
            "GET",
        ),
        ("/api/v1/adrs/{id}/verify", "POST"),
        ("/api/v1/adrs/{id}/activities", "GET"),
        (
            "/api/v1/projects/{project_id}/specifications/summary",
            "GET",
        ),
        ("/api/v1/projects/{project_id}/specifications/stats", "GET"),
    ] {
        let uri = template
            .replace("{id}", "c")
            .replace("{project_id}", "TRACERA");
        let (status, body) = request(app.clone(), method, &uri).await;
        assert_eq!(status, StatusCode::NOT_IMPLEMENTED, "{uri}: {body}");
        assert_eq!(body, json!({"error":"not_implemented","route":template}));
    }
}
#[tokio::test]
async fn writes_never_report_success_or_mutate_items() {
    let (app, store) = fixture().await;
    for kind in ["adrs", "contracts", "features", "scenarios"] {
        for (method, suffix) in [
            ("POST", ""),
            ("PATCH", "/c"),
            ("PUT", "/c"),
            ("DELETE", "/c"),
        ] {
            let (status, body) =
                request(app.clone(), method, &format!("/api/v1/{kind}{suffix}")).await;
            assert_eq!(status, StatusCode::NOT_IMPLEMENTED);
            let route = if suffix.is_empty() {
                format!("/api/v1/{kind}")
            } else {
                format!("/api/v1/{kind}/{{id}}")
            };
            assert_eq!(body, json!({"error":"not_implemented","route":route}));
        }
    }
    assert!(store.get_item("c".into()).await.unwrap().is_some());
}
#[tokio::test]
async fn negative_controls_cover_missing_wrong_type_filters_and_pagination() {
    let (app, _) = fixture().await;
    for uri in [
        "/api/v1/adrs/absent",
        "/api/v1/adrs/c",
        "/api/v1/contracts/item-100",
    ] {
        assert_eq!(
            request(app.clone(), "GET", uri).await.0,
            StatusCode::NOT_FOUND
        );
    }
    let (_,body)=request(app.clone(),"GET","/api/v1/adrs?project_id=TRACERA&tags=safety&status=accepted&search=decision&limit=2&offset=9").await;
    assert_eq!(body["total"], 11);
    assert_eq!(body["adrs"].as_array().unwrap().len(), 2);
    assert_eq!(body["adrs"][0]["id"], "item-109");
    assert_eq!(body["has_more"], false);
    let (_, body) = request(app.clone(), "GET", "/api/v1/adrs?tags=missing").await;
    assert_eq!(body["total"], 0);
    for uri in [
        "/api/v1/adrs?limit=0",
        "/api/v1/adrs?limit=1001",
        "/api/v1/adrs?offset=100001",
        "/api/v1/adrs?unknown=yes",
    ] {
        assert_eq!(
            request(app.clone(), "GET", uri).await.0,
            StatusCode::BAD_REQUEST,
            "{uri}"
        );
    }
    let (_, body) = request(app, "GET", "/api/v1/contracts?contract_type=precondition").await;
    assert_eq!(body["total"], 1);
}
#[tokio::test]
async fn store_failure_budget_and_unknown_projects_never_become_empty_success() {
    let (app, store) = fixture().await;
    for uri in [
        "/api/v1/adrs?project_id=absent",
        "/api/v1/projects/absent/adrs/stats",
        "/api/v1/specifications/projects/absent/scenarios",
    ] {
        assert_eq!(
            request(app.clone(), "GET", uri).await.0,
            StatusCode::NOT_FOUND
        );
    }
    let connection = store.pool.acquire().await.unwrap();
    let (status, body) = request(app.clone(), "GET", "/api/v1/adrs").await;
    assert_eq!(status, StatusCode::SERVICE_UNAVAILABLE);
    assert_eq!(body["error"], "specs_query_over_budget");
    drop(connection);
    store.pool.close().await;
    for uri in [
        "/api/v1/adrs",
        "/api/v1/adrs/item-100",
        "/api/v1/projects/TRACERA/adrs/stats",
        "/api/v1/specifications/projects/TRACERA/scenarios",
    ] {
        let (status, body) = request(app.clone(), "GET", uri).await;
        assert_eq!(status, StatusCode::INTERNAL_SERVER_ERROR);
        assert_eq!(body["error"], "specs_store_error");
    }
}
#[tokio::test]
async fn incomplete_subtype_observations_are_preserved_and_never_invented() {
    let (app, store) = fixture().await;
    let mut adr = store.get_item("item-100".into()).await.unwrap().unwrap();
    adr.id = "unmeasured".into();
    adr.extra.insert("complianceScore".into(), json!("unknown"));
    adr.extra.remove("context");
    adr.extra.insert("project_id".into(), json!("OTHER"));
    adr.extra.insert("created_at".into(), json!("spoofed"));
    store.create_item(adr).await.unwrap();
    let (status, body) = request(app.clone(), "GET", "/api/v1/adrs/unmeasured").await;
    assert_eq!(status, StatusCode::OK);
    assert!(body.get("context").is_none());
    assert_eq!(body["compliance_score"], "unknown");
    assert_eq!(body["project_id"], "TRACERA");
    assert_eq!(body["created_at"], "2026-10-16");
    let (_, body) = request(app.clone(), "GET", "/api/v1/projects/TRACERA/adrs/stats").await;
    assert_eq!(body["total"], 12);
    assert!(body["average_compliance_score"].is_null());
    let (_, body) = request(app, "GET", "/api/v1/projects/TRACERA/features/stats").await;
    assert_eq!(body["total_scenarios"], 1);
    assert!(body["pass_rate"].is_null());
    assert!(body["coverage"]["percentage"].is_null());
}
