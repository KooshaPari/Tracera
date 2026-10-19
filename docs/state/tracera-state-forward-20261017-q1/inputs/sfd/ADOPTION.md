# Adoption and operating procedure

## Before copying anything

Identify the real product, all relevant repositories, local instruments, aliases, and existing owner-held audit/intent/spec/task paths. Pin their revisions. Read applicable repository instructions. Reuse existing Master Assessment Kit and program-docset records. Map roles instead of creating duplicate schemas, task boards, or registries.

A suggested instance path is `docs/state/<snapshot-id>/`; use the subject's established equivalent when one exists. The registry owns this template distribution and portfolio pointers, not a second mutable copy of every product's live state. The product repository owns its Markdown docket and local evidence references. A cross-repository publication receipt binds both to the same snapshot ID.

## A useful first pass

Start with the cockpit, mature intent, present usability, critical gates, unfinished inventory, and next executable slice. Expand the rest in parallel with implementation. Do not spend the entire run producing governance artifacts while leaving the first real journey broken. A 100-page PDF is justified only when its drill-down supports actual decisions; the first two pages must still be useful in two minutes.

### Audit lanes

| Lane                                  | Substantive assignment                                                                                     | Required output                                                           |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Intent and archaeology                | Current user intent, accepted historical horizons, aliases, supersession, boundaries                       | Source-bound goal tree and conflict register.                             |
| Implementation and integration        | Actual code paths, dormant branches, stubs without markers, data contracts, deployed-vs-source differences | Capability map and precise unfinished leaves.                             |
| User experience and documentation     | Fresh-start journey, errors, recovery, accessibility, CLI/API/SDK ergonomics                               | Reproduction script, observed failure points, proof artifacts.            |
| Assurance and operations              | Security/privacy, integrity, negative cases, recovery, performance, CI and distribution                    | Gate-by-gate evidence and missing controls.                               |
| Research and alternatives             | Discovery breadth, primary-source depth, relevant existing ecosystem and alternatives                      | Candidate ledger, comparison, and discriminating pilot.                   |
| Independent challenge and integration | Reproduce load-bearing claims; test rival explanations; reconcile estimates and merge races                | Dispositions, counterexamples, critical path, honest publication receipt. |

Use real subagents only when the environment supports them. Record their actual IDs, scope, baseline, work, and review. Otherwise run explicitly labeled serial passes. A second wording pass by the author is not independent verification. Parallelize independent work with non-overlapping write ownership; serialize shared-file integration and final qualification.

## Hourly and daily behavior

**During execution:** record meaningful events and evidence as they occur. **At an hourly checkpoint:** reconcile source drift, affected gates, task state, and the next 30/60/240-minute outcomes; publish a short delta when something meaningful changed. **At a daily checkpoint:** consolidate the event stream into a full coherent docket, re-evaluate critical gates, revisit estimates, and preserve the previous snapshot. These are operating recommendations, not a claim that an automation has been installed.

Do not inflate report output during a quiet window. Record a collection heartbeat separately from a user-facing delta. A regression, stale proof, new decision, or scope change counts as a reportable change even without a commit. An inaccessible source is a coverage change, not evidence that nothing happened. Avoid overlapping polling jobs and multiply-counted event windows.

## Forecasting at this velocity

Use accepted outcome throughput, recent cycle times, review queues, contention, flaky reruns, and actual tool limits. The user's history establishes high activity, not a calibrated conversion rate from agents or commits to usable output. Record calibration sample size, window, work class, and outcome definition. With no comparable sample, label ranges as expert estimates, not P50/P90 forecasts.

Separate total agent effort, constrained parallel wall-clock time, human review effort, external waiting, integration/rework, and validation. A critical-path calculation without resource limits is a lower bound. Never divide total effort by nominal agent count. Show 30 minutes, 1 hour, 4 hours, and 24 hours as explicit outcome windows; do not promise a horizon whose inputs are still unknown.

## Publication protocol

1. Freeze and validate the source input set. Generate matching MD tables, HTML, PDFs, figures, and a manifest. Inspect rendered pages, not just extraction.
2. Commit the subject's MD docset to its authorized branch. Record full SHA, branch, PR and merge state. Re-read the remote head.
3. Commit the registry pointer/template changes independently. Verify the destination actually contains the artifacts claimed. A local file, opened PR, or intended outbox record is not a completed remote push.
4. Record partial publication explicitly and retry only within authority. Do not delete or rewrite original reports just because a new dossier identifies mistakes; append correction/supersession records.
5. Open the resulting PDF in Safari only through a real authorized macOS capability. Otherwise deliver it and record `NOT_OPENED`; do not claim a browser tab was opened.

An authorized macOS agent can run `open -a Safari /absolute/path/to/report.pdf`. `python tools/open_safari.py reports/SFD-COMPLETE.pdf` checks that it is on macOS and that the file exists. Linux rendering is not Safari verification.

## Acceptance of the template system itself

A local build and reference tests establish package behavior only. Operational adoption still needs one real subject adapter, source/evidence bindings, an exercised publication path, and independent semantic review. Leave AgilePlus spec IDs unresolved until actually created through its established workflow; a GitHub issue or Markdown filename is not silently an AgilePlus spec receipt.
