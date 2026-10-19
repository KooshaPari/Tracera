# Product spatial ontology — prior to geometry

**Status:** proposed semantic mapping. The Rust product-first layer remains the actual candidate authority; this document does not declare new persisted enums or migrations.

## Semantic entity classes

| Class | Canonical meaning | Example representation |
| --- | --- | --- |
| Product | Stable cross-repository subject and scope | Outer assembly/world |
| Capability | User-observable ability | Accessible mechanism/control |
| Obligation/requirement/target | Accepted condition, rule, measurable expectation | Instrument, acceptance fixture or obligation plate |
| Component/subsystem/interface | Architecturally typed structure | Module and connector |
| Behavior/state transition | Observable or specified action over time | Active machine segment or process |
| Evidence/observation/assessment | Provenance-bound assertion with outcome | Inspectable measurement channel |
| Actor/principal | Authorized initiator, human or software | Labeled operator/agent role (not implicit authority) |
| Asset/physical geometry | Sourced CAD, mechanical design or visual resource | Literal mesh with units and source |
| Derived aggregate | View-level cluster over canonical members | Collapsed enclosure, explicit member mapping |

## Relations

Preserve independently typed `contains`, `depends_on`, `implements`, `satisfies`, `verifies`, `observed_in`, `deployed_as`, `connected_to` and temporal relations **only where existing schema supports them or new schema is separately accepted**. An illustrative line is not a dependency and spatial proximity is not a relation.

## Formal invariants

1. Every selectable glyph has a stable canonical `entity_ref` or typed `aggregate_ref` and member-query reference.
2. A scene transform or bounding box is not an authoritative property of the product unless marked **physical** or **measured**, with units/frame/provenance.
3. `projection_signature = H(model revision, product scope, configuration, environment, time bounds, filters, authorized principal, compiler version)`; choice of hash format and exact constituent canonical IDs remain design tasks.
4. All omitted, redacted, unverified and unknown relationships have explicit completeness flags; do not synthesize a complete world from partial input.
5. A semantic `port` must target an interface entity or the known typed relationship of the owner; decorative ports never imply a real API/socket.
6. No agent or human can gain a new ability merely by being represented by the same glyph class. Source authorization remains separate.
7. Immutable fact lineage, baseline revisions and proposal history are carried through when supported; the global ledger research is not assumed implemented.

## Geometry-truth discriminant

- `physical`: real dimensions/source coordinate system, traceable to external design; allowed to claim scale.
- `measured`: positional or topology assertions with evidence and uncertainty.
- `semantic`: generated, testable visual grammar; units are presentational only.
- `illustrative`: aesthetic decoration; zero authority.

Adapters must label representations to users and assistive interfaces. Multiple projections may coexist and map to the same identity. Retained product/edge references outrank scene file paths.

## Conceptual schema / non-shipping example

~~~json
{
  "projection_kind": "assembly",
  "product_ref": "illustrative:product",
  "baseline": "illustrative:revision",
  "entities": [
    {"entity_ref": "illustrative:component", "kind": "component",
     "geometry_truth": "semantic", "source_evidence": [],
     "assertion_status": "unknown"}
  ],
  "relations": [],
  "completeness": {"partial": true, "reason": "example-only"}
}
~~~

The example deliberately denotes incomplete, *illustrative* state; it is neither a deployed route response nor a final schema. Full proposed request/response surface is in [spec 015](../specs/015-spatial-product-twin.md).
