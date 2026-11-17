# Master Assessment Kit — contract 1.1

## 1. Decision: a file set with one readable front door

The reusable master is the **Master Assessment Kit**. Each completed scope/baseline is an **Assessment Dossier**. `ASSESSMENT.md` and `ASSESSMENT.html` are generated front doors, not the only storage of truth. “Audit” remains a valid user command; the persisted object is broader than a checklist or numerical scorecard.

Use one logical dossier for a scoped assignment/assessment snapshot. A product spanning several repositories has a pinned component bill of materials, not an average of independent repo grades. One repo may have several dossiers for different beneficiary slices or deployments.

## 2. Minimum useful file set

```text
<owner-audit-path>/<assessment-id>/
  dossier.json                  # context, inventory, scope interpretation, linked findings/decisions
  subject.json                  # source/BOM descriptor; real digests, or explicit unavailable values
  assignment.json               # pinned scope, profile, criterion instances, gates, epoch
  assessment.json               # exact result/evidence/qualification indexes and identity locks
  measurement-bindings/*.json   # how each activated predicate is measured
  results/*.json                # immutable observations / verdicts / validity / review state
  evidence/*.json               # references and digests, not a substitute for raw evidence
  qualifications/*.json         # actual instrument controls, only when available
  findings/*.json               # defects, uncertainty, undeclared obligations, research gaps
  decisions/*.json              # separate authority, rationale, alternatives and stop conditions
  raw/*                        # authorized local evidence or portable references
  outbox/*.json                 # optional intended delivery; no fake registry receipt
  ASSESSMENT.md                 # generated report
  ASSESSMENT.html               # generated offline report
  views/assessment.json         # normalized generated view for agents/search
  views/assessment.yaml         # generated readable machine view, not a second authority
  views/records.jsonl           # generated streaming export of canonical JSON records
  views/build.json              # input and output hashes plus renderer/reducer/schema identities
```

Existing audit layouts may implement these roles under other names. Do not duplicate canonical product state merely to mirror a folder diagram. Add separate intent, mandate, genesis, leases, work items, checkpoints and amendment records from the retained core where their owner/scope requires them. The small examples keep some context in `dossier.json`; this is a snapshot context supplement, not a new portfolio registry.

## 3. Master sources versus dossier instances

The core catalog defines criterion predicates and source mappings. Profiles select candidate obligations. Schemas constrain record shapes. Measurement bindings connect a criterion instance to a real scope, method, fixtures, limits, controls and freshness rule.

A dossier instantiates only the applicable selected obligations and records coverage of the unselected frontier. Not selected means unassessed, not not-applicable. An approved exclusion needs a scope reason; unresolved applicability remains visible.

Do not create an independent manually edited copy of the 1,080-entry catalog inside every repo. Pin its version/digest and retain the subset or a resolvable reference needed for a self-contained export. The renderer may display repeated predicate text, but the definition remains source-controlled.

## 4. Human report contract

A complete report exposes, in this order:

1. Scope/evidence-class banner, exact subject, assignment epoch, source coverage and limits.
2. Decision brief: current scoped stage, next action, stop rule, and why it matters.
3. Evidence coverage and critical gates, with unknown and unresolved denominators explicit.
4. Intent, authority, authorship, beneficiary, assumptions, non-goals, alternatives and genesis rationale.
5. Inventory linking declared, implemented/observed, exercised and beneficial views.
6. Filled criterion rows with applicability, execution, verdict, review, freshness, evidence, and next action.
7. Findings and bounded decisions, with owner, action class, dependencies/wakeup and reversibility.
8. Maturity/viability by slice and axis, not one universal percent-complete.
9. Semantic review with supporting evidence, contrary explanations and a discriminating experiment.
10. Delta attribution and restart packet: what changed, what failed, what remains authorized.
11. Evidence index, machine views, build receipt and integrity limits.

The summary is allowed to be brief; the dossier must remain drillable. Do not hide the only failure or unknown inside a collapsed detail while presenting a global green banner.

## 5. Stable result semantics

Keep applicability (`APPLICABLE`, `NOT_APPLICABLE`, `UNRESOLVED`), execution, verdict, evidence freshness and review disposition independent. Passing a linter is different from passing a real consumer journey. A document exists, an accepted requirement exists, a test exercised the behavior, and the behavior helped a consumer are separate claims.

All fractions have explicit scope. With current admissible pass/fail/unknown weights P/F/U, report assessed pass rate P/(P+F), assessment coverage (P+F)/(P+F+U), and verified satisfaction P/(P+F+U). Undefined denominators are null, never 100%. Unresolved applicability remains separate and blocks dependent promotion. A waiver never becomes a pass.

Critical gates do not compensate across domains. Preserve accepted assurance floors and bind their actual denominators. A small library does not require cloud infrastructure just to earn points; a CLI handling private data still requires appropriate privacy and integrity assurance.

## 6. Illustrative versus executed versus operational

`EXAMPLE` is a record class, not operational acceptance. `EXECUTED_FIXTURE` means this specific bundled synthetic fixture actually ran; it does not establish a user's product. `ILLUSTRATIVE_SCENARIO` means even the product outcomes are authored premises.

For illustrative scenarios this layer enforces PROPOSED results and no qualification records. The hypothetical summary is explicitly named and separated from the real reducer. Importers must not turn its displayed PASS into product acceptance.

Real assessments use actual subject identities, operational records, qualified methods, appropriate evidence and authority. No command in this kit upgrades an example to a real assessment automatically.

## 7. File choices and authority

**Default:** JSON records for exchange and deterministic validation; YAML for human authoring at the intake boundary or generated exports; JSONL for streaming exports; Markdown for review and Git diffs; HTML for navigation and presentation.

This delivered layer implements JSON input and generated YAML output. It does not implement an arbitrary YAML-to-operational-record compiler. A future authoring adapter must parse safely, reject duplicate keys and unsupported tags, resolve values explicitly, and compile into a locked JSON snapshot. Editing YAML and JSON independently is prohibited.

Do not hash a rendered report as a proxy for all inputs. Pin the source/BOM, assignment, criterion/evaluator versions, evidence bytes, and the render input/output set. IDs identify logical objects; digests identify exact content or a documented normalized value. Both are useful.

## 8. Extensions and versioning

Core 1.0 contracts remain intact. Dossier context is an additive 1.1 schema. Unknown required meanings must not be silently ignored. Large media, private data, attestations, regulator-specific exports, specialized tests and registry adapters are optional extensions selected by actual capability and risk.

Do not require all optional pieces before a safe first useful loop. A missing hosted credential blocks that action; a missing registry blocks delivery of its receipt, not local evaluation. New integration work must justify its cost with an observed blocker.

## 9. Robustness boundary

The delivered tool checks selected record shapes and cross-references, the exact input set, subject descriptors, core evidence reductions, generated view equality and manifest bytes. It does not independently authenticate authors, verify real-world observations, prove that a mandate is genuine, make a semantic judgment true, enforce a multi-host lease, sign records, or decide whether an investment is worthwhile.

Hashes are integrity instruments. Stronger producer identity needs an actual trusted signing and verification path. Correctly signed nonsense is still nonsense. See [format and integrity](docs/FORMAT-AND-INTEGRITY.md).
