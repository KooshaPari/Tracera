# Tracera autograder design — not implementation proof

**Specification and test-generation readiness: incomplete. Concrete test generation remains deferred by the user.**

The prior claim that generic positive/negative sentences plus reserved IDs fully specified tests is withdrawn. `spec/product/mature-contract.v1.json` is invalidated and MUST NOT supply an accepted denominator. A consumer must reject `grading_eligible: false`, an invalidated baseline, unresolved mandatory projection, or empty mandatory expectation set; it must not produce a passing grade.

## Required eventual semantics

Grade exact requirement/criterion revisions against attributable candidate, target, fixture and verifier evidence. Keep behavioral result, trace completeness, work state and product acceptance distinct. Derive stages from reviewed requirement/dependency/feature/journey topology. Parent rollups cannot duplicate leaf credit. Missing, skipped, stale, contradictory, wrong-subject or unauthenticated required evidence cannot earn a pass.

Autograder specification must define status precedence, conflicts, invalidation, zero-denominator behavior, expected-check reconciliation, retry/quarantine semantics, approved exceptions and separation of acceptance-policy changes from the implementation under assessment. No product stage, compatibility claim or test-readiness claim may follow from catalogue size.

For every testable obligation define concrete stimulus, preconditions, observable expected result, relevant negative controls, fixture and environment, reset/isolation, assertions and evidence retention. Existing tests must be assessed for what they actually establish. Mock success is not proof of the mocked production boundary.

Current runtime behavior has not been re-tested in this correction. This document states required semantics, not that the application already implements them. Apply `governance/COUNT_INDEPENDENT_SPECIFICATION.md` when completing the source-backed design.
