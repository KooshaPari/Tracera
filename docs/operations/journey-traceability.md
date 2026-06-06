# Journey Traceability

Implements the [phenotype-infra journey-traceability standard](https://github.com/kooshapari/phenotype-infra/blob/main/docs/governance/journey-traceability-standard.md).

## Traceability Model

Every user-facing or agent-facing flow should be traceable across:

1. **FR/NFR** — requirement ID and user story from `docs/FUNCTIONAL_REQUIREMENTS.md`.
2. **Spec** — acceptance criteria, traceability invariant, and non-regression constraint.
3. **Docs** — operator/user documentation and rich media placeholders.
4. **Code** — backend handler, frontend view, graph service, MCP tool, or integration adapter implementing the flow.
5. **Tests/Gates** — unit, integration, BDD, lint, coverage, and journey verification acting as autograders.
6. **Evidence** — journey manifest, recording/keyframes, and evaluation verdict.

## User-Facing and Agent-Facing Flows

| Flow | Requirement | Implementation surface | Autograder gates | Evidence status |
| --- | --- | --- | --- | --- |
| Import requirements and create trace links | FR-DISC, FR-APP | import/parsing services, trace-link APIs, dashboard views | parser fixtures, API contract tests, BDD journey, eval verdict | Stubbed |
| Analyze coverage and impact across requirements/code/tests | FR-QUAL, FR-VERIF | graph service, coverage engine, impact analysis UI | graph fixture tests, coverage thresholds, journey manifest | Stubbed |
| Review traceability matrix and export report | FR-RPT | reporting APIs, dashboard matrix, export pipeline | report snapshot tests, export validation, screenshot journey | Stubbed |
| Collaborate on requirement status in real time | FR-COLLAB | realtime sync/webhooks, frontend state, backend events | websocket/webhook tests, state convergence checks, BDD journey | Stubbed |
| Agent/MCP analyzes a requirement and proposes trace updates | FR-AI, FR-MCP | MCP server tools/resources/prompts, automation services | MCP contract tests, tool fixture tests, eval verdict | Stubbed |
| Operator validates infrastructure health for traceability gates | FR-INFRA | database/auth/deployment/monitoring surfaces | health smoke, auth/config checks, workflow quality gates | Stubbed |

## Rich Media Stubs

<!-- RICH-MEDIA-STUB type="animated-gif" subject="Requirements import and trace link creation" journey="requirements-import-trace-link" status="TODO" -->
![Tracera requirements import — source document, parsed requirements, generated trace links, and validation state](../assets/rich-media/tracera/requirements-import-trace-link.gif)

*Expected capture: import a deterministic requirements fixture, show parsed requirement IDs, create or verify trace links to code/tests, and display validation feedback.*

<!-- RICH-MEDIA-STUB type="annotated-screenshot" subject="Coverage and impact analysis graph" journey="coverage-impact-analysis" status="TODO" -->
![Tracera coverage and impact graph — requirement, code, test, and deployment relationships](../assets/rich-media/tracera/coverage-impact-analysis.png)

*Expected capture: open an impact analysis view, annotate uncovered requirements, downstream code/test relationships, and the next action required for coverage closure.*

<!-- RICH-MEDIA-STUB type="annotated-screenshot" subject="Traceability matrix report export" journey="traceability-matrix-export" status="TODO" -->
![Tracera traceability matrix — requirement coverage, verification status, and export result](../assets/rich-media/tracera/traceability-matrix-export.png)

*Expected capture: generate a matrix/report from fixture data, verify exported rows match visible coverage state, and annotate failing or incomplete traces.*

<!-- RICH-MEDIA-STUB type="animated-gif" subject="Realtime collaboration status update" journey="realtime-requirement-status" status="TODO" -->
![Tracera realtime status — collaborator update, synchronized dashboard state, and event provenance](../assets/rich-media/tracera/realtime-requirement-status.gif)

*Expected capture: update a requirement status in one session, show synchronized state in another, and display event provenance or audit metadata.*

<!-- RICH-MEDIA-STUB type="journey-eval" subject="MCP trace update recommendation verdict" journey="mcp-trace-update-recommendation" status="TODO" -->
![Tracera MCP trace update verdict — requirement input, suggested links, confidence, and eval result](../assets/rich-media/tracera/mcp-trace-update-recommendation.png)

*Expected capture: invoke an MCP trace-analysis tool against fixture code/tests, verify suggested trace updates, and attach a pass/fail eval verdict for FR-AI and FR-MCP coverage.*

## Journey Manifests

Journey manifests should live in `docs/journeys/manifests/` and include:

- FR/NFR IDs or requirement category covered by the journey;
- fixture document, API endpoint, UI route, or MCP tool entrypoint used to reproduce the flow;
- deterministic seed data required for replay;
- expected screenshots/GIFs/keyframes;
- tests and gates that must pass before the journey is accepted;
- eval verdict schema and pass/fail criteria.

## Autograder Gates

Minimum gates before marking a journey complete:

- parser/import fixture tests for discovery flows;
- API/MCP contract tests for trace and automation flows;
- graph/coverage fixture tests for qualification and verification flows;
- report/export snapshot tests for analytics flows;
- BDD journey replay for user-visible traceability flows;
- realtime/webhook convergence tests for collaboration flows;
- doc link validation for every referenced rich media asset;
- journey manifest validation via `phenotype-journey verify` when available;
- eval verdict linked to the FR/NFR IDs in the manifest.

## Status

- [x] Identify initial FR-backed traceability flows
- [x] Stub rich media embeds for expected screenshots/GIFs/evals
- [ ] Author manifests in `docs/journeys/manifests/`
- [ ] Record journey captures for each flow
- [ ] Run `phenotype-journey verify` in CI
