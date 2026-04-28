# Auto Quality Runner – Enhanced Design

## Quick Start (task commands only)

```bash
cd trace
task quality:dag          # Run quality DAG (CLI)
task quality:dag:tui      # Run DAG with TUI progress (writes progress.json)
task quality:tui          # Open TUI dashboard (press R to run, f to fix)
task quality:fix          # Run fix agents for failed steps
task quality:dag:only ONLY=py-lint,py-type   # Run specific steps + deps
task quality:dag:skip SKIP=py-test,go-test   # Skip steps + dependents
```

Inspired by trace's existing quality infrastructure (`run-quality-split.sh`, `process-compose.quality.yaml`, `quality-report.py`), this design extends it with:

1. **Richer TUI dashboard** – Live-updating Textual UI (like `dev:tui`)
2. **Agent process visibility** – Show fix-agent processes alongside checkers
3. **DAG-based parallelization** – Dependency-aware execution with soft-fail
4. **DAG-based fix agents** – Split by file/checker instead of one large prompt

---

## 1. Current State (Trace)

| Component | Location | Behavior |
|-----------|----------|----------|
| `run-quality-split.sh` | `scripts/shell/` | 11 steps in parallel (naming, go-lint, go-proto, go-build, go-test, py-lint, py-type, py-test, fe-lint, fe-type, fe-build, fe-test) |
| `process-compose.quality.yaml` | `config/` | 3 processes (Go, Python, Frontend) with process-compose TUI |
| `quality-report.py` | `scripts/python/` | Parses logs, groups by file, prints action plan |
| `last-run.json` | `.quality/` | Per-step exit codes, `failed_steps` |

**Limitations:**
- No dependency DAG (e.g. `go-build` depends on `go-proto`)
- Hard fail: script exits 1 if any step fails
- Report is plain text, not a live TUI
- No agent process visibility
- No DAG-based fix agents

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Quality Runner TUI (Textual)                          │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Step Status │  │ Live Logs   │  │ Agent Procs │  │ Action Plan     │  │
│  │ (DAG view)  │  │ (streaming)│  │ (fix jobs)  │  │ (by file/check) │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Orchestrator (Python)                                 │
│  - DAG executor (topological sort, parallel tiers)                       │
│  - Soft-fail: skip dependents of failed node, run rest                  │
│  - Event bus → TUI updates                                              │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Checker DAG                    │  Fix Agent DAG                         │
│  naming → (go-lint, py-lint…)   │  Per-file or per-checker agents        │
│  go-proto → go-build → go-test  │  e.g. fix_ruff_file_foo.py             │
│  py-lint, py-type → py-test     │  fix_mypy_file_bar.py                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Checker DAG (Dependency-Aware)

```yaml
# quality-dag.yaml (conceptual)
steps:
  naming: []                    # no deps
  go-proto: []
  go-lint: [naming]
  go-build: [go-proto]
  go-test: [go-build]
  py-lint: [naming]
  py-type: [naming]
  py-test: [py-lint, py-type]
  fe-lint: [naming]
  fe-type: [naming]
  fe-build: [fe-lint, fe-type]
  fe-test: [fe-build]
```

**Parallel tiers:**
- Tier 0: `naming`, `go-proto`
- Tier 1: `go-lint`, `py-lint`, `py-type`, `fe-lint`, `fe-type`
- Tier 2: `go-build`, `py-test`, `fe-build`
- Tier 3: `go-test`, `fe-test`

**Soft-fail:**
- If `go-proto` fails → skip `go-build`, `go-test`; run all others
- If `py-lint` fails → skip `py-test`; run `py-type`, `go-*`, `fe-*`
- Continue to next tier for nodes whose deps passed

---

## 4. Fix Agent DAG (Split by File/Checker)

Instead of one large prompt: "fix all issues in the repo", spawn:

| Strategy | Granularity | Example |
|----------|-------------|---------|
| **By file** | One agent per file with issues | `fix backend/pkg/foo.go` (gofmt + vet) |
| **By checker** | One agent per checker | `fix all ruff issues`, `fix all mypy issues` |
| **By checker+file** | One agent per (checker, file) | `fix ruff in src/bar.py` |

**Recommended:** Start with **by checker** (simpler), then add **by file** for large files or when checker output is huge.

**Agent invocation:**
```
# Per checker (e.g. ruff)
cursor/agent fix --scope ruff --context .quality/logs/py-lint.log

# Per file (e.g. src/foo.py)
cursor/agent fix --scope file --path src/foo.py --context .quality/issues.json
```

**DAG for fix agents:**
- Lint-fix agents can run in parallel (no cross-file deps for most linters)
- Type-check fix agents may need ordering if files import each other (mypy: fix in dependency order)

---

## 5. TUI Dashboard Design

### 5.1 Layout (Textual)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Quality Runner                                    [r]efresh [q]uit       │
├──────────────────────────────────────────────────────────────────────────┤
│ Steps (DAG)              │ Live Logs (selected step)                      │
│ ● naming     ✓ 0.2s      │ $ task lint:naming                             │
│ ● go-proto   ✓ 1.1s      │ ...                                           │
│ ● go-lint    ✗ 0.5s      │ backend/pkg/foo.go:12: undefined: Bar         │
│ ● go-build   ⊘ skipped   │                                                │
│ ● py-lint    ● running   │                                                │
│ ● py-type    ○ pending   │                                                │
│ ...                     │                                                │
├──────────────────────────────────────────────────────────────────────────┤
│ Fix Agents (if any)                                                       │
│ ● fix_ruff_src_bar     ● running   │ fix_mypy_src_baz     ○ queued       │
├──────────────────────────────────────────────────────────────────────────┤
│ Action Plan (by file)                                                     │
│ src/foo.py: ruff E501, mypy error                                         │
│ backend/pkg/bar.go: vet undefined                                         │
└──────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Widgets

| Widget | Purpose |
|--------|---------|
| `StepStatusTable` | DAG steps with status (pending/running/passed/failed/skipped), duration |
| `LiveLogView` | Streaming log for selected step (tail of `.quality/logs/<step>.log`) |
| `AgentProcessList` | Fix agent jobs (name, status, progress) |
| `ActionPlanPanel` | By-file issues from `quality-report.py` logic, live-updated |

### 5.3 Data Flow

- Orchestrator writes to `.quality/logs/<step>.log` and `.quality/logs/<step>.exit`
- TUI polls or uses `watchdog` on `.quality/logs/` and `last-run.json`
- Optional: Orchestrator publishes events over a simple IPC (e.g. JSON file, or socket) for lower latency

---

## 6. Implementation Plan

### Phase 1: DAG Executor + Soft-Fail (Python)

1. **`scripts/python/quality_runner.py`**
   - Load step DAG from config (YAML or code)
   - Topological sort → tiers
   - Execute tier-by-tier: run all in tier in parallel, collect exit codes
   - Soft-fail: if step fails, mark dependents as `skipped`, continue
   - Write `last-run.json` with `skipped` and `failed` steps

2. **`config/quality-dag.yaml`**
   - Define steps and dependencies (as above)

### Phase 2: TUI Dashboard

3. **`src/tracertm/tui/apps/quality_runner.py`** (or `scripts/python/quality_runner_tui.py`)
   - Textual app with `StepStatusTable`, `LiveLogView`, `ActionPlanPanel`
   - Spawn `quality_runner.py` as subprocess or run in thread
   - Use `watchdog` or polling to refresh on log/exit file changes

4. **Task/Make target**
   - `task quality:tui` or `make quality-tui` → run TUI

### Phase 3: Agent Process Visibility

5. **Fix agent spawner**
   - After quality run, parse `quality-report.py` output (or `last-run.json` + logs)
   - Build list of fix jobs: `[(checker, file?), ...]`
   - Spawn agents (e.g. via `cursor` CLI or subprocess)
   - Report agent PIDs/status to TUI

6. **`AgentProcessList` widget**
   - Show agent name, status, optional log tail

### Phase 4: DAG-Based Fix Agents

7. **Fix agent orchestration**
   - Group issues by checker and optionally by file
   - Create DAG: e.g. `fix_ruff` → (no deps), `fix_mypy` → (optional: after ruff if ruff can change types)
   - Spawn agents with scoped prompts (file path, checker, log excerpt)

8. **Integration**
   - "Fix" button in TUI triggers agent spawn
   - Or: `task quality:fix` runs fix agents after quality

---

## 7. File Structure

```
trace/
├── config/
│   ├── quality-dag.yaml          # Step dependencies
│   └── quality-fix-dag.yaml     # Fix agent dependencies (optional)
├── scripts/
│   ├── python/
│   │   ├── quality_runner.py     # DAG executor, soft-fail
│   │   ├── quality_runner_tui.py  # TUI entrypoint
│   │   └── quality-report.py      # (existing) parse logs
│   └── shell/
│       └── run-quality-split.sh  # (keep for non-TUI / CI)
├── src/tracertm/tui/
│   ├── apps/
│   │   └── quality_runner_app.py # Textual app
│   └── widgets/
│       ├── step_status_table.py
│       ├── live_log_view.py
│       ├── agent_process_list.py
│       └── action_plan_panel.py
└── .quality/
    ├── logs/
    └── last-run.json
```

---

## 8. Dependencies

- **textual** – already in trace
- **watchdog** – already in trace (for file watching)
- **PyYAML** – for DAG config
- Optional: **hatchet-sdk** or similar for agent observability (trace already has it)

---

## 9. Backward Compatibility

- `run-quality-split.sh` remains for CI and non-TUI use
- `quality-report.py` unchanged; TUI consumes its output format
- `process-compose.quality.yaml` can stay for "run quality as 3 processes" mode; new TUI runs the Python DAG executor instead

---

## 10. Example: quality-dag.yaml

```yaml
version: 1
steps:
  naming:
    deps: []
    command: task lint:naming
  go-proto:
    deps: []
    command: task proto:gen
  go-lint:
    deps: [naming]
    command: task go:lint
  go-build:
    deps: [go-proto]
    command: task go:build
  go-test:
    deps: [go-build]
    command: task go:test
  py-lint:
    deps: [naming]
    command: poe lint
  py-type:
    deps: [naming]
    command: poe type-check
  py-test:
    deps: [py-lint, py-type]
    command: poe test
  fe-lint:
    deps: [naming]
    command: bun run --cwd frontend lint
  fe-type:
    deps: [naming]
    command: bun run --cwd frontend typecheck
  fe-build:
    deps: [fe-lint, fe-type]
    command: bun run --cwd frontend build
  fe-test:
    deps: [fe-build]
    command: bun run --cwd frontend test
```

---

## 11. Soft-Fail Pseudocode

```python
def run_tier(tier: list[str], steps: dict, results: dict) -> None:
    async def run_one(name: str):
        if any(results.get(d) != 0 for d in steps[name]["deps"]):
            results[name] = "skipped"
            return
        code = subprocess.run(steps[name]["command"], ...).returncode
        results[name] = code

    asyncio.gather(*[run_one(s) for s in tier])

def run_dag(steps: dict) -> dict:
    tiers = topological_sort(steps)
    results = {}
    for tier in tiers:
        run_tier(tier, steps, results)
    return results
```

---

## 12. Next Steps

1. Implement `quality_runner.py` with DAG + soft-fail
2. Add `quality-dag.yaml` config
3. Build minimal TUI (step status + live log)
4. Add agent process list and fix-agent spawner
5. Add DAG-based fix agent orchestration
