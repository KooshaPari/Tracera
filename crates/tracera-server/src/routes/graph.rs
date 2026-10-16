//! Graph queries over the current persisted SWEE graph through `Store`.
//! Canonical traceability persistence (#1126) is not on main yet. These routes
//! deliberately do not synthesize a graph from client input or trace-link subsets.
//! Successful responses use {items,total,limit,offset,has_more,store}; full emits
//! tagged nodes followed by tagged edges. IDs are SWEE IDs, not artifact IDs.
//! All directed edges participate in reachability and cycle analysis. Cycles
//! reports cyclic SCCs; dependencies follows direct depends_on edges only.
//! Cycle analysis returns 503 above 500 nodes to bound repeated reachability.
//! Unknown query options are rejected; project/depth filtering is unsupported.
use crate::{store::Store, AppState};
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
};
use serde::Deserialize;
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet, VecDeque};
type Reply = Result<Json<Value>, (StatusCode, Json<Value>)>;
fn error(status: StatusCode, code: &str) -> (StatusCode, Json<Value>) {
    (status, Json(json!({"error": code})))
}
#[derive(Default, Deserialize)]
#[serde(deny_unknown_fields)]
pub(super) struct Params {
    limit: Option<usize>,
    offset: Option<usize>,
    source: Option<String>,
    target: Option<String>,
}
impl Params {
    fn page(&self, items: Vec<Value>) -> Reply {
        let limit = self.limit.unwrap_or(50);
        if !(1..=100).contains(&limit) {
            return Err(error(StatusCode::BAD_REQUEST, "limit_must_be_1_to_100"));
        }
        let total = items.len();
        let offset = self.offset.unwrap_or(0);
        let items: Vec<_> = items.into_iter().skip(offset).take(limit).collect();
        Ok(Json(json!({"items": items, "total": total, "limit": limit,
            "offset": offset, "has_more": offset.saturating_add(items.len()) < total,
            "store": "swee"})))
    }
    fn validate(&self) -> Result<(), (StatusCode, Json<Value>)> {
        self.page(Vec::new()).map(|_| ())
    }
}
struct Graph {
    nodes: BTreeMap<String, Value>,
    edges: Vec<Value>,
    adj: BTreeMap<String, BTreeSet<String>>,
}
impl Graph {
    async fn load(store: &dyn Store) -> Result<Self, (StatusCode, Json<Value>)> {
        let nodes = store
            .list_swee_nodes(None)
            .await
            .map_err(|_| error(StatusCode::INTERNAL_SERVER_ERROR, "graph_store_error"))?;
        let mut edges = store
            .list_swee_edges(None)
            .await
            .map_err(|_| error(StatusCode::INTERNAL_SERVER_ERROR, "graph_store_error"))?;
        let nodes: BTreeMap<_, _> = nodes
            .into_iter()
            .map(|n| (n["id"].as_str().unwrap_or("").to_owned(), n))
            .collect();
        let mut adj: BTreeMap<_, BTreeSet<_>> = nodes
            .keys()
            .map(|id| (id.clone(), BTreeSet::new()))
            .collect();
        for edge in &edges {
            let (Some(source), Some(target)) =
                (edge["source_id"].as_str(), edge["target_id"].as_str())
            else {
                return Err(error(
                    StatusCode::INTERNAL_SERVER_ERROR,
                    "invalid_graph_edge",
                ));
            };
            if !nodes.contains_key(source) || !nodes.contains_key(target) {
                return Err(error(StatusCode::CONFLICT, "dangling_graph_edge"));
            }
            adj.get_mut(source).unwrap().insert(target.to_owned());
        }
        edges.sort_by_key(|edge| edge["id"].as_str().unwrap_or("").to_owned());
        Ok(Self { nodes, edges, adj })
    }
    fn require(&self, id: &str) -> Result<(), (StatusCode, Json<Value>)> {
        if self.nodes.contains_key(id) {
            Ok(())
        } else {
            Err(error(StatusCode::NOT_FOUND, "graph_node_not_found"))
        }
    }
    fn reachable(&self, id: &str, reverse: bool) -> BTreeSet<String> {
        let mut seen = BTreeSet::from([id.to_owned()]);
        let mut queue = VecDeque::from([id.to_owned()]);
        while let Some(node) = queue.pop_front() {
            let neighbors: Vec<_> = if reverse {
                self.adj
                    .iter()
                    .filter(|(_, targets)| targets.contains(&node))
                    .map(|(n, _)| n.clone())
                    .collect()
            } else {
                self.adj[&node].iter().cloned().collect()
            };
            for next in neighbors {
                if seen.insert(next.clone()) {
                    queue.push_back(next);
                }
            }
        }
        seen.remove(id);
        seen
    }
    fn values(&self, ids: impl IntoIterator<Item = String>) -> Vec<Value> {
        ids.into_iter().map(|id| self.nodes[&id].clone()).collect()
    }
}
pub(super) async fn full(State(state): State<AppState>, Query(p): Query<Params>) -> Reply {
    p.validate()?;
    let graph = Graph::load(state.store.as_ref()).await?;
    let items = graph
        .nodes
        .into_values()
        .map(|node| json!({"kind":"node", "node":node}))
        .chain(
            graph
                .edges
                .into_iter()
                .map(|edge| json!({"kind":"edge", "edge":edge})),
        )
        .collect();
    p.page(items)
}
pub(super) async fn orphans(State(state): State<AppState>, Query(p): Query<Params>) -> Reply {
    p.validate()?;
    let graph = Graph::load(state.store.as_ref()).await?;
    let connected: BTreeSet<_> = graph
        .adj
        .iter()
        .filter(|(_, to)| !to.is_empty())
        .flat_map(|(from, to)| std::iter::once(from.clone()).chain(to.iter().cloned()))
        .collect();
    p.page(
        graph.values(
            graph
                .nodes
                .keys()
                .filter(|id| !connected.contains(*id))
                .cloned(),
        ),
    )
}
pub(super) async fn topo(State(state): State<AppState>, Query(p): Query<Params>) -> Reply {
    p.validate()?;
    let graph = Graph::load(state.store.as_ref()).await?;
    let mut indegree: BTreeMap<_, usize> = graph.nodes.keys().map(|n| (n.clone(), 0)).collect();
    for targets in graph.adj.values() {
        for t in targets {
            *indegree.get_mut(t).unwrap() += 1;
        }
    }
    let mut ready: BTreeSet<_> = indegree
        .iter()
        .filter(|(_, d)| **d == 0)
        .map(|(n, _)| n.clone())
        .collect();
    let mut order = Vec::new();
    while let Some(node) = ready.pop_first() {
        for target in &graph.adj[&node] {
            let degree = indegree.get_mut(target).unwrap();
            *degree -= 1;
            if *degree == 0 {
                ready.insert(target.clone());
            }
        }
        order.push(node);
    }
    if order.len() != graph.nodes.len() {
        return Err(error(StatusCode::CONFLICT, "graph_contains_cycle"));
    }
    p.page(graph.values(order))
}
pub(super) async fn path(State(state): State<AppState>, Query(p): Query<Params>) -> Reply {
    p.validate()?;
    let graph = Graph::load(state.store.as_ref()).await?;
    let (Some(source), Some(target)) = (&p.source, &p.target) else {
        return Err(error(StatusCode::BAD_REQUEST, "source_and_target_required"));
    };
    graph.require(source)?;
    graph.require(target)?;
    let mut parents = BTreeMap::from([(source.clone(), source.clone())]);
    let mut queue = VecDeque::from([source.clone()]);
    while let Some(node) = queue.pop_front() {
        if &node == target {
            break;
        }
        for next in &graph.adj[&node] {
            if !parents.contains_key(next) {
                parents.insert(next.clone(), node.clone());
                queue.push_back(next.clone());
            }
        }
    }
    if !parents.contains_key(target) {
        return Err(error(StatusCode::NOT_FOUND, "graph_path_not_found"));
    }
    let mut result = vec![target.clone()];
    while result.last().unwrap() != source {
        result.push(parents[result.last().unwrap()].clone());
    }
    result.reverse();
    p.page(graph.values(result))
}
pub(super) async fn ancestors(
    State(s): State<AppState>,
    Path(id): Path<String>,
    Query(p): Query<Params>,
) -> Reply {
    related(s, id, p, true, false).await
}
pub(super) async fn descendants(
    State(s): State<AppState>,
    Path(id): Path<String>,
    Query(p): Query<Params>,
) -> Reply {
    related(s, id, p, false, false).await
}
pub(super) async fn dependencies(
    State(s): State<AppState>,
    Path(id): Path<String>,
    Query(p): Query<Params>,
) -> Reply {
    related(s, id, p, false, true).await
}
async fn related(state: AppState, id: String, p: Params, reverse: bool, direct: bool) -> Reply {
    p.validate()?;
    let graph = Graph::load(state.store.as_ref()).await?;
    graph.require(&id)?;
    // Dependencies are direct outgoing depends_on edges; ancestors/descendants follow all
    // edge kinds in the incoming/outgoing direction respectively.
    let ids = if direct {
        graph
            .edges
            .iter()
            .filter(|e| e["source_id"] == id && e["edge_type"] == "depends_on")
            .map(|e| e["target_id"].as_str().unwrap().to_owned())
            .collect()
    } else {
        graph.reachable(&id, reverse)
    };
    p.page(graph.values(ids))
}
pub(super) async fn cycles(State(state): State<AppState>, Query(p): Query<Params>) -> Reply {
    p.validate()?;
    let graph = Graph::load(state.store.as_ref()).await?;
    // Cyclic strongly connected components, not exponential simple-cycle enumeration.
    if graph.nodes.len() > 500 {
        return Err(error(
            StatusCode::SERVICE_UNAVAILABLE,
            "cycle_query_graph_too_large",
        ));
    }
    let mut remaining: BTreeSet<_> = graph.nodes.keys().cloned().collect();
    let mut components = Vec::new();
    while let Some(id) = remaining.pop_first() {
        let forward = graph.reachable(&id, false);
        let reverse = graph.reachable(&id, true);
        let mut component: BTreeSet<_> = forward.intersection(&reverse).cloned().collect();
        component.insert(id.clone());
        for node in &component {
            remaining.remove(node);
        }
        if component.len() > 1 || graph.adj[&id].contains(&id) {
            components
                .push(json!({"node_ids":component, "kind":"cyclic_strongly_connected_component"}));
        }
    }
    p.page(components)
}
pub(super) async fn unsupported(Query(p): Query<Params>) -> Reply {
    p.validate()?;
    Err((
        StatusCode::NOT_IMPLEMENTED,
        Json(json!({"error":"not_implemented",
        "message":"exhaustive paths, impact scoring and configurable traversal are not implemented for the current Store graph"})),
    ))
}
#[cfg(test)]
mod tests {
    use super::*;
    use crate::{sqlite_store::SqliteStore, store::Store};
    use axum::{
        body::{to_bytes, Body},
        Router,
    };
    use std::{sync::Arc, time::Instant};
    use tower::ServiceExt;
    async fn fixture() -> (Router, Arc<SqliteStore>, Vec<String>) {
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
        let mut ids = Vec::new();
        for name in ["root", "middle", "leaf", "isolated"] {
            ids.push(
                store
                    .create_swee_node(
                        "artifact".into(),
                        name.into(),
                        json!({}),
                        chrono::Utc::now(),
                    )
                    .await
                    .unwrap(),
            );
        }
        for (from, to) in [(0, 1), (1, 2)] {
            store
                .create_swee_edge(
                    "depends_on".into(),
                    ids[from].clone(),
                    ids[to].clone(),
                    1.0,
                    "manual".into(),
                    json!({}),
                    chrono::Utc::now(),
                )
                .await
                .unwrap();
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
        let app = crate::router::build_router(state);
        (app, store, ids)
    }
    async fn request(app: Router, uri: &str) -> (StatusCode, Value) {
        let response = app
            .oneshot(
                http::Request::builder()
                    .uri(format!("/api/v1/graph{uri}"))
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();
        let status = response.status();
        let body = to_bytes(response.into_body(), 1024 * 1024).await.unwrap();
        (status, serde_json::from_slice(&body).unwrap())
    }
    #[tokio::test]
    async fn graph_routes_read_sqlite_data() {
        let (app, _, ids) = fixture().await;
        for (route, count) in [
            ("/full".to_owned(), 6),
            ("/orphans".to_owned(), 1),
            ("/topo-sort".to_owned(), 4),
            (format!("/path?source={}&target={}", ids[0], ids[2]), 3),
            (format!("/ancestors/{}", ids[2]), 2),
            (format!("/descendants/{}", ids[0]), 2),
            (format!("/dependencies/{}", ids[0]), 1),
            ("/cycles".to_owned(), 0),
        ] {
            let (status, body) = request(app.clone(), &route).await;
            assert_eq!(status, StatusCode::OK, "{route}: {body}");
            assert_eq!(body["total"], count, "{route}");
        }
        let (_, orphan) = request(app.clone(), "/orphans").await;
        assert_eq!(orphan["items"][0]["id"], ids[3]);
        let (_, path) = request(app, &format!("/path?source={}&target={}", ids[0], ids[2])).await;
        assert_eq!(
            path["items"]
                .as_array()
                .unwrap()
                .iter()
                .map(|n| n["id"].as_str().unwrap())
                .collect::<Vec<_>>(),
            ids.iter().take(3).map(String::as_str).collect::<Vec<_>>()
        );
    }
    #[tokio::test]
    async fn cycles_and_topology_detect_persisted_cycle() {
        let (app, store, ids) = fixture().await;
        store
            .create_swee_edge(
                "depends_on".into(),
                ids[2].clone(),
                ids[0].clone(),
                1.0,
                "manual".into(),
                json!({}),
                chrono::Utc::now(),
            )
            .await
            .unwrap();
        let (status, cycles) = request(app.clone(), "/cycles").await;
        assert_eq!(status, StatusCode::OK);
        assert_eq!(cycles["total"], 1);
        assert_eq!(cycles["items"][0]["node_ids"], json!(&ids[..3]));
        let (status, body) = request(app, "/topo-sort").await;
        assert_eq!(status, StatusCode::CONFLICT);
        assert_eq!(body["error"], "graph_contains_cycle");
    }
    #[tokio::test]
    async fn pagination_and_negative_controls() {
        let (app, _, ids) = fixture().await;
        let (_, body) = request(app.clone(), "/full?limit=2&offset=2").await;
        assert_eq!(body["items"].as_array().unwrap().len(), 2);
        assert_eq!(body["total"], 6);
        assert_eq!(body["has_more"], true);
        for uri in ["/full?limit=101", "/cycles?limit=0", "/path"] {
            assert_eq!(request(app.clone(), uri).await.0, StatusCode::BAD_REQUEST);
        }
        for uri in [
            "/ancestors/missing".into(),
            format!("/path?source={}&target={}", ids[2], ids[0]),
        ] {
            assert_eq!(request(app.clone(), &uri).await.0, StatusCode::NOT_FOUND);
        }
        for uri in ["/paths", "/impact/1", "/traverse/1"] {
            let (status, body) = request(app.clone(), uri).await;
            assert_eq!(status, StatusCode::NOT_IMPLEMENTED);
            assert_eq!(body["error"], "not_implemented");
        }
    }
    #[tokio::test]
    async fn empty_graph_self_loop_and_store_failure() {
        let (app, store, ids) = fixture().await;
        store
            .create_swee_edge(
                "depends_on".into(),
                ids[3].clone(),
                ids[3].clone(),
                1.0,
                "manual".into(),
                json!({}),
                chrono::Utc::now(),
            )
            .await
            .unwrap();
        let (_, body) = request(app.clone(), "/cycles").await;
        assert_eq!(body["items"][0]["node_ids"], json!([ids[3]]));
        assert_eq!(
            request(app.clone(), "/topo-sort").await.0,
            StatusCode::CONFLICT
        );
        sqlx::query("DELETE FROM swee_edges")
            .execute(&store.pool)
            .await
            .unwrap();
        sqlx::query("DELETE FROM swee_nodes")
            .execute(&store.pool)
            .await
            .unwrap();
        for route in ["/full", "/cycles", "/orphans", "/topo-sort"] {
            let (status, body) = request(app.clone(), route).await;
            assert_eq!(status, StatusCode::OK);
            assert_eq!(body["total"], 0);
        }
        let (_, body) = request(app.clone(), "/full?limit=100&offset=18446744073709551615").await;
        assert_eq!(body["has_more"], false);
        sqlx::raw_sql("PRAGMA foreign_keys=OFF; INSERT INTO swee_edges(source_id,target_id,type) VALUES(999,998,'depends_on');").execute(&store.pool).await.unwrap();
        assert_eq!(
            request(app.clone(), "/cycles").await.0,
            StatusCode::CONFLICT
        );
        sqlx::query("DELETE FROM swee_edges")
            .execute(&store.pool)
            .await
            .unwrap();
        sqlx::query("WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n WHERE x<501) INSERT INTO swee_nodes(type,name) SELECT 'artifact','bulk' FROM n").execute(&store.pool).await.unwrap();
        let (status, body) = request(app.clone(), "/cycles").await;
        assert_eq!(status, StatusCode::SERVICE_UNAVAILABLE);
        assert_eq!(body["error"], "cycle_query_graph_too_large");
        sqlx::query("DROP TABLE swee_edges")
            .execute(&store.pool)
            .await
            .unwrap();
        let (status, body) = request(app, "/cycles").await;
        assert_eq!(status, StatusCode::INTERNAL_SERVER_ERROR);
        assert_eq!(body["error"], "graph_store_error");
    }
}
