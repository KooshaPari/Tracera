# WP-03 — Establish installed AP persistence/isolation baseline

**Gate:** G1 (Execution kernel qualified)  
**Status:** design_doc — requires AgilePlus repo  
**Date:** 2026-09-17  

## What This WP Requires

Run a real installed AgilePlus journey outside the source tree; capture baseline and exact missing kernel obligations before patching.

## Acceptance Oracles

### T13 — Project persistence and isolation survives installed restart
1. Create work item A in project P via AP CLI/API
2. Restart AP outside source tree
3. Verify A is retained with correct state
4. Create project Q; verify Q cannot see or mutate A

### T32 — Candidate install/deploy works outside source tree
1. Install supported artifact via chosen mode (binary, container, etc.)
2. Launch, persist data, restart, recover state
3. Uninstall cleanly

## Implementation Approach

### Step 1: Inventory current AP persistence
- Locate AP database/storage files
- Document what state is persisted (projects, work items, claims)
- Identify what is NOT persisted (in-memory state, caches)

### Step 2: Install outside source tree
- Build AP binary/package
- Install to a clean directory (not the repo checkout)
- Verify all features work without source tree dependencies

### Step 3: Isolation test
- Create two independent projects (A, B)
- Verify cross-project isolation
- Verify restart preserves isolation

### Step 4: Record evidence
- Exact binary version/commit
- Exact install path and mode
- Test results with timestamps
- Rollback procedure

## Dependencies
- WP-01 (source register) — completed

## What We Can Do From Tracera
- Design doc (this file)
- Integration test interface: define the contract that AP persistence must satisfy for Tracera to trust it
- The actual implementation must happen in the AgilePlus repo

## Rollback
- Preserve prior compatible data formats
- Rehearse schema restore
- Do not delete old persistence until consumer parity and cutover acceptance
