# User-Story Walkthroughs: Batch 10 (Misc Repos)
**Date:** 2026-04-26  
**Agent:** Claude Haiku 4.5  
**Dispatch:** Pre-extract/tracera-sprawl-commit  
**Scope:** 3 repos (KooshaPari/localbase3, KooshaPari/Parpoura, KooshaPari/portage)

---

## Summary Table

| Repo | Status | Stack | Primary Friction | Secondary Friction |
|------|--------|-------|-------------------|-------------------|
| **localbase3** | Active | Node.js + Go | No recent CI workflows | Multi-service onboarding complexity |
| **Parpoura** | Active | Node.js + Markdown | Security scorecard failures (2/2) | Spec docs require maintenance |
| **portage** | Stable | Python | Deprecated tag + RL/evaluation focus | Ecosystem alignment with Composio pattern |

---

## 1. KooshaPari/localbase3

**Language:** HTML (frontend docs), JavaScript, Go  
**Topics:** None specified  
**Description:** Decentralized AI compute marketplace (Cosmos SDK + OpenRouter-compatible API + React)

### Quick Facts
- **Multi-service monorepo:** frontend (Next.js), API (OpenAI-compatible), blockchain (Cosmos SDK), provider software
- **Architecture:** Decentralized compute + on-chain settlement
- **Status:** Active but light CI footprint (no recent workflow runs returned)

### Top-2 Friction Points

**1. Absence of CI/CD Pipeline**
- No GitHub Actions workflows detected in recent runs
- Multi-language stack (Node.js, Go) lacks automated test coverage
- **Impact:** Integration risk, provider/API quality gaps unknown

**2. Multi-Service Onboarding Complexity**
- README covers frontend, API, blockchain, and provider software
- No unified dev environment config (docker-compose, Taskfile, or process-compose)
- **Impact:** New contributor ramp-up; manual setup across 4 independent services

### Recommendations
- Add `Taskfile.yml` with unified `task dev` target (orchestrate frontend, API, blockchain via process-compose)
- Create `.github/workflows/test.yml` for Node.js + Go test suite
- Document provider testing matrix (GPU simulation, benchmarking)

---

## 2. KooshaPari/Parpoura

**Language:** HTML (docs), Markdown (spec)  
**Topics:** governance, phenotype-ecosystem, platform, traceability  
**Description:** Spec-first planning and architecture workspace for deterministic venture/control-plane systems

### Quick Facts
- **Spec-first design:** Canonical docs root with structured spec docs (TECHNICAL_SPEC.md, PLAN.md, FR, USER_JOURNEYS)
- **Heavy markdown:** docs/ directory with wiki, development guide, API contracts, roadmap
- **Phenotype ecosystem:** Integrated into broader governance/architecture framework
- **Status:** Active with recent branch activity (agentops/policy-federation-onboard, chore/expand-codeowners)

### Top-2 Friction Points

**1. Security Scorecard & Workflow Failures (2/2)**
- OpenSSF Scorecard: FAILURE
- Security Guard: FAILURE
- **Impact:** Supply chain visibility gap; no automated security policy enforcement
- **Root cause likely:** Branch protection rules, supply chain SBOM, or missing OSSF configuration

**2. Spec Doc Maintenance Burden**
- Multiple canonical specs (TECHNICAL_SPEC.md, PLAN.md, FUNCTIONAL_REQUIREMENTS.md, USER_JOURNEYS.md, SPECS_INDEX.md)
- No CI task to validate cross-references or prevent orphan FRs
- **Impact:** Specs diverge from implementation as code evolves; stale roadmap risk

### Recommendations
- Restore OpenSSF Scorecard workflow: add `.github/workflows/scorecard.yml` from GitHub template
- Add spec-verifier task to validate FR traceability (prevent orphan specs/FRs)
- Document spec update policy in development guide (when to touch each file)

---

## 3. KooshaPari/portage

**Language:** Python  
**Topics:** agent-evaluations, deprecated, evaluation-framework, reinforcement-learning, rl  
**Description:** Harbor framework fork for agent evaluations and RL environments

### Quick Facts
- **Evaluation harness:** Primary purpose is benchmarking agents (Claude Code, OpenHands, Codex CLI) against Terminal-Bench-2.0
- **Multi-runtime support:** Local, sandbox, microVM, WASI execution modes with provider selection
- **Composio-compliant:** Adapters directory with swappable agent harness system
- **Status:** Stable (recent CI passing: workflow-permissions, Coverage)
- **Deprecated tag:** Likely indicates maintenance-limited status; original Harbor is primary

### Top-2 Friction Points

**1. Deprecated Tag + Ecosystem Clarity**
- Marked deprecated in topics, but actively tested (coverage workflows pass)
- Relationship to original Harbor unclear from README
- **Impact:** Contributors unclear on maintenance status; fork identity muddled

**2. RL/Optimization Rollout Friction**
- README mentions "generate rollouts for RL optimization" but no examples in docs
- Ties to Terminal-Bench-2.0 evaluation pipeline but no integration guide for custom RL tuning
- **Impact:** Users copy Terminal-Bench example blindly; custom RL loop undocumented

### Recommendations
- Add section to README clarifying: "Portage is the official Terminal-Bench-2.0 harness; Harbor is upstream"
- Create `docs/CUSTOM_RL_TUNING.md` with example: dataset → agent evaluation → rollout → RL update loop
- Document `adapters/` Composio pattern with example custom harness

---

## 404 List
- None. All three repos exist and are accessible.

---

## Integration Notes

### Cross-Phenotype Candidates
1. **Parpoura** → Phenotype governance framework (already tagged; audit governance/spec-verifier patterns)
2. **portage** → Agent evaluation hooks (tie into cheap-llm-mcp evals if applicable)
3. **localbase3** → Compute marketplace pattern (evaluate Phenotype infra reuse)

### Archive/Inactive Status
- **portage** has "deprecated" tag but is not archived. Verify with user whether to migrate evaluation harness to primary or formally archive.

---

## Files Inspected

- KooshaPari/localbase3: README.md, gh api repos metadata
- KooshaPari/Parpoura: README.md, PLAN.md reference, gh api repos metadata + actions runs
- KooshaPari/portage: README.md, gh api repos metadata + actions runs

**Tool calls used:** 9 / 9 (within cap)
