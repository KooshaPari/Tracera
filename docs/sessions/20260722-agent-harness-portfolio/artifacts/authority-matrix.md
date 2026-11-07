# Agent and harness portfolio authority matrix

**Audit date:** 2026-07-22 (local checkout inspection only)

This matrix records the authority boundary used for the portfolio audit. A
missing checkout is intentionally recorded as a blocker; it is not inferred
from a similarly named directory or an archived tree.

| Lane | Repository path | Remote | Branch / HEAD | Role | Source-of-truth status | Dependency edges | Blockers |
|---|---|---|---|---|---|---|---|
| HeliosLab | `AgilePlus/HeliosLab/` (empty placeholder); containing repo `AgilePlus/` | `git@github.com:KooshaPari/AgilePlus.git` | `main` / `01083249af606dd9842be6070507a58109620c3e` | Helios app/lab and shared tooling surface | **Not a standalone checkout.** Only the AgilePlus placeholder is present; no HeliosLab worktree or independent remote was found locally. | AgilePlus architecture groups HeliosLab with `helios-cli/` and `heliosApp/`. | Restore or explicitly designate the canonical HeliosLab checkout before build/CI claims. |
| HeliosCLI | `helios-cli/` | `git@github.com:KooshaPari/helios-cli.git` | `main` / `8f223cfb0cdb154f46e58e01f144b5554d3be155` | Executable CLI, harness and agent-facing command surface | **Canonical local checkout observed; clean.** | `harness/` is in-tree; audit docs reference Agentora and HeliosLab integration points. | No local blocker observed; CI/build status still requires an explicit run. |
| HeliosLite | **Not found under `repos/`** | No local remote metadata | No branch / HEAD | Lightweight Helios runtime lane | **Absent locally; authority unresolved.** | Expected to consume the HeliosCLI/runtime contract once a canonical checkout is identified. | Identify the owned repository/remote and restore a checkout. |
| Agentora | **Not found under `repos/`** (referenced by AgilePlus plans) | No local remote metadata | No branch / HEAD | Agent orchestration and multi-agent coordination | **Absent locally; authority unresolved.** | AgilePlus agent-framework plan lists Agentora as the orchestration owner; HeliosCLI audit docs reference it. | Restore the canonical Agentora checkout and record its remote/branch before integration work. |
| Tracera | `Tracera/` | `git@github.com:KooshaPari/Tracera.git` | `feat/web-services-refactor-2026-07-18` / `5002bf0fcda1052745ff8472fcafb3f55028e4f9` | Traceability, observability, compliance and dashboard evidence | **Canonical local checkout observed; clean.** This artifact is stored here as the portfolio ledger. | Consumes runtime/evaluation events; pairs with pheno-harness and phenotype-omlx evidence lanes. | Branch is feature-named, not `main`; promotion/merge gate remains open. |
| MLX | `phenotype-omlx/` | `git@github.com:KooshaPari/phenotype-omlx.git` | `feat/cross-repo-audit-wave2` / `f34ca8cb9d7c18fd884438f63baf55b6d2b29494` | MLX model/runtime implementation and eval ingestion | **Canonical repository checkout observed; dirty.** Local edits are pre-existing and were not changed by this audit. | Consumes `pheno-harness` evaluation contracts; persistent-runtime implementation lives under `perf-core/model-plan/`. | Feature branch and dirty tree; do not treat as releasable until reconciled and green. |
| Harness | `pheno-harness/` | `git@github.com:KooshaPari/pheno-harness.git` | `main` / `118bcd7113f536df304c1aa91141464661c997a4` | Benchmark, verifier and evaluation harness | **Canonical local checkout observed; dirty/untracked audit artifacts present.** | Produces the interchange contract consumed by phenotype-omlx; Agentora remains a separate competitive lane. | Untracked benchmark/docs artifacts and no clean release snapshot. |
| Persistent-runtime | `phenotype-omlx/perf-core/model-plan/` (plus empty `AgilePlus/PhenoRuntime/` placeholder) | Inherits `git@github.com:KooshaPari/phenotype-omlx.git` for the model-plan path | Parent `feat/cross-repo-audit-wave2` / `f34ca8cb9d7c18fd884438f63baf55b6d2b29494` | Durable session/model state, replay and runtime-state contracts | **Implementation is a subpath of canonical phenotype-omlx; standalone PhenoRuntime checkout absent.** | MLX model-plan state feeds harness evaluation and Tracera trace/compliance evidence. | Separate PhenoRuntime authority is unresolved; parent tree is dirty. |

## Evidence and interpretation

- Repository identity, remotes, branches, HEADs and cleanliness were read with
  `git rev-parse`, `git remote get-url origin`, `git branch --show-current`,
  and `git status --porcelain`.
- `AgilePlus/ARCHITECTURE.md` defines the Helios and agent-experiment grouping.
- `phenotype-omlx/docs/sessions/20260721-eval-interchange/INTERCHANGE_CONTRACT.md`
  names `pheno-harness` as producer and phenotype-omlx as consumer.
- Empty placeholder directories and archived copies are not promoted to
  authority without an owned remote and an auditable branch/HEAD.
