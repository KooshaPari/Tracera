# Tracera engineering and agent delivery playbook

Status: proposed working practice, 2026-11-02. This document guides execution; it is not evidence that any listed gate, service or product capability has passed. Actual user instructions, repository rules and existing accepted decisions take precedence. Confirm the exact source revision before each work package.

## Purpose and authority

Tracera contains product-graph, API, interface, and evidence components. Before expanding them, verify the current product contract and the boundaries between linked systems using the applicable repository decisions and the work package's recorded source of authority. A work item marked done is not itself proof that product acceptance passed.

Use an independently verifiable vertical slice before declaring broad feature parity. A proposed graph acceptance slice creates or imports a project and canonical items, establishes project-scoped links, searches and traverses them, restarts against the same data, compares stable IDs and relationships, and checks the same truth through an unmocked UI. Whether the slice is accepted must be established by a revision-specific receipt. Do not substitute SWEE graph nodes or an artifact trace-link table for canonical item links without an explicit model decision and migration evidence.

## Existing assets and authority hygiene

- Use `CONTRIBUTING.md` for setup, branch and endpoint-governance expectations. It calls for a focused PR, CI and changes to `docs/governance/policy/endpoint_traceability_map.md` and `coverage_matrix_self_application.md` for endpoint changes. Check actual workflow definitions and results; documentation alone is not CI evidence.
- `docs/FEATURE_INVENTORY.md` is a historical migration oracle for the removed Python implementation. Do not treat labels such as CURRENT or legacy behavior as evidence of present Rust capabilities, security or product acceptance.
- `docs/governance/ADR-TEST-001-test-coverage-policy.md` calls itself Accepted and describes a public-function coverage policy; `ADR-TEST-002-mutation-testing.md` is Proposed. Inspect applicability and actual enforcement, avoid reporting either as enforced merely because a document says so. Do not silently override an applicable accepted policy. Confirm owner and intended supersession if a decision conflicts with practical evidence.
- `docs/specs/010-full-e2e-contract-coverage.md` is Draft. Its counts and scope are design-era statements; derive current endpoint and contract denominators from mounted routes, schemas, consumers and revision-specific test discovery. Existing FR-to-endpoint-to-test map is a starting point, not proof of exhaustive coverage.
- Reference the existing ADR index, specs, matrices and migration inventory rather than creating a second conflicting authority. Reconcile disagreements by date, author, scope, revision and explicit acceptance; record unresolved contradictions as such.

## Work package: ready before implementation

One small, complete vertical outcome has a single owner, an independent reviewer, and a durable work identifier. Record:

1. User intent and exact source or decision; relevant existing requirement/spec/ADR IDs and a baseline SHA. Explicitly label inferred requirements and unresolved decisions.
2. Trigger, desired observable result, non-goals, affected users, API/UI/data migrations, dependencies, risks and rollback. Identify who owns the product model versus execution and external integrations.
3. Concrete acceptance examples covering success, authorization, failure, empty/partial data, persistence and isolation where relevant. Include source of truth, boundaries and data ownership. Identify an independent oracle and real provider, rather than only a mock.
4. Design: current behavior and options; contracts and invariants; migration/compatibility plan; ADR for an architecturally significant change. For stored graph links specify project-scoped identities, endpoints, direction, type, lifecycle, atomicity and revision semantics; do not infer these from a similarly named table.
5. Verification plan: behavior scenarios; smallest useful regression test first when feasible; provider and consumer contract verification for changed boundaries; storage, security and end-to-end tests where applicable; exact commands, environment, preconditions and expected failures. State missing tools or credentials as a blocker, not an exception that turns an unrun test green.
6. A task boundary: allowed files or isolated worktree, branch base, interface owner, no shared mutable files with another worker, no secrets in logs or issue text; time/space limits and escalation conditions. Reserve an independent review pass and integration time.

For a one-line copy fix or similar low-risk change, a linked issue plus a direct review and proportionate verification is sufficient. Do not manufacture a separate spec, BDD harness or tests that only restate the implementation. For persistent data, auth, contract or graph changes, this minimum process expands with risk.

## Execute: spec, examples, tests, code, review

1. **Discover and model.** Read current code, historic implementation, product sources, existing specs and open PRs. Identify real user workflow, domain entities and invariants; avoid creating a competing model. Source presence, route mounting and runtime behavior are distinct observations.
2. **Specification-driven work.** Use the existing spec location/ID where possible. Keep requirement, decision, interface, invariant and concrete example linked; a proposed document is not an accepted product decision. Use ADRs for significant tradeoffs and reversibility, not every implementation detail.
3. **BDD / specification by example.** Collaboratively describe the observable behavior in concrete Given/When/Then examples. Automate risk-relevant examples through the product boundary. Gherkin is optional; the essential output is a shared example and an executable oracle. Do not let a mock scenario count as an unmocked acceptance journey.
4. **TDD and regression.** Start from the observable defect or boundary condition and write a test that fails for the intended reason where the execution environment allows it. Capture red, implement the minimum, demonstrate green, then refactor and rerun. If a test cannot run, mark both the check and the implementation unverified; do not label a test file a passing test. Use table/property and fuzz tests for combinatorial parsing, identity and security boundaries when they add meaningful coverage.
5. **Contract-driven work (CDD).** Specify requests, response envelopes, errors, auth/CSRF, status variants, paging/completeness, idempotency and evolution. Exercise consumer expectations against a real provider or provider verifier at a pinned compatible revision. Consumer mocks are useful but cannot establish provider compatibility. Pact is an option, not a new mandatory infrastructure dependency. If CDD means component-driven development for a UI task, apply component isolation, accessibility and interaction states separately; neither meaning replaces product behavior.
6. **Domain, data, and security.** Treat item graph identity and transaction boundaries as domain invariants. For a write path inspect the trust boundary and failure modes: missing/wrong credentials, cross-project access, CSRF/origin, malformed input, duplicate requests, concurrent retries, partial writes, revocation, restart and upgrade. Distinguish authentication from project authorization; a shared bearer is not proof of per-project access. Threat model early, update when design changes and record open residual risks.
7. **Engineering review.** A different agent or person reviews the actual diff and tests against requirements, contracts, authorization, data loss, concurrency, UI accessibility and false-success paths. Reviewer independence is an internal process objective, not evidence of human approval. A human review or approval is only claimed when a real authorized person performed it. Send unresolved concerns back to the implementer; do not auto-merge an unverified result.
8. **Integration.** Integrator rebases/cherry-picks intentionally onto a known base, resolves overlaps, verifies generated files and current contracts, and reruns affected checks on the integrated tree. Preserve separate unsupported drafts. Never equate a path-filtered or skipped GitHub check with an executed test. Do not force push, modify production, publish, or deploy without the applicable user scope and platform conditions.

### Worked acceptance slice: canonical item graph

The following are intended examples, not statements that current Tracera supports them:

```gherkin
Scenario: Product graph survives a restart
  Given an authorized actor and an isolated file-backed project A
  And canonical items X and Y with a directed typed relationship X -> Y
  When the server is restarted against the same data
  Then authorized reads and traversal return the same project, item IDs, edge type and direction
  And the real UI shows that relationship from the same server revision

Scenario: A project boundary cannot be crossed
  Given item X belongs to project A and item Z belongs to project B
  When an actor attempts to link X to Z within A
  Then the request is rejected and neither project's graph changes
```

Add separate tests for unconfigured auth, missing/wrong token, CSRF, duplicate and concurrent idempotency keys, request conflict, interrupted transaction, missing data, page limits, SQLite and PostgreSQL, graph revisions, restore, and no false-success UI. A source-code test or mocked browser route does not prove these scenarios. Execute against a disposable server/data store and capture the exact revisions and results.

## Agent swarm operating protocol

The coordinator owns priority, scope, allocation, integration and final claim; workers own bounded slices. Before fanning out, maintain a task ledger (issue or existing work package, not a parallel authority) with `id`, objective, requirement IDs, baseline SHA, allowed files/worktree, dependencies, risk, owner, verifier, test plan and current status. Assign independent work only where shared interfaces are agreed; serialize competing edits. A reviewer must receive the diff, requirement, expected behavior and evidence—not just the implementer's summary. A reviewer can invalidate a result without assuming an alternative is correct.

Every worker returns a receipt: actual head/tree, paths changed, hypothesis, commands and outcomes, test discovery and pass/fail/skip counts, fixture vs real dependencies, evidence links, open risks and exactly what was not checked. Integrator confirms commits survive the execution environment before ending the session. Scratch storage can disappear: do not claim an unpushed local commit is durable or available in GitHub. Use only an authorized persistence route; avoid publishing sensitive or unfinished branches just to trigger CI.

Use a common state vocabulary with evidence:

| State | Meaning |
| --- | --- |
| Proposed | Intent or design collected, not accepted |
| Source observed | Code/docs exist at a named SHA; no behavior implied |
| Implemented | Diff exists on a named, retrievable revision; correctness not implied |
| Verified | Named checks ran against that revision, with limitations and failures |
| Integrated | Compatible work combined and relevant checks rerun on the combined tree |
| Accepted | Named independent product journey and its acceptance criteria passed in the stated environment |
| Blocked | Required dependency, evidence or permission is unavailable; name impact and next action |

Implementation, verification, integration, acceptance and release are separate transitions. Failed or skipped checks, unsupported feature flags and mocked inputs remain visible. Do not use a green aggregate check as proof all jobs ran, nor claim percentages without explicit numerator, denominator, time and methodology.

## Evidence and release gates

For each actual run record: repository/ref/commit and tree, exact command or run URL, tool/runtime versions, service configuration and schema revision, DB type and migration state, fixture/mocks vs real services, environment, start time, test selection/discovery count, passed/failed/skipped results, logs and screenshots where relevant, and reviewer conclusions. Keep secrets and personal data out. Preserve enough state to reproduce without treating an ephemeral local path as a durable artifact.

Minimum gate by change risk:

| Change | Required evidence |
| --- | --- |
| Text or reversible local formatting | Diff review and appropriate rendering/lint where applicable |
| UI or domain behavior | Meaningful regression cases; typecheck; explicit loading, empty, partial and failure states; independent review |
| Consumer/provider boundary | Actual request/response and errors, consumer expectations verified against provider, auth/CSRF, pagination and version compatibility |
| Persistent or security-sensitive change | Plus threat/authorization review, real DB integration, cross-project isolation, transaction/idempotency, restart/migration/restore tests, supported backends identified |
| Product acceptance | Unmocked end-to-end journey with pinned UI/server/data revisions and explicit independently checked acceptance cases |
| Release/deploy | Above required checks on exact head, review, build and artifact provenance, deployment target/authorization, migration and rollback plan, post-deploy smoke and observation |

This table describes risk-tailored expectations; it does not override repository policy or user instructions. A check blocked by missing Rust, database, browser, CI identity or authorization remains blocked, not waived. Identify the responsible owner and next concrete path to unblock it.

## Research references

- [Cucumber: Behaviour-Driven Development](https://cucumber.io/docs/bdd/) and [writing better Gherkin](https://cucumber.io/docs/bdd/better-gherkin/): concrete collaborative examples and behavior-focused scenarios.
- [Pact provider verification](https://docs.pact.io/getting_started/provider_verification) and [consumer testing guidance](https://docs.pact.io/consumer): consumer expectations require provider verification; contract tests are not a substitute for provider functional and product acceptance tests.
- [NIST SP 800-218 SSDF 1.1](https://csrc.nist.gov/pubs/sp/800/218/final) and [NIST IR 8397](https://csrc.nist.gov/pubs/ir/8397/final): integrate secure development and multiple verification techniques throughout the lifecycle.
- [OWASP threat modeling cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html): model the system, identify threats, decide mitigation, and verify the results iteratively.
- [Architecture decision record templates](https://adr.github.io/adr-templates/): record context, options, decision, status and consequences for material tradeoffs.
- [SLSA build-track basics](https://slsa.dev/spec/v1.2/build-track-basics): source and build provenance help establish what artifact was built and with what process; a provenance claim itself requires verification.
- [GitHub protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches): a status can be successful, skipped or neutral for branch protection; inspect execution evidence before treating a required check as proof.
