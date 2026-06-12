# SOTA Wrap Research: Traceability Ecosystem

Date: 2026-06-11
Repo: Tracera
Scope: StrictDoc, Kuzu, OpenFastTrace, Graphiti, Doorstop, BASIL, Joern

Note: Network access was unavailable in this run; license and architecture notes are based on current package/project knowledge and should be rechecked against upstream before vendoring or redistribution.

| Tool | Summary | License | Wrap/use | Why / why not | Integration effort |
| --- | --- | --- | --- | --- | --- |
| StrictDoc | Requirements authoring and documentation system with traceability, SDoc format, HTML export, and growing requirements-management features. Python core with JS frontend pieces. | Apache-2.0 | Wrap import/export for SDoc and generated trace links; optionally invoke CLI for document transforms. | Strong fit for requirements-first workflows and permissive license; avoid deep UI coupling initially. | Medium |
| Kuzu | Embedded graph database optimized for property-graph workloads, implemented in C++ with language bindings. | MIT | Use as an optional local trace graph backend for requirements, code, tests, and evidence edges. | Best immediate fit for Tracera's multi-view trace graph; low license risk and deploys embedded. | Medium |
| OpenFastTrace | Traceability checker that links requirements to specs, code, tests, and docs using marker conventions. Java implementation. | MIT | Wrap CLI as an evidence extractor/checker for trace coverage reports. | Useful validation engine with permissive license; Java runtime and marker conventions make it a better adapter than core dependency. | Low-Medium |
| Graphiti | Temporal knowledge graph framework for continuously updated entity/relation memory over time. | Apache-2.0 | Defer; study temporal modeling ideas and possibly wrap for change-history KG experiments. | Conceptually aligned with evolving project knowledge, but likely broader than first traceability needs. | Medium-High |
| Doorstop | Lightweight requirements-management tool with document/item hierarchy, links, and verification workflows. | MIT | Wrap import/export for Doorstop item trees and link validation. | Practical bridge for teams already using text-based requirements; overlap with StrictDoc means do after one primary requirements adapter. | Low-Medium |
| BASIL | Web-based requirements/test-management and traceability platform. | GPL | Do not embed or link into product code; consider one-way import/export only if demanded. | GPL creates product-distribution risk; useful comparison point, not a near-term dependency. | High |
| Joern | Code Property Graph platform for code analysis, security queries, and semantic code exploration. | Apache-2.0 | Defer; wrap CLI/server for code-to-requirement evidence extraction after core graph model stabilizes. | Powerful for code intelligence but heavier than needed for initial traceability graph and requires language/query operational work. | High |

## Top Recommendation

Wrap now:

1. Kuzu: make it the optional embedded graph substrate for trace objects and relationships. It directly supports Tracera's graph-shaped core and keeps deployment simple.
2. StrictDoc: add SDoc import/export and CLI-based trace extraction to cover requirements authoring without owning a full requirements editor immediately.

Defer:

1. Joern: valuable later for semantic code evidence, but too heavy before the core trace schema and graph APIs are stable.
2. Graphiti or Doorstop: choose Graphiti later if temporal KG/history becomes central; choose Doorstop later if user migration/import from lightweight requirements repos is requested.

Avoid embedding:

- BASIL, because GPL licensing makes it unsuitable as a product dependency. Keep it as a comparative reference or external import target only.
