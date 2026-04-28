# Advanced Hook Patterns - Quick Reference

**Source:** `docs/research/ADVANCED_HOOK_PATTERNS_AND_MCP.md` (1,527 lines)
**Date:** 2026-02-06
**Scope:** Production-ready composite hooks, chains, and MCP integrations

---

## 🔗 Pattern Categories

### 1. Composite Hooks (Multi-Stage Pipelines)
**Sequential execution with fail-fast:**
- PreCommit Pipeline: format → lint → security → coverage
- PostDeploy Validation: smoke tests → metrics → rollback
- OnError Recovery: retry → log → escalate

### 2. Conditional Hooks (Context-Aware)
**Smart execution based on context:**
- Branch-based: Run expensive checks only on main
- File-based: Skip tests for docs-only changes
- Size-based: Different linters per project size
- Time-based: Scheduled vs on-demand hooks

### 3. Hook Chains (Output Feeding)
**One hook's output feeds the next:**
- Coverage regression → identify gaps → generate stubs
- Complexity detection → suggest refactor → create ticket
- Performance degradation → profile → optimization PR

### 4. Collaborative Hooks (Hook → Agent)
**Hooks spawn agents for complex work:**
- Failed test → debugging agent → auto-fix attempt
- Security issue → security agent → patch generation
- Performance regression → profiling agent → optimization

### 5. MCP Integrations (External Services)
**Hooks using MCP servers:**
- Linear: Auto-create tickets from TODOs
- Slack: Deployment notifications, test alerts
- GitHub: Auto-PR labeling, review requests
- Sentry: Error tracking, auto-triage

---

## 🚀 Quick Implementation Examples

### PreCommit Quality Pipeline
```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(git commit)": [{
        "command": "bash -c 'set -e; bun format; bun lint; trivy fs .; check-coverage.py'"
      }]
    }
  }
}
```
**Features:** Fail-fast, clear progress, actionable errors

### Hook → Agent Collaboration
```json
{
  "hooks": {
    "PostToolUseFailure": {
      "Bash(bun test)": [{
        "command": "claude-agent debugging-agent --task 'Fix failing tests' --context $TOOL_RESULT"
      }]
    }
  }
}
```
**Features:** Auto-spawn agent, pass failure context, attempt fix

### MCP Linear Integration
```json
{
  "hooks": {
    "PostToolUse": {
      "Edit": [{
        "command": "grep TODO $FILE | linear issue create --from-stdin",
        "async": true
      }]
    }
  }
}
```
**Features:** Auto-ticket creation, async execution, contextual

---

## 📊 10 Composite Hook Workflows

| Workflow | Stages | Trigger | Impact |
|----------|--------|---------|--------|
| PreCommit Pipeline | 4 (format→lint→security→coverage) | git commit | Prevent bad commits |
| PostDeploy Validation | 3 (smoke→metrics→rollback) | git push main | Deployment safety |
| OnError Recovery | 3 (analyze→retry→log) | Test failure | Auto-fix flaky tests |
| Bundle Size Gate | 2 (build→compare) | npm build | Prevent bloat |
| API Contract Check | 3 (schema→diff→validate) | API changes | Breaking changes |
| Performance Monitor | 4 (profile→compare→alert→PR) | Post-deploy | Regression detection |
| Security Scan | 3 (secrets→deps→SAST) | Pre-commit | Vulnerability prevention |
| Dependency Update | 4 (check→update→test→PR) | Weekly cron | Security patching |
| Documentation Sync | 3 (extract→format→PR) | Code changes | Doc freshness |
| Test Pyramid Check | 2 (count→validate) | Pre-push | Coverage quality |

---

## 🎯 8 Conditional Hook Patterns

| Pattern | Condition | Action | Example |
|---------|-----------|--------|---------|
| Branch-Based | `if main` | Run full CI | Expensive checks only on main |
| File-Based | `if *.md` | Skip tests | Docs-only changes |
| Size-Based | `if >500 LOC` | Warn + request split | Large PR detection |
| Time-Based | `if weekday` | Schedule heavy tasks | Weekend long-running jobs |
| User-Based | `if @team-lead` | Skip approval | Trusted committer bypass |
| Dependency-Based | `if package.json` | Run audit | Security scan on deps |
| Error-Based | `if test fail` | Retry with verbose | Flaky test debugging |
| Performance-Based | `if >10s build` | Enable caching | Slow build optimization |

---

## ⛓️ 6 Hook Chain Examples

### 1. Coverage Regression Chain
```
Coverage Regression Hook
  ↓ (extracts untested files)
Generate Test Stubs Hook
  ↓ (creates test files)
Spawn Test Agent
  ↓ (implements tests)
Update Coverage Report
```

### 2. Complexity Detection Chain
```
Complexity Analysis Hook
  ↓ (identifies complex functions)
Suggest Refactoring Hook
  ↓ (generates refactor plan)
Create Linear Ticket
  ↓ (tracks technical debt)
Schedule Review
```

### 3. Performance Degradation Chain
```
Performance Benchmark Hook
  ↓ (detects regression)
Profile Application Hook
  ↓ (identifies bottleneck)
Spawn Performance Agent
  ↓ (generates optimization)
Create PR with Fix
```

### 4. Security Vulnerability Chain
```
Dependency Scan Hook
  ↓ (finds CVEs)
Risk Assessment Hook
  ↓ (prioritizes by severity)
Auto-Update Hook
  ↓ (patches non-breaking)
Slack Alert for Breaking
```

### 5. Bundle Size Chain
```
Bundle Analysis Hook
  ↓ (measures size)
Compare to Baseline
  ↓ (detects bloat)
Identify Heavy Imports
  ↓ (finds culprits)
Suggest Tree-Shaking
```

### 6. API Breaking Change Chain
```
OpenAPI Diff Hook
  ↓ (detects schema changes)
Classify Breaking vs Non-Breaking
  ↓ (severity assessment)
Update Changelog
  ↓ (documents change)
Bump Version (semver)
```

---

## 🤝 5 Collaborative Hook → Agent Patterns

### 1. Test Failure → Debugging Agent
```json
{
  "PostToolUseFailure": {
    "Bash(bun test)": [{
      "command": "claude spawn debugging-agent --failure-log $RESULT"
    }]
  }
}
```

### 2. Security Issue → Security Agent
```json
{
  "PostToolUse": {
    "Bash(trivy scan)": [{
      "command": "if grep CRITICAL; then claude spawn security-agent --cves $RESULT; fi"
    }]
  }
}
```

### 3. Performance Regression → Profiling Agent
```json
{
  "PostToolUse": {
    "Bash(benchmark)": [{
      "command": "if [ $CURRENT_TIME -gt $BASELINE ]; then claude spawn profiling-agent; fi"
    }]
  }
}
```

### 4. Large PR → Review Agent
```json
{
  "PreToolUse": {
    "Bash(gh pr create)": [{
      "command": "if [ $LINES -gt 500 ]; then claude spawn review-agent --files $CHANGED; fi"
    }]
  }
}
```

### 5. Migration Needed → Migration Agent
```json
{
  "UserPromptSubmit": [{
    "command": "if grep 'upgrade framework'; then claude spawn migration-agent; fi"
  }]
}
```

---

## 🔌 12 MCP Integration Examples

| Service | Use Case | Hook Event | MCP Command |
|---------|----------|------------|-------------|
| **Linear** | Auto-ticket TODOs | PostToolUse(Edit) | `linear issue create` |
| **Slack** | Deploy notifications | PostToolUse(git push) | `slack send-message` |
| **GitHub** | Auto-label PRs | PreToolUse(gh pr create) | `github add-label` |
| **Sentry** | Error triage | PostToolUseFailure | `sentry create-issue` |
| **Datadog** | Performance metrics | PostToolUse(deploy) | `datadog send-metric` |
| **PagerDuty** | Critical alerts | PostToolUseFailure | `pagerduty trigger` |
| **Jira** | Ticket sync | PostToolUse(git commit) | `jira create-issue` |
| **Notion** | Doc updates | PostToolUse(Edit *.md) | `notion update-page` |
| **Calendar** | Release schedule | UserPromptSubmit | `calendar create-event` |
| **Figma** | Design sync | PostToolUse(*.tsx) | `figma export-component` |
| **Stripe** | Billing events | PostToolUse(deploy) | `stripe log-event` |
| **SendGrid** | Email reports | Scheduled | `sendgrid send-email` |

---

## ⚙️ Configuration Templates

### Full-Stack Quality Pipeline
```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(git commit)": [{
        "command": ".claude/hooks/pre-commit-pipeline.sh",
        "description": "4-stage quality gate"
      }]
    },
    "PostToolUse": {
      "Edit|Write": [{
        "command": ".claude/hooks/auto-format.sh",
        "description": "Auto-format on save"
      }],
      "Bash(git push origin main)": [{
        "command": ".claude/hooks/post-deploy-validation.sh",
        "async": true,
        "description": "Deployment validation + rollback"
      }]
    },
    "PostToolUseFailure": {
      "Bash(bun test)": [{
        "command": ".claude/hooks/test-failure-recovery.sh",
        "description": "Auto-retry flaky tests"
      }]
    },
    "UserPromptSubmit": [{
      "command": ".claude/hooks/context-injection.sh",
      "description": "Git context + recent changes"
    }]
  }
}
```

---

## 🎯 Best Practices

### Performance
- ✅ Use `async: true` for long-running hooks
- ✅ Cache expensive operations (lint results, coverage)
- ✅ Run hooks in parallel where possible
- ✅ Skip hooks for trivial changes (docs-only)

### Error Handling
- ✅ Always use `set -e` for fail-fast
- ✅ Provide actionable error messages
- ✅ Log failures for debugging
- ✅ Distinguish warnings (exit 2) from errors (exit 1)

### Security
- ✅ Never log secrets or tokens
- ✅ Validate all hook inputs
- ✅ Use environment variables for sensitive data
- ✅ Restrict hook execution scope

### Testing
- ✅ Test hooks in isolation first
- ✅ Verify exit codes (0, 1, 2)
- ✅ Check async hook completion
- ✅ Validate error messages

---

**Full Implementation Details:** `docs/research/ADVANCED_HOOK_PATTERNS_AND_MCP.md`
