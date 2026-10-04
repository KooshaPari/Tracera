# Tracera recovery authority

For the active mature-first recovery branch, future ChatGPT chats, ChatGPT Work
sessions, coding agents and humans should recover current state in this order:

1. `spec/product/mature-contract.v1.json` — accepted mature semantic contract.
2. `verification/FORWARD_WBS_2026-10-04.md` — current execution/release WBS.
3. `docs/architecture/NETWORK_DEPLOYMENT_DOCTRINE.md` — tailnet-first network/deployment doctrine.
4. `verification/NEXT_DEPLOYABLE_RELEASE_2026-10-04.md` — deployed-release gate.
5. Current Git/CI evidence.
6. Older recovery/history documents as evidence, not automatically current authority.

## Hard invariants

- Locked product pair in this chat/program: Tracera + AgilePlus only.
- PhenoRegistry is supporting governance/evidence, not product #3.
- Tracera owns product truth; AgilePlus owns development/work truth.
- AgilePlus AcceptedWork is not Tracera Satisfied.
- Historical truth is not current evidence applicability.
- Missing/inferred dependency information cannot prove independence.
- Bounded invalidation with `complete=false` must never be reported as complete.
- Test existence is not test execution.
- Route/page existence is not journey closure.
- Optimization cannot redefine graph/product truth.
- Private/operator deployment is tailnet-first. Cloudflare Tunnel is optional
  future public ingress.
- Use one host-level Caddy per physical host; do not stack reverse proxies
  without a demonstrated requirement.
- Every status report must include time-to-next-deployed/installable release.

## Git doctrine

Preserve history. Prefer additive/superseding commits, reverts and forensic
documentation over cosmetic shared-history rewrites.
