//! Cypher query builders for common SWEE graph analyses.

use neo4rs::Query;

/// Return a bounded shortest path between two SWEE nodes.
pub fn shortest_path(source: i64, target: i64, max_hops: usize) -> Query {
    Query::new(
        "MATCH (source:SWEE {id: $source}), (target:SWEE {id: $target}) CALL { WITH source, target MATCH path = (source)-[:SWEE_EDGE*..]->(target) RETURN path ORDER BY length(path) LIMIT 1 } RETURN source.id AS source_id, target.id AS target_id, length(path) AS hops, [node IN nodes(path) | {id: node.id, kind: node.kind, name: node.name}] AS path",
    )
    .param("source", source)
    .param("target", target)
    .param("max_hops", max_hops as i64)
}

/// Return weighted degree centrality for all SWEE nodes.
pub fn centrality() -> Query {
    Query::new(
        "MATCH (n:SWEE) OPTIONAL MATCH (n)-[out:SWEE_EDGE]->() OPTIONAL MATCH (in)-[incoming:SWEE_EDGE]->(n) RETURN n.id AS id, n.kind AS kind, n.name AS name, count(DISTINCT out) AS out_degree, count(DISTINCT incoming) AS in_degree, coalesce(sum(out.weight), 0) + coalesce(sum(incoming.weight), 0) AS weighted_degree ORDER BY weighted_degree DESC",
    )
}

/// Return connected components as communities.
pub fn community_detection() -> Query {
    Query::new(
        "MATCH (n:SWEE) WITH collect(n) AS nodes UNWIND nodes AS start CALL { WITH start MATCH path = (start)-[:SWEE_EDGE*]->(member) RETURN collect(DISTINCT member) + [start] AS members } WITH members, reduce(s = 0, member IN members | s + size((member)--())) AS score UNWIND members AS member RETURN member.id AS id, member.kind AS kind, member.name AS name, score ORDER BY score DESC",
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn query_builders_contain_analysis_operations() {
        let shortest = shortest_path(1, 2, 10).to_string();
        assert!(shortest.contains("MATCH path"));
        assert!(shortest.contains("$source"));
        assert!(centrality().to_string().contains("weighted_degree"));
        assert!(community_detection().to_string().contains("SWEE_EDGE"));
    }
}
