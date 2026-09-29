# Tracera Autograder Contract

**Test generation status:** DEFERRED.  
**Verification specification status:** REQUIRED NOW.

The autograder grades the accepted product contract, not test counts.

## Required inputs

- contract baseline/revision;
- selected VP stage;
- canonical FR/AC identities;
- feature/journey topology and completion rules;
- implementation/test/evidence trace links;
- exact candidate artifact/source revision;
- target environment/configuration;
- verifier identity/version;
- observation timestamp/freshness policy;
- scope amendments since prior baseline.

## Behavioral states

`not_started | implementing | implemented_unverified | partially_verified | verified | failed | stale | unknown | inconclusive | blocked | not_applicable`

Trace completeness is a separate dimension.

## False-green prohibitions

The grader MUST NOT return verified solely because:
- no tests were selected;
- a required collector failed;
- evidence is missing;
- a check was skipped or neutral;
- a test passed for another product/component/baseline;
- evidence is stale beyond its declared policy;
- a mock passed while the mocked integration is the requirement;
- the same change weakened/removes its acceptance rule without independent approval;
- a parent is marked complete while required descendants remain open;
- a work item was closed externally;
- a stage denominator is empty.

## Stage grading

For selected stage S:
1. project canonical FRs by applicability;
2. evaluate each required FR from admissible evidence;
3. aggregate feature state using declared completion rules;
4. evaluate required journeys;
5. apply essential blockers;
6. separately calculate trace completeness;
7. derive structural shape and stage readiness;
8. report scope delta separately from engineering delta.

Unknown/stale/inconclusive/failed required FRs remain in the denominator and receive no verified credit.

## Product-shape output

Every grade should be able to emit:
- mature-contract completeness;
- selected-stage completeness/readiness;
- highest achieved stage;
- structural shape;
- feature closure;
- journey closure;
- core/supporting/enabling breakdown;
- implementation survivability;
- mature-contract compatibility;
- transition burden;
- blocker list.

## Deferred test-generation contract

Each FR in `spec/product/mature-contract.v1.json` already carries:
- acceptance IDs;
- positive oracle;
- negative/adversarial oracle;
- expected test levels;
- future positive/negative test IDs.

The later test-generation pass MUST replace placeholders with concrete assertions/fixtures and trace them back to these IDs. It MUST NOT rediscover or redefine expected behavior ad hoc.

## Independence

Implementation and acceptance policy may evolve through explicit separate revisions. An implementation change cannot silently weaken the policy used to grade itself.
