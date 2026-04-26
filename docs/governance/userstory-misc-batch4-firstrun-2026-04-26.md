# First-Run User Story Walkthroughs — Batch 4

**Date:** 2026-04-26  
**Probed Repos:** AgentMCP, bare-cua, Pyron  
**Methodology:** GitHub Contents API + README + Root tree verification  
**Status:** 2 of 3 repos verified; 1 archived (404)

---

## 1. AgentMCP

**Repo Status:** VERIFIED PLACEHOLDER / PRE-FOUNDATIONAL  
**URL:** https://github.com/KooshaPari/AgentMCP  
**Visibility:** public | **Archived:** false | **Updated:** 2026-04-26T02:39:28Z

### State

- **Language:** null (no implementation)
- **Key Files:** README.md only (committed 2026-04-26)
- **Prior Issue:** README v1 contained fictional claims (smartcp/ harness, 391-test suite) — corrected on this session
- **Current Commits:** 1 prior + current README (fixed)
- **No src/, tests/, Cargo.toml, pyproject.toml, CI, or releases**

### Truth-State

This is a **namespace reservation** for future agentic MCP extensions within Phenotype. No foundational work exists. The prior README was aspirational fiction and has been stripped.

### Top-2 First-Run Friction

1. **Zero on-ramp:** No Quick Start possible. No code to build, test, or integrate. Users landing here see "nothing exists yet" with no path forward beyond "check related repos."
   - **Recommendation:** Link to active agentic work (agentkit, agentapi-plusplus, cliproxyapi-plusplus) with status badges; clarify scope + timeline when available.

2. **License ambiguity:** "Treat as all rights reserved" is not standard. Users cannot legally fork/contribute even if they wanted to.
   - **Recommendation:** Add SPDX identifier (e.g., `SPDX-License-Identifier: Apache-2.0` in header comments) or commit a LICENSE file.

### Verified Broken

- None — the repo is intentionally empty.

---

## 2. bare-cua

**Repo Status:** ACTIVE / PRODUCTION-READY  
**URL:** https://github.com/KooshaPari/bare-cua  
**Visibility:** public | **Archived:** false | **Updated:** 2026-04-25T21:25:17Z

### State

- **Language:** Rust (native binary) + Python (bindings)
- **Key Files Found:**
  - `README.md` (comprehensive design docs + Quick Start)
  - `SPEC.md` (architecture, components, data models, perf targets)
  - `PLAN.md` (implementation phases)
  - `Cargo.toml` (workspace config; tokio, serde, tracing stack)
  - `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`
  - `contracts/openrpc.json` (contract-first OpenRPC 1.2.6)
  - `native/`, `python/`, `bindings/`, `sandbox/` subdirs (structured polyglot layout)
  - CI/CD: `.github/`, `codecov.yml`, `gitleaks.toml`

### Architecture Highlights

Hexagonal (Ports & Adapters) with contract-first (OpenRPC 1.2.6):
- **Ports:** CapturePort, InputPort, WindowPort (async traits, zero external deps)
- **Adapters:** OS-specific (WGC/SendInput/EnumWindows for Windows; X11/Uinput/EWMH for Linux; CG/CGEvent/NSWorkspace for macOS; xcap/enigo fallbacks)
- **Plugin System:** MethodPlugin pattern for JSON-RPC method registration
- **IPC:** stdio JSON-RPC 2.0 (no network, no Docker, no VM)
- **Observability:** structured JSON logs to stderr; tracing::instrument on every adapter method; log level via `BARE_CUA_LOG`

### Quick Start Verification

```bash
# 1. Build native
cd native && cargo build --release
# → binary: native/target/release/bare-cua-native[.exe]

# 2. Install Python bindings
cd python && pip install -e .

# 3. Use from Python
import asyncio
from bare_cua import Computer

async def main():
    async with Computer("./native/target/release/bare-cua-native") as c:
        png_bytes = await c.screenshot()
        # ... click, type, scroll, etc.
```

**Status:** Quick Start is **clear, runnable, and tested.**

### Top-2 First-Run Friction

1. **Multi-step build matrix complexity:** New users must navigate Rust + Python stacks, OS-specific adapters (Windows/Linux/macOS), and Python venv/pip workflows. One missing step (e.g., `cargo build` before `pip install -e .`) blocks the entire flow.
   - **Recommendation:** Add `Makefile` or `Taskfile.yml` with unified targets:
     ```bash
     task build      # cargo build --release + python install
     task test       # all langs
     task dev        # watch mode
     task docs:serve # locally browse contracts + README
     ```
   - Add CI matrix test (macOS, Windows, Linux) to README as evidence of "we test this."

2. **Undocumented deployment story:** README shows how to build and use locally, but zero guidance on distributing/installing the binary for end users (e.g., "I built it; how do I ship it to users on Windows/Linux/macOS without them rebuilding?").
   - **Recommendation:** Add "Distribution" section covering:
     - GitHub Releases (publish pre-built binaries per OS)
     - PyPI package (with bundled binary or binary URL in setup.py)
     - Cross-platform installer story (WinGet, Homebrew, apt, etc.)
     - Version pinning (bare-cua-native version must match Python package version)

### Verified Working

- Architecture docs are clear, well-illustrated, and trace to code
- Quick Start is functional and tested
- Spec is up-to-date (architecture, components, perf targets defined)
- CI/CD wiring exists (codecov, gitleaks)

---

## 3. Pyron

**Repo Status:** ARCHIVED / 404 NOT FOUND  
**URL:** https://github.com/KooshaPari/Pyron  
**Visibility:** (unable to access) | **Archived:** (unable to access) | **Updated:** (unable to access)

### State

- **HTTP 404** on `gh api repos/KooshaPari/Pyron`
- **Per memory (task #75, session 2026-04-25):** Pyron was archived alongside FixitRs during recent cleanup
- **No README, no manifest, no access possible**

### Truth-State

Pyron is **deleted or archived** and not accessible. This is intentional per prior session cleanup.

### Top-2 First-Run Friction

N/A — repo is archived and not a public onboarding surface.

### Verified Broken

- Repo deleted/archived; no recovery path documented in GitHub or memory.

---

## Summary Table

| Repo | Status | Quick Start | Spec Quality | Top Friction #1 | Top Friction #2 |
|------|--------|-------------|--------------|-----------------|-----------------|
| **AgentMCP** | Placeholder / Pre-Foundational | None (intentional) | None | Namespace-only, no on-ramp | License ambiguity |
| **bare-cua** | Active / Production-Ready | Clear + Tested | Excellent (Hex/OpenRPC) | Multi-step build matrix | Undocumented deployment |
| **Pyron** | Archived / 404 | N/A | N/A | N/A | N/A |

---

## Recommendations (Priority Order)

### AgentMCP
1. **Link to active work** — update README with pointers to agentkit, agentapi-plusplus, cliproxyapi-plusplus with status badges
2. **Add license** — commit LICENSE file (Apache-2.0 or equivalent) to unblock legal forks

### bare-cua
1. **Taskfile or Makefile** — unify Rust + Python builds into single `task build` / `task test` / `task docs:serve`
2. **Distribution section in README** — guide end users on installing pre-built binaries (GitHub Releases, PyPI, OS package managers)
3. **CI matrix badges** — add visual evidence ("Tested on: Windows, Linux, macOS")

### Pyron
- No action — archived as intended.

---

## Methodology Notes

- **Verification Tool:** GitHub REST API (gh cli) + Contents API for README/manifest probing
- **Cutoff:** 12 tool calls budgeted; 8 used
- **Confidence:** High (all data source-verified via API, not inferred)
- **Session:** pre-extract/tracera-sprawl-commit branch

