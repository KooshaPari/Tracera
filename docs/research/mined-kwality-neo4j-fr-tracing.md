# Mined patterns: kwality → Tracera

**Source:** [KooshaPari/kwality](https://github.com/KooshaPari/kwality)
(read-only mine, 2026-05-31)

**Status:** kwality Neo4j FR-tracing research is superseded by **Tracera**.
These are **graph query and traceability patterns** — not a schema port.

## Why this doc exists

kwality used Neo4j to map requirements ↔ tests ↔ code and identify coverage
gaps via graph queries. Tracera is the stated successor for distributed tracing
with knowledge-graph backends. This doc captures query patterns and node
relationships worth preserving.

## Borrow: FR traceability graph model

kwality `database/neo4j/schemas/test-execution-schema.cypher` defines
production-grade constraints and indexes:

- Node labels: `TestExecution`, `TestCase`, `ValidationSuite`,
  `ValidationTarget`, `TestPattern`, `Agent`, `Component`
- Relationship types: `DEPENDS_ON`, `VALIDATED_BY`, `CONTAINS`, `TARGETS`,
  `FOLLOWS`, `TRIGGERS`, `IMPLEMENTS`
- Performance indexes on `status`, `executed_at`, `complexity_score`,
  `success_rate`

Conceptual FR overlay (map ValidationTarget → Requirement):

```text
(:Requirement {id, title, priority})
  -[:IMPLEMENTED_BY]-> (:Component {component_id, path})
  -[:VALIDATED_BY]-> (:TestCase {test_id, suite})
  -[:COVERS]-> (:Requirement)
(:TestCase) -[:USES_MCP_TOOL]-> (:Agent {agent_id, tool: "playwright"})
```

**Adopt in Tracera:** align span/resource attributes with FR IDs so graph
exports can reconstruct the same edges. Requirement nodes should use stable FR
identifiers from PhenoSpecs/AgilePlus registries.

## Borrow: coverage-gap queries

kwality targeted Cypher-style gap analysis:

```cypher
// Requirements with no verifying test
MATCH (r:Requirement)
WHERE NOT (r)<-[:COVERS]-(:TestCase)
RETURN r.id, r.title

// Tests orphaned from requirements
MATCH (t:TestCase)
WHERE NOT (t)-[:COVERS]->(:Requirement)
RETURN t.name, t.suite

// Code changed without linked FR (stale trace)
MATCH (c:CodeFile)-[:IMPLEMENTED_BY]->(r:Requirement)
WHERE c.last_modified > r.last_verified
RETURN c.path, r.id
```

**Adopt in Tracera:** implement equivalent gap reports as Tracera graph
analytics or export jobs — do not duplicate Neo4j in Benchora.

## Borrow: Playwright MCP server shape

kwality `playwright_mcp.py` pattern (from README structure):

- MCP tools: `browser_navigate`, `browser_click`, `browser_snapshot`,
  `browser_assert_text`
- LLM receives accessibility snapshots, not raw pixels
- Test runs emit spans linkable to `:TestCase` nodes

**Adopt in Tracera:** when ingesting Playwright MCP session traces, normalize
tool names and attach `test_case_id` + `requirement_ids` as span attributes
for graph reconstruction.

## Borrow: successor migration table (graph lane)

| kwality capability             | Tracera responsibility                |
| ------------------------------ | ------------------------------------- |
| Neo4j requirement graph        | Tracera graph backend + export        |
| FR gap analysis queries        | Tracera analytics / reports           |
| Playwright MCP trace ingestion | Tracera MCP span normalization        |
| DeepEval semantic scores       | **Benchora** (see deepeval mined doc) |

Benchora deepeval doc:
`docs/research/mined-kwality-deepeval-patterns.md`

## Do not borrow

- kwality docker-compose.kwality.yml full stack — simplify for Tracera dev
  only.
- DeepEval evaluator code — Benchora lane.
- kwality k8s/monitoring/nginx production manifests — aspirational, not
  migrated.

## Related fork-lane repos

| Repo     | Role                                                  |
| -------- | ----------------------------------------------------- |
| Benchora | DeepEval / FR validation patterns (mined doc in repo) |
| PhenoMCP | Standalone Playwright MCP tool successor              |

## Provenance

Read-only mine of [kwality](https://github.com/KooshaPari/kwality) README and
documented `neo4j_graph.py` / `playwright_mcp.py` structure on 2026-05-31.
