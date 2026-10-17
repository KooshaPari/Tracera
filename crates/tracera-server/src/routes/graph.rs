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
#[path = "graph_tests.rs"]
mod tests;

// W9 unavailable routes (generated).
pub(super) const W9_ROUTES: &[&str] = &[
    "/api/v1/graph/analysis/cache/invalidate",
    "/api/v1/projects/{project_id}/graph",
    "/api/v1/projects/{project_id}/graph/viewport",
];
pub(super) fn w9_routes() -> axum::Router<AppState> {
    super::w9_routes::unavailable_routes(W9_ROUTES)
}
