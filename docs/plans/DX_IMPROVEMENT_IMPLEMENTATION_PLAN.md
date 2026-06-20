# DX Improvement Implementation Plan
**Date:** 2026-02-06
**Status:** Ready for Execution
**Research:** GSD + OpenSpec + BMAD + 40+ Claude Code V4 sources

## Executive Summary

Transform trace project's development experience through:
1. **Hybrid hook system** (user + project level) with intelligent triggers
2. **Auto-detection** replacing manual slash commands
3. **Specialized agents** with isolated contexts
4. **Session learning** that teaches future sessions

---

## Phase 1: Hook System (Week 1)

### 1.1 File Access Monitoring Hook
**Type:** PreToolUse
**Scope:** User-level (`~/.claude/hooks/file-monitor.py`)

```python
#!/usr/bin/env python3
import json, sys
from pathlib import Path

SENSITIVE = {'.env', '.env.local', 'secrets.json', 'id_rsa', 'bun.lock'}

data = json.load(sys.stdin)
file_path = data.get('tool_input', {}).get('file_path', '')

if Path(file_path).name in SENSITIVE:
    # WARN but don't block (user requirement)
    print(f"⚠️ Accessing sensitive file: {file_path}", file=sys.stderr)
    print(f"📋 Logged: {Path(file_path).name} access at {datetime.now()}", file=sys.stderr)

sys.exit(0)  # Allow operation
```

**Configuration:** `~/.claude/settings.json`
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Read|Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/hooks/file-monitor.py"
      }]
    }]
  }
}
```

### 1.2 Auto-Lint Hook (REPLACES Auto-Test)
**Type:** PostToolUse
**Scope:** Project-level (`.claude/hooks/auto-lint.sh`)

```bash
#!/bin/bash
# Only run on code file edits

TOOL_NAME="$1"
FILE_PATH=$(echo "$2" | jq -r '.file_path // empty')

if [[ "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "Write" ]]; then
    exit 0
fi

# Detect file type
case "$FILE_PATH" in
    *.ts|*.tsx|*.js|*.jsx)
        echo "🔧 Running lint + typecheck..."
        cd frontend/apps/web && bun run lint --fix "$FILE_PATH" 2>&1
        cd frontend/apps/web && bun run typecheck 2>&1
        ;;
    *.go)
        echo "🔧 Running gofmt + golangci-lint..."
        gofmt -w "$FILE_PATH"
        golangci-lint run "$FILE_PATH" 2>&1
        ;;
    *.py)
        echo "🔧 Running black + ruff..."
        black "$FILE_PATH"
        ruff check --fix "$FILE_PATH" 2>&1
        ;;
esac

exit 0
```

### 1.3 Context Injection Hook
**Type:** UserPromptSubmit
**Scope:** Project-level (`.claude/hooks/context-inject.sh`)

```bash
#!/bin/bash
# Inject git context into user prompts

BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
RECENT_COMMITS=$(git log --oneline -3 2>/dev/null || echo "")
STATUS=$(git status --short 2>/dev/null || echo "")

cat <<EOF

## Current Context
- Branch: $BRANCH
- Recent commits:
$RECENT_COMMITS
- Modified files:
$STATUS

EOF
```

### 1.4 Session Learning Hook (ACE-inspired)
**Type:** SessionEnd
**Scope:** User-level (`~/.claude/hooks/session-learn.py`)

**Pattern:** (Awaiting ACE/evolver research for implementation details)
- Analyze session for patterns
- Extract: ✅ Do this / ❌ Don't do this / 📝 Notes
- Update `~/.claude/memory/lessons-learned.md`
- Auto-inject into next session startup

---

## Phase 2: Auto-Detection System (Week 2)

### 2.1 Context Pattern Matcher
**Location:** `.claude/skills/auto-detect/SKILL.md`

```markdown
---
name: Workflow Auto-Detection
description: Automatically detects and triggers workflows based on user intent
triggers:
  - conversation_start
  - user_message
---

# Auto-Detection Rules

When user says:
- "add <feature>" or "implement <thing>" → Trigger: /dev:feature
- "fix <bug>" or "bug in <thing>" → Trigger: /dev:fix
- "refactor <scope>" → Trigger: /dev:refactor
- "document <thing>" → Trigger: docs-agent

Methodology Keywords:
- "propose" → Create proposal.md (OpenSpec)
- "impl" or "implement" → GSD phase execution
- "validate" → Run verification workflow

**Confirmation Required** for:
- Git operations (commit, push, merge)
- Destructive operations (delete, force-push)
- File moves affecting >5 files
```

### 2.2 File Pattern Detection
**Location:** `.claude/hooks/file-change-detect.sh`

```bash
#!/bin/bash
# Detects file changes and triggers appropriate actions

FILE="$1"

case "$FILE" in
    *.test.ts|*.test.tsx|*_test.go|test_*.py)
        echo "📋 Test file modified - run tests with: bun test $FILE"
        ;;
    docs/*.md|README.md|CLAUDE.md)
        echo "📝 Documentation modified - checking organization..."
        # Trigger docs organization check
        ;;
    package.json|go.mod|pyproject.toml)
        echo "📦 Dependencies changed - consider running install"
        ;;
esac
```

### 2.3 Git Event Integration
**Location:** `.git/hooks/pre-commit` (with confirmation)

```bash
#!/bin/bash
# Pre-commit with user confirmation

echo "🔍 Pre-commit checks..."
echo "   - Lint + typecheck"
echo "   - Secret scanning"
echo "   - Dependency audit"
echo ""
read -p "Run checks? (Y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Run checks
    make lint && make typecheck && make audit
fi
```

---

## Phase 3: Specialized Agents (Weeks 3-4)

### 3.1 Frontend Agent
**Location:** `~/.claude/agents/frontend.md`

```markdown
---
name: frontend
description: React, Vite, TypeScript specialist for UI components and frontend logic
tools: Read, Write, Bash(bun)
model: sonnet
---

You are a frontend specialist for React + Vite + TypeScript projects.

**Focus Areas:**
- Component architecture (functional, hooks)
- State management (React Query, Context)
- Performance (memo, lazy loading, code splitting)
- TypeScript types and interfaces
- Vite build optimization

**Standards:**
- Use existing patterns from codebase
- Follow project's TypeScript config
- Maintain test coverage
- Document complex components

**Auto-invoked when:**
- UI component work
- Frontend state management
- Vite/build configuration
- React patterns
```

### 3.2 Backend Agent
**Location:** `~/.claude/agents/backend.md`

```markdown
---
name: backend
description: Go services, API handlers, and backend logic specialist
tools: Read, Write, Bash(go)
model: sonnet
---

You are a backend specialist for Go services.

**Focus Areas:**
- API handlers and routing
- Service layer architecture
- Database integration (Postgres, Neo4j)
- Error handling and logging
- Testing (unit + integration)

**Standards:**
- Follow Go idioms
- Use project's error handling patterns
- Maintain test coverage ≥90%
- Document public APIs

**Auto-invoked when:**
- API endpoint work
- Service layer changes
- Database operations
- Backend testing
```

### 3.3 Docs Agent
**Location:** `~/.claude/agents/docs.md`

```markdown
---
name: docs
description: Markdown organization, documentation structure, and content clarity specialist
tools: Read, Write
model: haiku
---

You are a documentation specialist.

**Focus Areas:**
- Markdown organization (follow docs/ structure)
- Clear, concise writing
- Proper linking and cross-references
- Code examples and usage guides

**Standards:**
- Follow project's docs/ organization rules
- Never create .md files in project root (except allowed list)
- Use proper heading hierarchy
- Include code examples

**Auto-invoked when:**
- Documentation tasks
- README updates
- CLAUDE.md modifications
- Docs organization
```

### 3.4 Test Agent
**Location:** `~/.claude/agents/test.md`

```markdown
---
name: test
description: Test gap analysis, coverage reporting, and test strategy specialist
tools: Read, Bash, Grep
model: haiku
---

You are a test strategy specialist.

**Focus Areas:**
- Test gap identification
- Coverage analysis
- Test pyramid validation (79% unit, 14% integration, 7% e2e)
- Flaky test detection

**Standards:**
- Identify gaps by feature area
- Prioritize high-value tests
- Suggest test strategies
- Report coverage regressions

**Auto-invoked when:**
- Test gap analysis requests
- Coverage reports
- Test strategy discussions
```

---

## Phase 4: Workflow Integration (Month 2)

### 4.1 YAML Workflow Definitions
**Location:** `.bmad/workflows/`

```yaml
# feature-development.yaml
name: "Feature Development"
trigger:
  - context: "add <feature>"
  - context: "implement <thing>"

sequence:
  - phase: propose
    agent: pm
    output: docs/proposals/${FEATURE_NAME}.md
    template: docs/templates/proposal.md

  - phase: plan
    agent: gsd-planner
    context_budget: 200k
    output: docs/plans/${FEATURE_NAME}-plan.md
    depends: [propose]

  - phase: design
    agent: architect
    output: docs/specs/${FEATURE_NAME}-spec.md
    gates: [proposal.md, plan.md]
    depends: [plan]

  - phase: implement
    agent: general-purpose
    parallel: true
    atomic_commits: true
    depends: [design]

  - phase: validate
    agent: test
    verify: spec.md
    depends: [implement]
```

---

## Installation Instructions

### Prerequisites
- Claude Code v2.1.7+ (for MCP Tool Search)
- Python 3.8+ (for hooks)
- jq (for JSON parsing)

### Step 1: Install User-Level Hooks
```bash
mkdir -p ~/.claude/hooks
cp hooks/user/*.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.py
```

### Step 2: Install Project-Level Hooks
```bash
mkdir -p .claude/hooks
cp hooks/project/*.sh .claude/hooks/
chmod +x .claude/hooks/*.sh
```

### Step 3: Configure Settings
Edit `~/.claude/settings.json` to enable hooks (see section 1.1)

### Step 4: Create Agents
```bash
mkdir -p ~/.claude/agents
cp agents/*.md ~/.claude/agents/
```

### Step 5: Install Auto-Detection Skills
```bash
mkdir -p .claude/skills/auto-detect
cp skills/auto-detect/SKILL.md .claude/skills/auto-detect/
```

---

## Testing & Validation

### Test File Protection
```bash
claude
> "Read .env file"
# Should see: ⚠️ Accessing sensitive file: .env
```

### Test Auto-Lint
```bash
# Edit a TypeScript file
# Hook should auto-run: lint + typecheck
```

### Test Auto-Detection
```bash
claude
> "add user authentication"
# Should auto-trigger: /dev:feature workflow
```

### Test Agent Delegation
```bash
claude
> "review the authentication component"
# Should auto-delegate to: frontend agent
```

---

## Maintenance

### Weekly
- Review session learning bullets
- Update agents based on new patterns
- Audit file access logs

### Monthly
- Review workflow effectiveness
- Update YAML definitions
- Optimize hook performance

---

## Rollback Plan

If issues arise:
1. Disable hooks: Comment out in `settings.json`
2. Remove auto-detection: Delete `.claude/skills/auto-detect/`
3. Revert to manual: Use original slash commands

---

## Next Steps

1. ✅ Research ACE/evolver (in progress)
2. Implement Session Learning Hook
3. Create all agent definitions
4. Test auto-detection in real workflows
5. Gather feedback and iterate

**Status:** Awaiting ACE/evolver research for Session Learning implementation details.
