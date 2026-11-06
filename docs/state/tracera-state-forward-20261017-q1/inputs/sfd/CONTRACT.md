# Docket contract

## 1. Three questions that must never collapse into one

**Implementation:** What has been built or changed? **Usability:** Which named beneficiary can complete which real journey on which artifact and environment? **Validation:** Has an actual person or intended consumer used it, and did the result help? A fourth view, assurance, establishes what evidence supports those statements. More code, tests, workflows, or reports do not automatically move all four.

The mature product contract comes first. CVP, MVP, beta, release, and other stages are scoped projections of it, not excuses to forget accepted intent. PhenoRegistry defines **CVP as Closest Viable Product**: the smallest living slice that preserves the product's identity and survives an end-to-end journey. Do not silently rename it. Internal tools need not invent market-validation ceremony, but still need a useful consumer outcome. [I02]

![Intent, implementation, usable outcome, and learning are different gates](assets/identity-to-learning.svg)

## 2. Field-level authority

| Meaning                     | Existing authority                                                     | Docket treatment                                                             |
| --------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Human intent and exclusions | Direct user requirements and their accepted amendments                 | Cite, date, preserve exact qualifications; record unresolved contradictions. |
| Repository boundary         | PhenoRegistry boundary/SSOT records                                    | Pin source; do not silently redraw ownership.                                |
| Accepted design             | Relevant accepted ADR/spec                                             | Distinguish accepted, proposed, superseded, and experimental.                |
| What the code does          | Pinned implementation plus appropriate execution evidence              | Docs and source presence are not runtime proof.                              |
| Product assessment          | Existing owner-held Assessment Dossier / Tracera records where present | Reuse identities and typed observations.                                     |
| Work and dependencies       | AgilePlus or the subject's established execution records               | Link tasks; do not create a competing task registry.                         |
| Reading projections         | Generated Markdown tables, HTML, and PDF                               | Rebuild from the same locked input set.                                      |

JSON is canonical for typed snapshot, observation, evidence, and event records in this reference profile. Markdown is canonical for authored explanations only where no stronger owner-held document already owns that meaning. Generated tables are not hand-maintained alternatives. YAML/JSONL may be exports, never a second independent truth. This follows the existing Master Assessment Kit rather than replacing its schemas. [I01]

## 3. Snapshot identity and evidence

Every snapshot identifies product, beneficiary/journey scope, repository IDs and full SHAs, dirty worktree state if accessible, deployed/installed artifact, environment, schema/template/evaluator versions, baseline membership and weights, observation start/end, generated time, previous snapshot, and limitations. Unknown values are explicit `null` with an explanation. Do not invent a local SHA from a remote head.

A material claim needs a stable claim ID, authority class, supporting and contrary sources, exact subject, method, result, observation time, freshness rule, raw evidence location or an explicit missing-evidence reason, and reviewer disposition. Evidence from different builds, fixtures, people, or environments must not be silently combined. One report's PDF and Markdown are one originating source, not two independent confirmations. A hash identifies bytes; it does not authenticate the author or prove a claim's semantics. [I01, W08]

Keep **applicability, execution, verdict, freshness, review, and acceptance** separate. `NOT_RUN`, `UNKNOWN`, `STALE`, `BLOCKED`, `FAIL`, and `NOT_APPLICABLE` are not interchangeable. An approved exclusion is not a pass. A waived gate remains waived. A passing fixture does not qualify a user's product.

## 4. Progress accounting

Define stable leaves and weights before scoring. Raw implementation progress may use explicit checkpoints; show checkpoint criteria and label it implementation, not verified satisfaction. Verified engineering and usable-journey credit require current admissible evidence and the required review. Do not score an unfinished journey as usable merely because most of its components exist.

For applicable weighted predicates, use P = current accepted pass weight, F = current fail weight, U = unknown/unexecuted/stale weight:

- **Assessed pass rate:** P / (P + F).
- **Assessment coverage:** (P + F) / (P + F + U).
- **Verified satisfaction:** P / (P + F + U).

A zero denominator is undefined, not 100%. Show unresolved applicability separately. Parent roll-ups use unique leaf membership; overlapping work cannot be counted twice. Never average unrelated repository percentages into product completion. Critical gates do not compensate across domains. A product can show engineering growth and still be blocked. [I01]

For delta bars show retained credit, newly earned credit, lost/stale credit, and remaining/unmeasured scope with labels or patterns, not color alone. Show the numerator, denominator, baseline ID, old/new value and percentage-point difference. On a scope change, report the old-scope delta and a separate denominator restatement; refuse an unqualified like-for-like delta.

Illustrative examples may show **hypothetical** scores. Their operational credit is always absent. Do not import illustrative PASS values as observations. A structural validator is not the assessment reducer or an independent semantic reviewer.

## 5. High-velocity continuity

Snapshot boundaries are event-driven; hourly/daily are reading windows. Capture gate changes, releases, new usable journeys, regressions, scope changes, and decisions without waiting for a daily report. The first report establishes the full baseline. Later short reports print changed projects/branches only, including negative changes and lost freshness. A daily full reading edition consolidates events without adding the same gain twice.

Record both observation time and ingestion time. Bind freshness to change impact, not just elapsed age. A code/config/data change invalidates dependent evidence; unrelated documentation does not automatically erase all test credit. A safety-critical decision requires evidence valid at execution time. A failed collection is `NO_OBSERVATION`, not `NO_CHANGE`.

Use append-only observations and immutable snapshots; update only a small current-snapshot pointer with an expected previous value. Deduplicate exact event IDs; reject the same ID with different content. Reconcile a moved branch before publishing. Do not overwrite concurrent work or force-push to make receipts look clean. This file set does not implement a distributed lease or global transaction service.

## 6. Completion and authority boundaries

Declare completion only for a named, versioned scope with accepted gates, current proof, usable delivery, accurate docs, and no hidden in-scope stubs. Record authorized exclusions for scaling, sunset, or unresolved user learning; do not use them as blanket debt buckets. A fresh project should reach a safe identity-preserving usable slice promptly, then obtain real feedback. Feedback-dependent product choices can wait while independent hardening proceeds.

A report cannot authorize deletion, external sharing, deployment, billing, permission escalation, security-gate removal, or a new recurring schedule. A blocker applies to the actions it actually prevents, not the entire project. Never invent subagent execution, Safari opening, CI success, user approval, or publication receipts.
