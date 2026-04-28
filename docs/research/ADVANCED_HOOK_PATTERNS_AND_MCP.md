# Advanced Hook Patterns and MCP Integrations for DX Improvement

**Research Date:** 2026-02-05
**Status:** Comprehensive Design Complete
**Scope:** Production-ready patterns for Claude Code hooks + MCP server orchestration

---

## Table of Contents

1. [Composite Hook Workflows](#1-composite-hook-workflows)
2. [Conditional Hook Patterns](#2-conditional-hook-patterns)
3. [Hook Chain Examples](#3-hook-chain-examples)
4. [Collaborative Hook Patterns](#4-collaborative-hook-patterns)
5. [MCP Integration Examples](#5-mcp-integration-examples)
6. [Configuration Templates](#6-configuration-templates)
7. [Best Practices](#7-best-practices)
8. [Performance & Error Handling](#8-performance--error-handling)

---

## 1. Composite Hook Workflows

### 1.1 PreCommit Quality Pipeline

**Multi-stage validation before commits.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(git commit)": [
        {
          "command": "bash -c '\n            set -e\n            echo \"[1/4] Running code formatters...\"\n            bun run format:check || { echo \"❌ Formatting failed\"; exit 1; }\n            \n            echo \"[2/4] Running linters...\"\n            bun run lint || { echo \"❌ Linting failed\"; exit 1; }\n            \n            echo \"[3/4] Running security scan...\"\n            trivy fs --severity HIGH,CRITICAL . || { echo \"❌ Security vulnerabilities found\"; exit 1; }\n            \n            echo \"[4/4] Checking coverage...\"\n            python3 .github/scripts/check-coverage-regression.py || { echo \"❌ Coverage regression detected\"; exit 1; }\n            \n            echo \"✅ All pre-commit checks passed\"\n          '",
          "description": "PreCommit quality pipeline: format → lint → security → coverage"
        }
      ]
    }
  }
}
```

**Features:**
- Sequential execution with `set -e` (fail-fast)
- Clear progress indicators (1/4, 2/4, etc.)
- Actionable error messages
- Exit codes propagate failures

---

### 1.2 PostDeploy Validation Pipeline

**Automated smoke tests and rollback logic.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Bash(git push origin main)": [
        {
          "command": "bash -c '\n            DEPLOY_URL=\"https://staging.example.com\"\n            \n            echo \"[1/3] Waiting for deployment...\"\n            sleep 30\n            \n            echo \"[2/3] Running smoke tests...\"\n            curl -f \"$DEPLOY_URL/health\" || { \n              echo \"❌ Health check failed - initiating rollback\"\n              git revert HEAD --no-edit\n              git push origin main --force-with-lease\n              exit 1\n            }\n            \n            echo \"[3/3] Checking metrics...\"\n            python3 scripts/check-metrics.py --baseline main~1 --current HEAD || {\n              echo \"⚠️ Performance degradation detected - review required\"\n              exit 2  # Warning, not failure\n            }\n            \n            echo \"✅ Deployment validated\"\n          '",
          "async": true,
          "description": "PostDeploy validation with automatic rollback"
        }
      ]
    }
  }
}
```

**Features:**
- Async execution (`async: true`) - doesn't block Claude
- Automatic rollback on smoke test failure
- Non-blocking warnings (exit 2) vs hard failures (exit 1)
- Real deployment URL health checks

---

### 1.3 OnError Recovery Pipeline

**Auto-fix attempts with escalation.**

```json
{
  "hooks": {
    "PostToolUseFailure": {
      "Bash(bun test)": [
        {
          "command": "bash -c '\n            FAILURE_LOG=\".test-failures.log\"\n            echo \"$TOOL_RESULT\" > \"$FAILURE_LOG\"\n            \n            echo \"[1/3] Analyzing test failures...\"\n            FLAKY=$(grep -c \"Timeout\" \"$FAILURE_LOG\" || echo 0)\n            \n            if [ \"$FLAKY\" -gt 0 ]; then\n              echo \"[2/3] Detected $FLAKY flaky tests - retrying with increased timeout...\"\n              VITEST_TIMEOUT=30000 bun test --retry=2 && {\n                echo \"✅ Tests passed on retry\"\n                rm \"$FAILURE_LOG\"\n                exit 0\n              }\n            fi\n            \n            echo \"[3/3] Logging failure details...\"\n            cat \"$FAILURE_LOG\" | tee -a .persistent-test-failures.log\n            echo \"❌ Auto-fix failed - manual intervention required\"\n            exit 1\n          '",
          "description": "Auto-retry flaky tests, log persistent failures"
        }
      ]
    }
  }
}
```

**Features:**
- Failure log capture (`$TOOL_RESULT`)
- Pattern detection (timeouts → flaky tests)
- Intelligent retry with adjusted parameters
- Persistent logging for manual review

---

### 1.4 Multi-Language Validation Pipeline

**Coordinated checks across Go, Python, TypeScript.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(git commit)": [
        {
          "command": "bash -c '\n            FILES_CHANGED=$(git diff --cached --name-only)\n            \n            # Go validation\n            if echo \"$FILES_CHANGED\" | grep -q \"\\.go$\"; then\n              echo \"[Go] Running go vet...\"\n              go vet ./... || exit 1\n              echo \"[Go] Running staticcheck...\"\n              staticcheck ./... || exit 1\n            fi\n            \n            # Python validation\n            if echo \"$FILES_CHANGED\" | grep -q \"\\.py$\"; then\n              echo \"[Python] Running mypy...\"\n              mypy . --ignore-missing-imports || exit 1\n              echo \"[Python] Running ruff...\"\n              ruff check . || exit 1\n            fi\n            \n            # TypeScript validation\n            if echo \"$FILES_CHANGED\" | grep -q \"\\.tsx\\?$\"; then\n              echo \"[TypeScript] Running type checks...\"\n              bun run type-check || exit 1\n              echo \"[TypeScript] Running ESLint...\"\n              bun run lint:check || exit 1\n            fi\n            \n            echo \"✅ Multi-language validation passed\"\n          '",
          "description": "Language-aware pre-commit validation"
        }
      ]
    }
  }
}
```

**Features:**
- Dynamic language detection via `git diff --cached --name-only`
- Conditional execution (only validate changed languages)
- Zero-config (auto-detects file extensions)

---

### 1.5 Documentation Sync Pipeline

**Keep code and docs in sync.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Edit": [
        {
          "command": "bash -c '\n            FILE=\"$TOOL_INPUT_FILE_PATH\"\n            \n            # Check if file has JSDoc/docstrings\n            if grep -qE \"(^\\s*\\/\\*\\*|^\\s*\\\"\\\"\\\")\" \"$FILE\"; then\n              echo \"[1/2] Detected documentation in $FILE\"\n              \n              # Extract and update API reference\n              case \"$FILE\" in\n                *.ts|*.tsx)\n                  bun run typedoc --plugin none --tsconfig tsconfig.json \"$FILE\"\n                  ;;\n                *.py)\n                  pdoc \"$FILE\" --output-dir docs/api/python\n                  ;;\n              esac\n              \n              echo \"[2/2] Auto-generated API docs updated\"\n              git add docs/api/\n            fi\n          '",
          "async": true,
          "description": "Auto-generate API docs from code comments"
        }
      ]
    }
  }
}
```

**Features:**
- Automatic documentation generation on code edits
- Language-specific tooling (TypeDoc for TS, pdoc for Python)
- Auto-stage generated docs
- Async execution (non-blocking)

---

### 1.6 Database Migration Safety Pipeline

**Prevent dangerous schema changes.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(migrate)": [
        {
          "command": "bash -c '\n            MIGRATION_FILE=$(find migrations -name \"*.sql\" -newer .last-migration-check 2>/dev/null | head -1)\n            \n            if [ -z \"$MIGRATION_FILE\" ]; then\n              echo \"✅ No new migrations detected\"\n              exit 0\n            fi\n            \n            echo \"[1/3] Analyzing migration: $MIGRATION_FILE\"\n            \n            # Check for destructive operations\n            DESTRUCTIVE=$(grep -iE \"DROP (TABLE|COLUMN)|ALTER.*DROP|TRUNCATE\" \"$MIGRATION_FILE\")\n            if [ -n \"$DESTRUCTIVE\" ]; then\n              echo \"⚠️ DESTRUCTIVE OPERATION DETECTED:\"\n              echo \"$DESTRUCTIVE\"\n              read -p \"Type CONFIRM to proceed: \" CONFIRM\n              [ \"$CONFIRM\" = \"CONFIRM\" ] || exit 1\n            fi\n            \n            echo \"[2/3] Running dry-run...\"\n            psql \"$DATABASE_URL\" --dry-run -f \"$MIGRATION_FILE\" || exit 1\n            \n            echo \"[3/3] Creating backup...\"\n            pg_dump \"$DATABASE_URL\" > \"backups/pre-migration-$(date +%s).sql\"\n            touch .last-migration-check\n            \n            echo \"✅ Migration safety checks passed\"\n          '",
          "description": "Database migration safety: detect destructive ops + backup"
        }
      ]
    }
  }
}
```

**Features:**
- Destructive operation detection (DROP, TRUNCATE)
- Interactive confirmation for dangerous changes
- Dry-run validation
- Automatic backup creation

---

### 1.7 Dependency Audit Pipeline

**Security and license compliance checks.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Bash(bun add)": [
        {
          "command": "bash -c '\n            echo \"[1/3] Running security audit...\"\n            bun audit || {\n              echo \"❌ Security vulnerabilities found in dependencies\"\n              exit 1\n            }\n            \n            echo \"[2/3] Checking license compliance...\"\n            npx license-checker --production --failOn \"GPL;AGPL\" || {\n              echo \"❌ Non-compliant licenses detected\"\n              exit 1\n            }\n            \n            echo \"[3/3] Updating dependency graph...\"\n            bun run madge --circular --extensions ts,tsx src/ || {\n              echo \"⚠️ Circular dependencies detected - review required\"\n              exit 2\n            }\n            \n            echo \"✅ Dependency audit passed\"\n          '",
          "async": true,
          "description": "Security + license + circular dependency checks"
        }
      ]
    }
  }
}
```

**Features:**
- Automatic security audits on dependency changes
- License compliance validation
- Circular dependency detection
- Warning-level (exit 2) for non-blocking issues

---

### 1.8 Performance Budget Enforcement

**Prevent bundle size regressions.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Bash(bun build)": [
        {
          "command": "bash -c '\n            echo \"[1/2] Analyzing bundle size...\"\n            \n            BUNDLE_SIZE=$(stat -f%z dist/main.js)\n            MAX_SIZE=$((2 * 1024 * 1024))  # 2MB limit\n            \n            if [ \"$BUNDLE_SIZE\" -gt \"$MAX_SIZE\" ]; then\n              echo \"❌ Bundle size exceeded: $(numfmt --to=iec $BUNDLE_SIZE) > 2MB\"\n              echo \"[2/2] Analyzing largest chunks...\"\n              bun run esbuild-visualizer --stat-size dist/main.js\n              exit 1\n            fi\n            \n            echo \"✅ Bundle size OK: $(numfmt --to=iec $BUNDLE_SIZE)\"\n          '",
          "description": "Enforce 2MB bundle size budget"
        }
      ]
    }
  }
}
```

**Features:**
- Hard size limits
- Human-readable size formatting
- Automatic chunk analysis on failure
- Fast (no network calls)

---

### 1.9 Environment Validation Pipeline

**Ensure required services are running.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(make dev)": [
        {
          "command": "bash -c '\n            echo \"[1/4] Checking PostgreSQL...\"\n            pg_isready -h localhost -p 5432 || {\n              echo \"❌ PostgreSQL not running - start with: brew services start postgresql\"\n              exit 1\n            }\n            \n            echo \"[2/4] Checking Redis...\"\n            redis-cli ping > /dev/null 2>&1 || {\n              echo \"❌ Redis not running - start with: brew services start redis\"\n              exit 1\n            }\n            \n            echo \"[3/4] Checking Node version...\"\n            NODE_VERSION=$(node -v | cut -d. -f1 | tr -d v)\n            [ \"$NODE_VERSION\" -ge 20 ] || {\n              echo \"❌ Node 20+ required (found: $(node -v))\"\n              exit 1\n            }\n            \n            echo \"[4/4] Checking environment variables...\"\n            [ -n \"$DATABASE_URL\" ] || {\n              echo \"❌ DATABASE_URL not set - copy .env.example to .env\"\n              exit 1\n            }\n            \n            echo \"✅ Environment validation passed\"\n          '",
          "description": "Validate dev environment before starting services"
        }
      ]
    }
  }
}
```

**Features:**
- Service availability checks (PostgreSQL, Redis)
- Version validation (Node 20+)
- Environment variable validation
- Actionable error messages

---

### 1.10 Code Complexity Gates

**Prevent complex functions from entering codebase.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Edit": [
        {
          "command": "bash -c '\n            FILE=\"$TOOL_INPUT_FILE_PATH\"\n            \n            case \"$FILE\" in\n              *.py)\n                COMPLEXITY=$(radon cc \"$FILE\" -a -s | grep \"Average complexity\" | awk '\''{print $NF}'\'')\n                if (( $(echo \"$COMPLEXITY > 10\" | bc -l) )); then\n                  echo \"❌ Cyclomatic complexity too high: $COMPLEXITY (max: 10)\"\n                  radon cc \"$FILE\" -s\n                  exit 1\n                fi\n                ;;\n              *.ts|*.tsx)\n                COMPLEXITY=$(bun run complexity-report \"$FILE\" --format json | jq '.aggregate.cyclomatic')\n                if [ \"$COMPLEXITY\" -gt 10 ]; then\n                  echo \"❌ Cyclomatic complexity too high: $COMPLEXITY (max: 10)\"\n                  exit 1\n                fi\n                ;;\n            esac\n            \n            echo \"✅ Complexity checks passed\"\n          '",
          "description": "Enforce max cyclomatic complexity of 10"
        }
      ]
    }
  }
}
```

**Features:**
- Language-specific complexity tools (radon for Python, complexity-report for TS)
- Hard complexity limits
- Detailed reporting on failure

---

## 2. Conditional Hook Patterns

### 2.1 Branch-Aware Execution

**Different rules for main vs feature branches.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(git push)": [
        {
          "command": "bash -c '\n            BRANCH=$(git rev-parse --abbrev-ref HEAD)\n            \n            if [ \"$BRANCH\" = \"main\" ] || [ \"$BRANCH\" = \"master\" ]; then\n              echo \"[MAIN BRANCH] Running full validation suite...\"\n              \n              # Expensive checks only on main\n              bun test --coverage --run || exit 1\n              go test -race ./... || exit 1\n              pytest --cov --cov-fail-under=90 || exit 1\n              \n              # Require linear history\n              git log --oneline --graph --all | grep -q \"Merge\" && {\n                echo \"❌ Merge commits not allowed on main - use rebase\"\n                exit 1\n              }\n            else\n              echo \"[FEATURE BRANCH] Running fast checks...\"\n              \n              # Fast checks on feature branches\n              bun run lint:check || exit 1\n              go vet ./... || exit 1\n            fi\n            \n            echo \"✅ Branch-specific checks passed\"\n          '",
          "description": "Expensive checks on main, fast checks on feature branches"
        }
      ]
    }
  }
}
```

**Features:**
- Branch detection via `git rev-parse --abbrev-ref HEAD`
- Conditional test coverage enforcement (main only)
- Linear history enforcement (main only)
- Fast feedback on feature branches

---

### 2.2 File Type Conditional Execution

**Different linters per file type.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Edit": [
        {
          "command": "bash -c '\n            FILE=\"$TOOL_INPUT_FILE_PATH\"\n            \n            case \"$FILE\" in\n              *.py)\n                echo \"[Python] Running ruff...\"\n                ruff check \"$FILE\" || exit 1\n                ;;\n              *.ts|*.tsx)\n                echo \"[TypeScript] Running ESLint...\"\n                bunx eslint \"$FILE\" || exit 1\n                ;;\n              *.go)\n                echo \"[Go] Running golangci-lint...\"\n                golangci-lint run \"$FILE\" || exit 1\n                ;;\n              *.md)\n                echo \"[Markdown] Running markdownlint...\"\n                markdownlint \"$FILE\" || exit 1\n                ;;\n              *.sql)\n                echo \"[SQL] Running sqlfluff...\"\n                sqlfluff lint \"$FILE\" || exit 1\n                ;;\n              *)\n                echo \"ℹ️ No linter configured for: $FILE\"\n                ;;\n            esac\n          '",
          "description": "File-type-aware linting"
        }
      ]
    }
  }
}
```

**Features:**
- Extension-based routing
- Language-specific linters
- Graceful fallback for unknown types

---

### 2.3 Time-Based Execution

**Different behavior during work hours vs off-hours.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(git push)": [
        {
          "command": "bash -c '\n            HOUR=$(date +%H)\n            DAY=$(date +%u)  # 1=Monday, 7=Sunday\n            \n            # Block deployments outside business hours (9am-5pm, Mon-Fri)\n            if [ \"$DAY\" -ge 6 ] || [ \"$HOUR\" -lt 9 ] || [ \"$HOUR\" -ge 17 ]; then\n              BRANCH=$(git rev-parse --abbrev-ref HEAD)\n              if [ \"$BRANCH\" = \"main\" ]; then\n                echo \"⚠️ Pushing to main outside business hours (9am-5pm Mon-Fri)\"\n                read -p \"Type EMERGENCY to override: \" OVERRIDE\n                [ \"$OVERRIDE\" = \"EMERGENCY\" ] || exit 1\n              fi\n            fi\n            \n            echo \"✅ Time-based validation passed\"\n          '",
          "description": "Prevent off-hours production deployments"
        }
      ]
    }
  }
}
```

**Features:**
- Business hours detection
- Emergency override mechanism
- Prevents accidental off-hours deployments

---

### 2.4 User-Specific Hooks

**Different rules per developer.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(git commit)": [
        {
          "command": "bash -c '\n            GIT_USER=$(git config user.email)\n            \n            # Junior devs require peer review flag\n            if echo \"$GIT_USER\" | grep -q \"junior\\|intern\"; then\n              COMMIT_MSG=$(git log -1 --pretty=%B)\n              if ! echo \"$COMMIT_MSG\" | grep -q \"Reviewed-by:\"; then\n                echo \"❌ Junior developers must include Reviewed-by: tag\"\n                exit 1\n              fi\n            fi\n            \n            # Security team must sign commits\n            if echo \"$GIT_USER\" | grep -q \"security@\"; then\n              git verify-commit HEAD || {\n                echo \"❌ Security team commits must be GPG-signed\"\n                exit 1\n              }\n            fi\n            \n            echo \"✅ User-specific validation passed\"\n          '",
          "description": "Role-based commit requirements"
        }
      ]
    }
  }
}
```

**Features:**
- Email-based role detection
- Custom requirements per role
- Enforces organizational policies

---

### 2.5 Monorepo Path-Based Execution

**Run checks only for affected packages.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(git commit)": [
        {
          "command": "bash -c '\n            FILES_CHANGED=$(git diff --cached --name-only)\n            \n            # Frontend changes\n            if echo \"$FILES_CHANGED\" | grep -q \"^frontend/\"; then\n              echo \"[Frontend] Running tests...\"\n              bun test frontend/ || exit 1\n            fi\n            \n            # Backend changes\n            if echo \"$FILES_CHANGED\" | grep -q \"^backend/\"; then\n              echo \"[Backend] Running tests...\"\n              go test ./backend/... || exit 1\n            fi\n            \n            # Shared changes\n            if echo \"$FILES_CHANGED\" | grep -q \"^shared/\"; then\n              echo \"[Shared] Running full test suite...\"\n              bun test && go test ./... || exit 1\n            fi\n            \n            echo \"✅ Path-based validation passed\"\n          '",
          "description": "Test only affected monorepo packages"
        }
      ]
    }
  }
}
```

**Features:**
- Path-based change detection
- Isolated package testing
- Full suite for shared code changes

---

### 2.6 Documentation-Only Changes

**Skip tests for docs-only commits.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(git commit)": [
        {
          "command": "bash -c '\n            FILES_CHANGED=$(git diff --cached --name-only)\n            \n            # Check if all changes are documentation\n            NON_DOC_FILES=$(echo \"$FILES_CHANGED\" | grep -vE \"\\.(md|txt|rst)$|^docs/\")\n            \n            if [ -z \"$NON_DOC_FILES\" ]; then\n              echo \"ℹ️ Documentation-only changes detected - skipping tests\"\n              exit 0\n            fi\n            \n            echo \"[Code Changes] Running full validation...\"\n            bun test || exit 1\n            \n            echo \"✅ Validation passed\"\n          '",
          "description": "Skip expensive checks for documentation-only commits"
        }
      ]
    }
  }
}
```

**Features:**
- Documentation file detection
- Fast-path for docs-only changes
- Full validation for code changes

---

### 2.7 Dependency Version Conditionals

**Different checks based on Node/Go versions.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(make dev)": [
        {
          "command": "bash -c '\n            NODE_VERSION=$(node -v | cut -d. -f1 | tr -d v)\n            GO_VERSION=$(go version | awk '\''{print $3}'\'' | cut -d. -f2)\n            \n            # Node 22+ has native test runner\n            if [ \"$NODE_VERSION\" -ge 22 ]; then\n              echo \"[Node 22+] Using native test runner...\"\n              node --test\n            else\n              echo \"[Node <22] Using vitest...\"\n              bun test\n            fi\n            \n            # Go 1.21+ has improved fuzzing\n            if [ \"$GO_VERSION\" -ge 21 ]; then\n              echo \"[Go 1.21+] Running fuzz tests...\"\n              go test -fuzz=. -fuzztime=30s ./...\n            fi\n            \n            echo \"✅ Version-aware tests passed\"\n          '",
          "description": "Adapt tests to runtime versions"
        }
      ]
    }
  }
}
```

**Features:**
- Version detection
- Conditional tool selection
- Backward compatibility

---

### 2.8 CI vs Local Environment Detection

**Different behavior in CI vs local dev.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(bun test)": [
        {
          "command": "bash -c '\n            if [ -n \"$CI\" ]; then\n              echo \"[CI] Running with full coverage...\"\n              bun test --coverage --run --reporter=json > test-results.json\n              bun run codecov --file=coverage/coverage-final.json\n            else\n              echo \"[Local] Running with watch mode...\"\n              bun test --watch --coverage=false\n            fi\n          '",
          "description": "CI: coverage + reporting | Local: watch mode"
        }
      ]
    }
  }
}
```

**Features:**
- `$CI` environment variable detection
- Different UX for CI vs local
- Coverage reporting in CI only

---

## 3. Hook Chain Examples

### 3.1 Coverage Regression → Test Generation Chain

**Hook output feeds next hook.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Bash(bun test --coverage)": [
        {
          "command": "bash -c '\n            echo \"[Chain 1/3] Detecting coverage regressions...\"\n            python3 scripts/detect-coverage-regression.py > /tmp/uncovered-files.txt\n            \n            if [ -s /tmp/uncovered-files.txt ]; then\n              echo \"[Chain 2/3] Generating test stubs for uncovered code...\"\n              while read -r FILE; do\n                bun run test-stub-generator \"$FILE\" > \"${FILE%.ts}.test.ts\"\n              done < /tmp/uncovered-files.txt\n              \n              echo \"[Chain 3/3] Creating PR for test stubs...\"\n              git checkout -b \"auto-test-stubs-$(date +%s)\"\n              git add \"**/*.test.ts\"\n              git commit -m \"chore: auto-generated test stubs for uncovered code\"\n              gh pr create --title \"Auto-generated test stubs\" --body \"Coverage regression detected. Stubs created for:\n$(cat /tmp/uncovered-files.txt)\"\n            fi\n            \n            echo \"✅ Coverage regression chain complete\"\n          '",
          "async": true,
          "description": "Coverage regression → test stub generation → PR creation"
        }
      ]
    }
  }
}
```

**Features:**
- 3-stage pipeline: detect → generate → PR
- Automatic branch creation
- Async execution (non-blocking)
- PR with detailed context

---

### 3.2 Complexity Detection → Refactoring Ticket Chain

**Auto-create Linear tickets for complex code.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Edit": [
        {
          "command": "bash -c '\n            FILE=\"$TOOL_INPUT_FILE_PATH\"\n            \n            echo \"[Chain 1/3] Analyzing complexity...\"\n            COMPLEX_FUNCTIONS=$(radon cc \"$FILE\" -s -n C | grep -E \"^[A-Z]\") || true\n            \n            if [ -n \"$COMPLEX_FUNCTIONS\" ]; then\n              echo \"[Chain 2/3] Complex functions detected:\"\n              echo \"$COMPLEX_FUNCTIONS\"\n              \n              echo \"[Chain 3/3] Creating Linear ticket...\"\n              linear issue create \\\n                --title \"Refactor complex functions in $FILE\" \\\n                --description \"Complexity analysis detected functions requiring refactoring:\n\n\\`\\`\\`\n$COMPLEX_FUNCTIONS\n\\`\\`\\`\n\nTarget: Reduce complexity to <= 10\" \\\n                --priority 2 \\\n                --label \"tech-debt\" \\\n                --label \"auto-created\"\n            fi\n            \n            echo \"✅ Complexity chain complete\"\n          '",
          "async": true,
          "description": "Complexity detection → Linear ticket creation"
        }
      ]
    }
  }
}
```

**Features:**
- Automatic ticket creation
- Formatted ticket description
- Priority and labels
- Async execution

---

### 3.3 Performance Regression → Profiling → Optimization PR Chain

**End-to-end performance fix automation.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Bash(bun test benchmark)": [
        {
          "command": "bash -c '\n            echo \"[Chain 1/4] Detecting performance regressions...\"\n            python3 scripts/benchmark-regression.py > /tmp/slow-functions.json\n            \n            if [ -s /tmp/slow-functions.json ]; then\n              echo \"[Chain 2/4] Profiling slow functions...\"\n              SLOWEST=$(jq -r '\''.functions[0].name'\'' /tmp/slow-functions.json)\n              node --cpu-prof --cpu-prof-dir=/tmp/profiles node_modules/.bin/vitest run --testNamePattern=\"$SLOWEST\"\n              \n              echo \"[Chain 3/4] Analyzing profile...\"\n              HOTSPOT=$(node scripts/analyze-cpu-profile.js /tmp/profiles/*.cpuprofile | head -1)\n              \n              echo \"[Chain 4/4] Creating optimization PR...\"\n              git checkout -b \"perf-fix-$(date +%s)\"\n              echo \"# Performance Optimization\n\n## Regression Detected\n\\`\\`\\`json\n$(cat /tmp/slow-functions.json)\n\\`\\`\\`\n\n## Hotspot\n$HOTSPOT\n\nTODO: Optimize this code path.\" > OPTIMIZATION.md\n              git add OPTIMIZATION.md\n              git commit -m \"perf: add optimization analysis\"\n              gh pr create --title \"Fix performance regression in $SLOWEST\" --body \"$(cat OPTIMIZATION.md)\"\n            fi\n            \n            echo \"✅ Performance chain complete\"\n          '",
          "async": true,
          "description": "Benchmark → profile → analyze → PR"
        }
      ]
    }
  }
}
```

**Features:**
- 4-stage automated workflow
- CPU profiling integration
- Hotspot analysis
- PR with detailed profiling data

---

### 3.4 Security Scan → Patch Generation → Auto-Merge Chain

**Automated security fixes.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Bash(trivy fs)": [
        {
          "command": "bash -c '\n            echo \"[Chain 1/3] Scanning for vulnerabilities...\"\n            trivy fs --severity HIGH,CRITICAL --format json . > /tmp/vulns.json\n            \n            VULN_COUNT=$(jq '.Results[].Vulnerabilities | length' /tmp/vulns.json | awk '{s+=$1} END {print s}')\n            \n            if [ \"$VULN_COUNT\" -gt 0 ]; then\n              echo \"[Chain 2/3] Attempting auto-fix...\"\n              \n              # Try automated patch\n              trivy image --severity HIGH,CRITICAL --ignore-unfixed --format json . | \\\n                jq -r '.Results[].Vulnerabilities[] | select(.FixedVersion != \"\") | \"\\(.PkgName) \\(.FixedVersion)\"' | \\\n                while read -r PKG VERSION; do\n                  bun add \"$PKG@$VERSION\"\n                done\n              \n              echo \"[Chain 3/3] Creating auto-fix PR...\"\n              git checkout -b \"security-fix-$(date +%s)\"\n              git add package.json bun.lockb\n              git commit -m \"security: auto-fix HIGH/CRITICAL vulnerabilities\"\n              gh pr create --title \"🔒 Security: Auto-fix vulnerabilities\" --body \"Auto-generated security patch.\n\nFixed vulnerabilities:\n\\`\\`\\`json\n$(cat /tmp/vulns.json)\n\\`\\`\\`\" --label \"security\" --label \"automerge\"\n            fi\n            \n            echo \"✅ Security chain complete\"\n          '",
          "async": true,
          "description": "Security scan → auto-patch → PR with automerge label"
        }
      ]
    }
  }
}
```

**Features:**
- Trivy vulnerability scanning
- Automated dependency updates
- Auto-merge label for CI
- Detailed vulnerability reporting

---

### 3.5 Test Failure → Bisect → Blame → Notify Chain

**Find and notify author of breaking commit.**

```json
{
  "hooks": {
    "PostToolUseFailure": {
      "Bash(bun test)": [
        {
          "command": "bash -c '\n            echo \"[Chain 1/4] Test failure detected\"\n            \n            echo \"[Chain 2/4] Running git bisect to find breaking commit...\"\n            git bisect start\n            git bisect bad HEAD\n            git bisect good main~10\n            git bisect run bun test --run\n            BREAKING_COMMIT=$(git bisect log | grep \"is the first bad commit\" -B 1 | head -1 | awk '\''{print $1}'\'')\n            git bisect reset\n            \n            echo \"[Chain 3/4] Finding commit author...\"\n            AUTHOR=$(git show -s --format=\"%ae\" \"$BREAKING_COMMIT\")\n            COMMIT_MSG=$(git show -s --format=\"%s\" \"$BREAKING_COMMIT\")\n            \n            echo \"[Chain 4/4] Notifying author via Slack...\"\n            curl -X POST \"$SLACK_WEBHOOK_URL\" -H \"Content-Type: application/json\" -d \"{\n              \\\"text\\\": \\\"⚠️ Test failure in commit $BREAKING_COMMIT by $AUTHOR\\\",\n              \\\"blocks\\\": [{\n                \\\"type\\\": \\\"section\\\",\n                \\\"text\\\": {\n                  \\\"type\\\": \\\"mrkdwn\\\",\n                  \\\"text\\\": \\\"Commit: *$COMMIT_MSG*\\\\nAuthor: $AUTHOR\\\\nPlease fix ASAP.\\\"\n                }\n              }]\n            }\"\n            \n            echo \"✅ Bisect chain complete\"\n          '",
          "async": true,
          "description": "Test fail → git bisect → find author → Slack notify"
        }
      ]
    }
  }
}
```

**Features:**
- Automatic git bisect
- Author identification
- Slack notification with context
- Async execution

---

### 3.6 Bundle Analysis → Lazy Loading Suggestions → PR Chain

**Auto-suggest code splitting opportunities.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Bash(bun build)": [
        {
          "command": "bash -c '\n            echo \"[Chain 1/3] Analyzing bundle...\"\n            bun run esbuild-visualizer --stat-size dist/main.js --format json > /tmp/bundle-stats.json\n            \n            echo \"[Chain 2/3] Finding large modules...\"\n            LARGE_MODULES=$(jq -r '.modules[] | select(.size > 100000) | .name' /tmp/bundle-stats.json)\n            \n            if [ -n \"$LARGE_MODULES\" ]; then\n              echo \"[Chain 3/3] Generating lazy loading suggestions...\"\n              echo \"# Bundle Optimization Opportunities\n\n## Large Modules (>100KB)\n\\`\\`\\`\n$LARGE_MODULES\n\\`\\`\\`\n\n## Suggested Lazy Loading\n\" > LAZY_LOADING_SUGGESTIONS.md\n              \n              echo \"$LARGE_MODULES\" | while read -r MODULE; do\n                echo \"- \\`import('$MODULE')\\` instead of \\`import ... from '$MODULE'\\`\" >> LAZY_LOADING_SUGGESTIONS.md\n              done\n              \n              git checkout -b \"optimize-bundle-$(date +%s)\"\n              git add LAZY_LOADING_SUGGESTIONS.md\n              git commit -m \"docs: add bundle optimization suggestions\"\n              gh pr create --title \"Bundle optimization opportunities\" --body \"$(cat LAZY_LOADING_SUGGESTIONS.md)\"\n            fi\n            \n            echo \"✅ Bundle analysis chain complete\"\n          '",
          "async": true,
          "description": "Bundle analyze → suggest lazy loading → PR"
        }
      ]
    }
  }
}
```

**Features:**
- Bundle size analysis
- Automatic suggestion generation
- Markdown documentation
- PR creation with recommendations

---

## 4. Collaborative Hook Patterns

### 4.1 Failed Test → Debugging Agent Chain

**Hook spawns agent for auto-fix.**

```json
{
  "hooks": {
    "PostToolUseFailure": {
      "Bash(bun test)": [
        {
          "command": "bash -c '\n            echo \"[1/2] Test failure detected - spawning debugging agent...\"\n            \n            TEST_OUTPUT=\"$TOOL_RESULT\"\n            FAILED_TEST=$(echo \"$TEST_OUTPUT\" | grep -oE \"Test failed: .*\" | head -1)\n            \n            # Create task for debugging agent\n            echo \"{\n              \\\"type\\\": \\\"debug_test_failure\\\",\n              \\\"test\\\": \\\"$FAILED_TEST\\\",\n              \\\"output\\\": $(echo \"$TEST_OUTPUT\" | jq -Rs .),\n              \\\"timestamp\\\": $(date +%s)\n            }\" > /tmp/debug-task.json\n            \n            echo \"[2/2] Agent task created: /tmp/debug-task.json\"\n            echo \"ℹ️ Run: claude-code task create --file /tmp/debug-task.json\"\n            \n            # Could integrate with Task API here\n            # curl -X POST localhost:8080/api/tasks -d @/tmp/debug-task.json\n          '",
          "description": "Spawn debugging agent on test failure"
        }
      ]
    }
  }
}
```

**Features:**
- Structured task creation
- Agent delegation pattern
- Can integrate with Task API
- Async debugging workflow

---

### 4.2 Security Issue → Security Agent → Patch Generation

**Delegate security fixes to specialized agent.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Bash(trivy fs)": [
        {
          "command": "bash -c '\n            VULNS=$(trivy fs --severity HIGH,CRITICAL --format json . | jq -r '.Results[].Vulnerabilities | length' | awk '{s+=$1} END {print s}')\n            \n            if [ \"$VULNS\" -gt 0 ]; then\n              echo \"[1/2] Security vulnerabilities found - delegating to security agent...\"\n              \n              # Create security agent task\n              cat > /tmp/security-task.json <<EOF\n{\n  \"agent\": \"security-specialist\",\n  \"task\": \"fix_vulnerabilities\",\n  \"context\": {\n    \"scan_results\": $(trivy fs --severity HIGH,CRITICAL --format json .),\n    \"priority\": \"HIGH\",\n    \"auto_pr\": true\n  }\n}\nEOF\n              \n              echo \"[2/2] Security agent task queued\"\n              # Integration point: spawn agent via Task API\n              # claude-code spawn security-specialist --task /tmp/security-task.json\n            fi\n          '",
          "async": true,
          "description": "Delegate security fixes to specialist agent"
        }
      ]
    }
  }
}
```

**Features:**
- Agent specialization
- Structured task delegation
- Auto-PR capability
- High-priority flagging

---

### 4.3 Performance Regression → Profiling Agent → Optimization

**Multi-agent performance workflow.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Bash(bun test benchmark)": [
        {
          "command": "bash -c '\n            REGRESSION=$(python3 scripts/benchmark-regression.py | jq -r '.regression_detected')\n            \n            if [ \"$REGRESSION\" = \"true\" ]; then\n              echo \"[Agent Delegation] Spawning profiling agent...\"\n              \n              cat > /tmp/profiling-task.json <<EOF\n{\n  \"agent\": \"performance-optimizer\",\n  \"workflow\": [\n    {\"step\": \"profile\", \"target\": \"slow_functions\"},\n    {\"step\": \"analyze\", \"tool\": \"flamegraph\"},\n    {\"step\": \"optimize\", \"strategy\": \"auto\"},\n    {\"step\": \"benchmark\", \"threshold\": \"10%_improvement\"},\n    {\"step\": \"pr\", \"auto_merge\": false}\n  ],\n  \"context\": $(cat /tmp/benchmark-results.json)\n}\nEOF\n              \n              echo \"ℹ️ Profiling agent will handle optimization\"\n            fi\n          '",
          "async": true,
          "description": "Multi-step profiling workflow via agent"
        }
      ]
    }
  }
}
```

**Features:**
- Multi-step workflow definition
- Agent orchestration
- Automated optimization
- Benchmark validation

---

### 4.4 Code Review → Review Agent → Feedback Loop

**Automated code review via agent.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(gh pr create)": [
        {
          "command": "bash -c '\n            echo \"[1/2] PR creation detected - spawning review agent...\"\n            \n            # Get changed files\n            FILES=$(git diff main...HEAD --name-only)\n            \n            cat > /tmp/review-task.json <<EOF\n{\n  \"agent\": \"code-reviewer\",\n  \"review_type\": \"pre_pr\",\n  \"files\": $(echo \"$FILES\" | jq -R . | jq -s .),\n  \"checklist\": [\n    \"security_vulnerabilities\",\n    \"code_complexity\",\n    \"test_coverage\",\n    \"documentation\",\n    \"breaking_changes\"\n  ],\n  \"auto_comment\": true\n}\nEOF\n              \n              echo \"[2/2] Review agent will analyze changes before PR\"\n              # Integration: claude-code spawn code-reviewer --blocking --task /tmp/review-task.json\n            fi\n          '",
          "description": "Automated code review before PR creation"
        }
      ]
    }
  }
}
```

**Features:**
- Pre-PR validation
- Comprehensive checklist
- Auto-commenting on issues
- Blocking execution option

---

### 4.5 Deployment → Monitoring Agent → Auto-Rollback

**Post-deploy monitoring via agent.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Bash(git push origin main)": [
        {
          "command": "bash -c '\n            echo \"[Agent Spawn] Starting post-deploy monitoring agent...\"\n            \n            DEPLOY_SHA=$(git rev-parse HEAD)\n            \n            cat > /tmp/monitoring-task.json <<EOF\n{\n  \"agent\": \"deployment-monitor\",\n  \"deployment\": {\n    \"sha\": \"$DEPLOY_SHA\",\n    \"environment\": \"production\",\n    \"url\": \"https://app.example.com\"\n  },\n  \"monitoring\": {\n    \"duration_minutes\": 30,\n    \"metrics\": [\"error_rate\", \"latency_p95\", \"cpu_usage\"],\n    \"thresholds\": {\n      \"error_rate\": 0.01,\n      \"latency_p95\": 500,\n      \"cpu_usage\": 80\n    },\n    \"rollback_on_breach\": true\n  },\n  \"notifications\": {\n    \"slack_channel\": \"#deployments\",\n    \"pagerduty\": true\n  }\n}\nEOF\n              \n              echo \"ℹ️ Monitoring agent watching deployment for 30 minutes\"\n              # claude-code spawn deployment-monitor --async --task /tmp/monitoring-task.json\n            fi\n          '",
          "async": true,
          "description": "30-minute post-deploy monitoring with auto-rollback"
        }
      ]
    }
  }
}
```

**Features:**
- Long-running monitoring
- Automatic rollback on threshold breach
- Multi-channel notifications
- Async execution

---

## 5. MCP Integration Examples

### 5.1 Linear Issue Tracking Integration

**Auto-create Linear tickets from TODOs.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Edit": [
        {
          "command": "bash -c '\n            FILE=\"$TOOL_INPUT_FILE_PATH\"\n            \n            # Extract TODO comments\n            TODOS=$(grep -nE \"TODO:|FIXME:|XXX:\" \"$FILE\" || true)\n            \n            if [ -n \"$TODOS\" ]; then\n              echo \"[Linear Integration] Creating tickets for TODOs...\"\n              \n              echo \"$TODOS\" | while IFS=: read -r LINE_NUM TODO_TEXT; do\n                linear issue create \\\n                  --title \"$(echo $TODO_TEXT | sed 's/.*TODO://' | xargs)\" \\\n                  --description \"File: $FILE:$LINE_NUM\n\nContext:\n\\`\\`\\`\n$(sed -n \"$((LINE_NUM-2)),$((LINE_NUM+2))p\" \"$FILE\")\n\\`\\`\\`\" \\\n                  --priority 3 \\\n                  --label \"todo\" \\\n                  --label \"auto-created\"\n                  \n                echo \"  ✓ Created ticket for line $LINE_NUM\"\n              done\n            fi\n          '",
          "async": true,
          "description": "Auto-create Linear tickets from TODO comments"
        }
      ]
    }
  }
}
```

**Linear MCP Tools:**
- `linear issue create`
- `linear issue update`
- `linear issue search`

**Features:**
- TODO comment extraction
- Contextual ticket descriptions
- Automatic labeling
- File/line references

---

### 5.2 Slack Deployment Notifications

**Real-time deployment updates.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Bash(git push origin main)": [
        {
          "command": "bash -c '\n            COMMIT_SHA=$(git rev-parse HEAD)\n            COMMIT_MSG=$(git log -1 --pretty=%B)\n            AUTHOR=$(git log -1 --pretty=\"%an\")\n            \n            # Slack MCP integration\n            claude-mcp slack send-message \\\n              --channel \"#deployments\" \\\n              --message \"{\n                \\\"blocks\\\": [\n                  {\n                    \\\"type\\\": \\\"header\\\",\n                    \\\"text\\\": {\\\"type\\\": \\\"plain_text\\\", \\\"text\\\": \\\"🚀 Deployment to Production\\\"}\n                  },\n                  {\n                    \\\"type\\\": \\\"section\\\",\n                    \\\"fields\\\": [\n                      {\\\"type\\\": \\\"mrkdwn\\\", \\\"text\\\": \\\"*Commit:*\\\\n$COMMIT_SHA\\\"},\n                      {\\\"type\\\": \\\"mrkdwn\\\", \\\"text\\\": \\\"*Author:*\\\\n$AUTHOR\\\"},\n                      {\\\"type\\\": \\\"mrkdwn\\\", \\\"text\\\": \\\"*Message:*\\\\n$COMMIT_MSG\\\"},\n                      {\\\"type\\\": \\\"mrkdwn\\\", \\\"text\\\": \\\"*Status:*\\\\n🟡 Deploying...\\\"}\n                    ]\n                  }\n                ]\n              }\"\n            \n            echo \"✅ Slack notification sent\"\n          '",
          "async": true,
          "description": "Send formatted deployment notification to Slack"
        }
      ]
    }
  }
}
```

**Slack MCP Tools:**
- `slack send-message`
- `slack list-channels`
- `slack get-thread`

**Features:**
- Rich Block Kit formatting
- Real-time deployment tracking
- Multi-field metadata

---

### 5.3 GitHub PR Auto-Review

**Automated PR checks via GitHub MCP.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(gh pr create)": [
        {
          "command": "bash -c '\n            echo \"[GitHub MCP] Running PR pre-flight checks...\"\n            \n            # Get PR details\n            BASE_BRANCH=$(git rev-parse --abbrev-ref main)\n            HEAD_BRANCH=$(git rev-parse --abbrev-ref HEAD)\n            FILES_CHANGED=$(git diff $BASE_BRANCH...$HEAD_BRANCH --name-only)\n            \n            # Check for required files\n            MISSING_CHANGELOG=$(echo \"$FILES_CHANGED\" | grep -q CHANGELOG.md || echo \"missing\")\n            if [ \"$MISSING_CHANGELOG\" = \"missing\" ]; then\n              echo \"⚠️ CHANGELOG.md not updated\"\n            fi\n            \n            # Check PR size\n            LINES_CHANGED=$(git diff $BASE_BRANCH...$HEAD_BRANCH --stat | tail -1 | awk '\''{print $4}'\'')\n            if [ \"$LINES_CHANGED\" -gt 500 ]; then\n              echo \"⚠️ Large PR detected ($LINES_CHANGED lines) - consider splitting\"\n            fi\n            \n            # Auto-add labels via GitHub MCP\n            if echo \"$FILES_CHANGED\" | grep -q \"^frontend/\"; then\n              claude-mcp github add-label --label \"frontend\"\n            fi\n            \n            if echo \"$FILES_CHANGED\" | grep -q \"^backend/\"; then\n              claude-mcp github add-label --label \"backend\"\n            fi\n            \n            echo \"✅ GitHub MCP pre-flight checks complete\"\n          '",
          "description": "Auto-label PRs and warn about size/missing changelog"
        }
      ]
    }
  }
}
```

**GitHub MCP Tools:**
- `github add-label`
- `github request-review`
- `github get-pr-diff`

**Features:**
- Automatic labeling
- PR size warnings
- Changelog enforcement

---

### 5.4 Sentry Error Tracking Integration

**Auto-create Sentry issues from errors.**

```json
{
  "hooks": {
    "PostToolUseFailure": {
      "Bash(bun test)": [
        {
          "command": "bash -c '\n            ERROR_LOG=\"$TOOL_RESULT\"\n            \n            # Extract error details\n            ERROR_MESSAGE=$(echo \"$ERROR_LOG\" | grep -oE \"Error: .*\" | head -1)\n            STACK_TRACE=$(echo \"$ERROR_LOG\" | grep -A 10 \"Error:\")\n            \n            if [ -n \"$ERROR_MESSAGE\" ]; then\n              echo \"[Sentry MCP] Capturing error...\"\n              \n              claude-mcp sentry capture-exception \\\n                --message \"$ERROR_MESSAGE\" \\\n                --level \"error\" \\\n                --extra \"{\n                  \\\"context\\\": \\\"test_failure\\\",\n                  \\\"stack_trace\\\": $(echo \"$STACK_TRACE\" | jq -Rs .),\n                  \\\"git_sha\\\": \\\"$(git rev-parse HEAD)\\\",\n                  \\\"branch\\\": \\\"$(git rev-parse --abbrev-ref HEAD)\\\"\n                }\"\n              \n              echo \"✅ Error reported to Sentry\"\n            fi\n          '",
          "async": true,
          "description": "Capture test failures in Sentry"
        }
      ]
    }
  }
}
```

**Sentry MCP Tools:**
- `sentry capture-exception`
- `sentry create-issue`
- `sentry search-issues`

**Features:**
- Automatic error capture
- Rich context (git SHA, branch, stack trace)
- Test failure tracking

---

### 5.5 Jira Integration for Project Management

**Create Jira tickets for bugs.**

```json
{
  "hooks": {
    "PostToolUseFailure": {
      "Bash(bun test --run)": [
        {
          "command": "bash -c '\n            TEST_OUTPUT=\"$TOOL_RESULT\"\n            FAILED_TESTS=$(echo \"$TEST_OUTPUT\" | grep -E \"FAIL\" | wc -l)\n            \n            if [ \"$FAILED_TESTS\" -gt 5 ]; then\n              echo \"[Jira MCP] Multiple test failures detected - creating bug ticket...\"\n              \n              claude-mcp jira create-issue \\\n                --project \"ENG\" \\\n                --type \"Bug\" \\\n                --summary \"$FAILED_TESTS test failures in $(git rev-parse --abbrev-ref HEAD)\" \\\n                --description \"{\n                  \\\"type\\\": \\\"doc\\\",\n                  \\\"content\\\": [\n                    {\\\"type\\\": \\\"paragraph\\\", \\\"content\\\": [{\\\"type\\\": \\\"text\\\", \\\"text\\\": \\\"Test suite regression detected.\\\"}]},\n                    {\\\"type\\\": \\\"codeBlock\\\", \\\"content\\\": [{\\\"type\\\": \\\"text\\\", \\\"text\\\": $(echo \"$TEST_OUTPUT\" | jq -Rs .)}]}\n                  ]\n                }\" \\\n                --priority \"High\" \\\n                --labels \"test-regression,auto-created\"\n              \n              echo \"✅ Jira bug ticket created\"\n            fi\n          '",
          "async": true,
          "description": "Create Jira bug for test regressions"
        }
      ]
    }
  }
}
```

**Jira MCP Tools:**
- `jira create-issue`
- `jira update-issue`
- `jira search-issues`

**Features:**
- Threshold-based ticket creation
- Rich text formatting
- Automatic labeling

---

### 5.6 Confluence Documentation Updates

**Auto-update docs on API changes.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Edit": [
        {
          "command": "bash -c '\n            FILE=\"$TOOL_INPUT_FILE_PATH\"\n            \n            # Detect API endpoint changes\n            if echo \"$FILE\" | grep -q \"routes.ts\"; then\n              echo \"[Confluence MCP] API routes changed - updating docs...\"\n              \n              # Generate OpenAPI spec\n              bun run generate-openapi > /tmp/openapi.json\n              \n              # Update Confluence page\n              claude-mcp confluence update-page \\\n                --page-id \"123456789\" \\\n                --title \"API Reference (Auto-Generated)\" \\\n                --content \"<ac:structured-macro ac:name=\\\"code\\\">\n                  <ac:plain-text-body><![CDATA[\n                  $(cat /tmp/openapi.json)\n                  ]]></ac:plain-text-body>\n                </ac:structured-macro>\n                <p>Last updated: $(date)</p>\" \\\n                --version \"incremental\"\n              \n              echo \"✅ Confluence docs updated\"\n            fi\n          '",
          "async": true,
          "description": "Auto-update Confluence on API changes"
        }
      ]
    }
  }
}
```

**Confluence MCP Tools:**
- `confluence update-page`
- `confluence create-page`
- `confluence search-pages`

**Features:**
- Automatic doc generation
- Version tracking
- Rich content macros

---

### 5.7 Figma Design Sync

**Validate design tokens against Figma.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(git commit)": [
        {
          "command": "bash -c '\n            FILES_CHANGED=$(git diff --cached --name-only)\n            \n            # Check if design tokens changed\n            if echo \"$FILES_CHANGED\" | grep -q \"tokens.json\"; then\n              echo \"[Figma MCP] Validating design tokens...\"\n              \n              # Fetch latest from Figma\n              claude-mcp figma get-file-variables \\\n                --file-key \"ABC123XYZ\" \\\n                --output /tmp/figma-tokens.json\n              \n              # Compare with local\n              DIFF=$(diff <(jq -S . tokens.json) <(jq -S . /tmp/figma-tokens.json) || true)\n              \n              if [ -n \"$DIFF\" ]; then\n                echo \"⚠️ Design tokens diverge from Figma:\"\n                echo \"$DIFF\"\n                read -p \"Type OVERRIDE to commit anyway: \" OVERRIDE\n                [ \"$OVERRIDE\" = \"OVERRIDE\" ] || exit 1\n              fi\n              \n              echo \"✅ Design tokens validated\"\n            fi\n          '",
          "description": "Validate design tokens against Figma source"
        }
      ]
    }
  }
}
```

**Figma MCP Tools:**
- `figma get-file-variables`
- `figma get-styles`
- `figma export-images`

**Features:**
- Design token sync
- Divergence detection
- Override mechanism

---

### 5.8 Gmail Integration for Code Review Requests

**Send code review requests via email.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Bash(gh pr create)": [
        {
          "command": "bash -c '\n            PR_URL=$(gh pr view --json url -q .url)\n            PR_TITLE=$(gh pr view --json title -q .title)\n            FILES_CHANGED=$(git diff main...HEAD --name-only | wc -l)\n            \n            echo \"[Gmail MCP] Sending code review request...\"\n            \n            claude-mcp gmail send-email \\\n              --to \"team-lead@example.com\" \\\n              --subject \"[Code Review] $PR_TITLE\" \\\n              --body \"<html>\n                <body>\n                  <h2>Code Review Request</h2>\n                  <p><strong>PR:</strong> <a href=\\\"$PR_URL\\\">$PR_TITLE</a></p>\n                  <p><strong>Files Changed:</strong> $FILES_CHANGED</p>\n                  <p><strong>Description:</strong></p>\n                  <pre>$(gh pr view --json body -q .body)</pre>\n                  <p>Please review at your earliest convenience.</p>\n                </body>\n              </html>\" \\\n              --html\n            \n            echo \"✅ Code review request sent\"\n          '",
          "async": true,
          "description": "Email team lead for code review"
        }
      ]
    }
  }
}
```

**Gmail MCP Tools:**
- `gmail send-email`
- `gmail list-threads`
- `gmail create-draft`

**Features:**
- HTML email formatting
- PR metadata inclusion
- Async sending

---

### 5.9 Notion Knowledge Base Integration

**Auto-create postmortem documents.**

```json
{
  "hooks": {
    "PostToolUseFailure": {
      "Bash(make deploy-production)": [
        {
          "command": "bash -c '\n            echo \"[Notion MCP] Creating deployment postmortem...\"\n            \n            FAILURE_LOG=\"$TOOL_RESULT\"\n            TIMESTAMP=$(date -Iseconds)\n            \n            claude-mcp notion create-page \\\n              --parent-id \"abc123xyz\" \\\n              --title \"Deployment Failure - $TIMESTAMP\" \\\n              --properties \"{\n                \\\"Status\\\": {\\\"select\\\": {\\\"name\\\": \\\"In Progress\\\"}},\n                \\\"Severity\\\": {\\\"select\\\": {\\\"name\\\": \\\"High\\\"}},\n                \\\"Date\\\": {\\\"date\\\": {\\\"start\\\": \\\"$TIMESTAMP\\\"}}\n              }\" \\\n              --content \"[\n                {\n                  \\\"object\\\": \\\"block\\\",\n                  \\\"type\\\": \\\"heading_2\\\",\n                  \\\"heading_2\\\": {\\\"rich_text\\\": [{\\\"type\\\": \\\"text\\\", \\\"text\\\": {\\\"content\\\": \\\"Incident Summary\\\"}}]}\n                },\n                {\n                  \\\"object\\\": \\\"block\\\",\n                  \\\"type\\\": \\\"code\\\",\n                  \\\"code\\\": {\\\"rich_text\\\": [{\\\"type\\\": \\\"text\\\", \\\"text\\\": {\\\"content\\\": $(echo \"$FAILURE_LOG\" | jq -Rs .)}}]}\n                }\n              ]\"\n            \n            echo \"✅ Postmortem created in Notion\"\n          '",
          "async": true,
          "description": "Auto-create Notion postmortem on deploy failure"
        }
      ]
    }
  }
}
```

**Notion MCP Tools:**
- `notion create-page`
- `notion update-page`
- `notion query-database`

**Features:**
- Structured postmortem templates
- Rich content blocks
- Property-based filtering

---

### 5.10 Database Query Integration

**Validate migrations against live schema.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(migrate)": [
        {
          "command": "bash -c '\n            echo \"[Database MCP] Validating migration...\"\n            \n            # Get current schema\n            CURRENT_SCHEMA=$(claude-mcp postgres query \\\n              --connection \"$DATABASE_URL\" \\\n              --query \"SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_schema = 'public' ORDER BY table_name, ordinal_position\")\n            \n            # Dry-run migration\n            NEW_SCHEMA=$(psql \"$DATABASE_URL\" --dry-run -f migrations/latest.sql 2>&1)\n            \n            # Detect breaking changes\n            DROPPED_COLUMNS=$(echo \"$NEW_SCHEMA\" | grep -i \"DROP COLUMN\" || true)\n            if [ -n \"$DROPPED_COLUMNS\" ]; then\n              echo \"⚠️ BREAKING CHANGE: Columns will be dropped\"\n              echo \"$DROPPED_COLUMNS\"\n              exit 1\n            fi\n            \n            echo \"✅ Migration validation passed\"\n          '",
          "description": "Validate migrations with live schema comparison"
        }
      ]
    }
  }
}
```

**Database MCP Tools:**
- `postgres query`
- `postgres execute`
- `postgres get-schema`

**Features:**
- Live schema comparison
- Breaking change detection
- Dry-run validation

---

### 5.11 Playwright Browser Automation

**Visual regression testing via MCP.**

```json
{
  "hooks": {
    "PostToolUse": {
      "Bash(bun build)": [
        {
          "command": "bash -c '\n            echo \"[Playwright MCP] Running visual regression tests...\"\n            \n            # Navigate to staging\n            claude-mcp playwright browser_navigate \\\n              --url \"https://staging.example.com\"\n            \n            # Wait for hydration\n            claude-mcp playwright browser_wait_for \\\n              --selector \"#app[data-hydrated='true']\"\n            \n            # Take screenshot\n            claude-mcp playwright browser_take_screenshot \\\n              --full_page true \\\n              --path \"/tmp/staging-screenshot.png\"\n            \n            # Compare with baseline\n            DIFF=$(compare -metric AE /tmp/baseline.png /tmp/staging-screenshot.png /tmp/diff.png 2>&1 || true)\n            \n            if [ \"$DIFF\" -gt 1000 ]; then\n              echo \"❌ Visual regression detected: $DIFF pixels changed\"\n              exit 1\n            fi\n            \n            echo \"✅ Visual regression tests passed\"\n          '",
          "async": true,
          "description": "Visual regression testing via Playwright MCP"
        }
      ]
    }
  }
}
```

**Playwright MCP Tools:**
- `playwright browser_navigate`
- `playwright browser_take_screenshot`
- `playwright browser_wait_for`

**Features:**
- Automated browser control
- Screenshot comparison
- Pixel-level diffing

---

### 5.12 Context7 API Documentation Integration

**Validate code against latest library docs.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(git commit)": [
        {
          "command": "bash -c '\n            FILES_CHANGED=$(git diff --cached --name-only)\n            \n            # Check for React usage changes\n            if echo \"$FILES_CHANGED\" | grep -q \"\\.tsx$\"; then\n              echo \"[Context7 MCP] Checking React best practices...\"\n              \n              # Query latest React docs\n              LATEST_HOOKS_DOCS=$(claude-mcp context7 query-docs \\\n                --library \"react\" \\\n                --query \"useState useEffect dependencies\" \\\n                --version \"latest\")\n              \n              # Check for common anti-patterns\n              MISSING_DEPS=$(grep -r \"useEffect(\" frontend/ | grep -v \"// eslint-disable\" | grep -v \"\\[\\]\" || true)\n              \n              if [ -n \"$MISSING_DEPS\" ]; then\n                echo \"⚠️ Potential missing dependencies in useEffect:\"\n                echo \"$MISSING_DEPS\"\n                echo \"\"\n                echo \"Latest docs:\"\n                echo \"$LATEST_HOOKS_DOCS\"\n              fi\n            fi\n            \n            echo \"✅ Context7 validation complete\"\n          '",
          "description": "Validate React patterns against latest docs"
        }
      ]
    }
  }
}
```

**Context7 MCP Tools:**
- `context7 query-docs`
- `context7 resolve-library-id`

**Features:**
- Latest documentation querying
- Anti-pattern detection
- Version-specific validation

---

## 6. Configuration Templates

### 6.1 Full Production Hook Suite

**settings.json with all major hooks.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(git commit)": [
        {
          "command": "bash -c 'bun run lint:check && bun test --run && go test ./... && pytest'",
          "description": "Pre-commit validation suite"
        }
      ],
      "Bash(git push origin main)": [
        {
          "command": "bash -c 'BRANCH=$(git rev-parse --abbrev-ref HEAD); [ \"$BRANCH\" != \"main\" ] || { echo \"⚠️ Pushing to main\"; read -p \"Confirm (yes): \" CONFIRM; [ \"$CONFIRM\" = \"yes\" ]; }'",
          "description": "Confirm main branch pushes"
        }
      ],
      "Bash(migrate)": [
        {
          "command": "bash -c 'pg_dump \"$DATABASE_URL\" > \"backups/pre-migration-$(date +%s).sql\" && echo \"✅ Backup created\"'",
          "description": "Backup database before migrations"
        }
      ]
    },
    "PostToolUse": {
      "Bash(bun add)": [
        {
          "command": "bash -c 'bun audit && npx license-checker --production --failOn \"GPL;AGPL\"'",
          "description": "Audit dependencies after install",
          "async": true
        }
      ],
      "Bash(git push origin main)": [
        {
          "command": "bash -c 'linear issue create --title \"Deployed $(git rev-parse --short HEAD)\" --description \"Auto-deploy notification\" --priority 4 --label \"deployment\"'",
          "description": "Create Linear deployment ticket",
          "async": true
        }
      ]
    },
    "PostToolUseFailure": {
      "Bash(bun test)": [
        {
          "command": "bash -c 'echo \"$TOOL_RESULT\" > .test-failures.log && cat .test-failures.log | tee -a .persistent-failures.log'",
          "description": "Log test failures for debugging"
        }
      ]
    }
  }
}
```

---

### 6.2 Development Environment Template

**Fast feedback for local development.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Edit": [
        {
          "command": "bash -c 'FILE=\"$TOOL_INPUT_FILE_PATH\"; case \"$FILE\" in *.ts|*.tsx) bunx prettier --check \"$FILE\" ;; *.py) black --check \"$FILE\" ;; esac'",
          "description": "Format check on edit"
        }
      ]
    },
    "PostToolUse": {
      "Edit": [
        {
          "command": "bash -c 'FILE=\"$TOOL_INPUT_FILE_PATH\"; if grep -qE \"(TODO:|FIXME:)\" \"$FILE\"; then grep -nE \"(TODO:|FIXME:)\" \"$FILE\"; fi'",
          "description": "Show TODOs after editing",
          "async": true
        }
      ]
    }
  }
}
```

---

### 6.3 CI/CD Pipeline Template

**Comprehensive checks for continuous integration.**

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash(git push)": [
        {
          "command": "bash -c 'bun run type-check && bun run lint:check && bun test --coverage --run && go test -race ./... && pytest --cov --cov-fail-under=90'",
          "description": "Full CI validation suite"
        }
      ]
    },
    "PostToolUse": {
      "Bash(git push origin main)": [
        {
          "command": "bash -c 'sleep 60 && curl -f https://app.example.com/health || { git revert HEAD --no-edit && git push origin main --force-with-lease; }'",
          "description": "Health check with auto-rollback",
          "async": true
        }
      ]
    }
  }
}
```

---

## 7. Best Practices

### 7.1 Performance Optimization

1. **Use `async: true` for non-blocking hooks**
   - Long-running tasks (profiling, monitoring)
   - Non-critical notifications (Slack, email)
   - Background processing (log aggregation)

2. **Minimize hook execution time**
   - Cache expensive computations
   - Use incremental checks (only changed files)
   - Parallelize independent checks (`&` + `wait`)

3. **Avoid redundant tool calls**
   - Check if validation already passed in earlier hooks
   - Use environment variables to share state between hooks

### 7.2 Error Handling

1. **Always provide actionable error messages**
   ```bash
   echo "❌ Tests failed - run 'bun test --watch' to debug"
   ```

2. **Use exit codes correctly**
   - `exit 0` - success, continue
   - `exit 1` - failure, block operation
   - `exit 2` - warning, log but continue

3. **Log failures persistently**
   ```bash
   echo "$TOOL_RESULT" | tee -a .persistent-failures.log
   ```

### 7.3 Security

1. **Never log secrets**
   ```bash
   SANITIZED_OUTPUT=$(echo "$TOOL_RESULT" | sed 's/token=[^&]*/token=REDACTED/g')
   ```

2. **Validate inputs**
   ```bash
   FILE="$TOOL_INPUT_FILE_PATH"
   [ -f "$FILE" ] || { echo "Invalid file"; exit 1; }
   ```

3. **Use read-only operations when possible**
   ```bash
   # Good: read-only check
   git diff --check

   # Avoid: modifying state in PreToolUse hooks
   git commit --amend  # BAD in PreToolUse
   ```

### 7.4 Testing Hooks

1. **Test hooks in isolation**
   ```bash
   # Extract hook command to script
   .claude/hooks/pre-commit.sh

   # Test manually
   bash .claude/hooks/pre-commit.sh
   ```

2. **Use dry-run flags**
   ```bash
   psql --dry-run -f migration.sql
   gh pr create --dry-run
   ```

3. **Mock external services**
   ```bash
   if [ -n "$HOOK_TEST_MODE" ]; then
     echo "Skipping Slack notification (test mode)"
     exit 0
   fi
   ```

---

## 8. Performance & Error Handling

### 8.1 Performance Benchmarks

**Expected hook execution times:**

| Hook Type | Operation | Target Time | Notes |
|-----------|-----------|-------------|-------|
| PreToolUse | Lint check | <2s | Use `--cache` flags |
| PreToolUse | Unit tests | <10s | Run only changed files |
| PreToolUse | Security scan | <30s | Incremental scanning |
| PostToolUse | Notification | <1s | Async recommended |
| PostToolUse | Documentation | <5s | Async recommended |

### 8.2 Error Recovery Patterns

**Retry with exponential backoff:**

```bash
retry() {
  local max_attempts=3
  local delay=1
  local attempt=1

  while [ $attempt -le $max_attempts ]; do
    "$@" && return 0

    echo "Attempt $attempt failed, retrying in ${delay}s..."
    sleep $delay
    delay=$((delay * 2))
    attempt=$((attempt + 1))
  done

  echo "All $max_attempts attempts failed"
  return 1
}

retry bun test
```

**Graceful degradation:**

```bash
# Try primary tool, fallback to secondary
bun run format:check || {
  echo "⚠️ Primary formatter failed, trying fallback..."
  prettier --check .
}
```

### 8.3 Monitoring Hook Performance

**Log execution times:**

```bash
START=$(date +%s)
bun test --run
END=$(date +%s)
DURATION=$((END - START))

echo "Test suite completed in ${DURATION}s" >> .hook-performance.log

if [ $DURATION -gt 30 ]; then
  echo "⚠️ Tests slower than expected (${DURATION}s > 30s)"
fi
```

---

## Research Sources

This guide synthesizes research from multiple authoritative sources:

- [Claude Code Hooks Reference](https://code.claude.com/docs/en/hooks) - Official documentation on hook lifecycle events
- [GitHub - claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) - Community hook patterns
- [Claude Code Hooks Complete Guide](https://claudefa.st/blog/tools/hooks/hooks-guide) - 12 lifecycle events reference
- [DataCamp: Claude Code Hooks Tutorial](https://www.datacamp.com/tutorial/claude-code-hooks) - Workflow automation guide
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-11-25) - MCP protocol details
- [GitHub - MCP Servers](https://github.com/modelcontextprotocol/servers) - Official MCP server catalog
- [Awesome MCP Servers](https://github.com/wong2/awesome-mcp-servers) - Community MCP integrations
- [MCP Servers Directory](https://aiagentslist.com/mcp-servers) - 593+ MCP server catalog
- [Git Hooks Best Practices - Kinsta](https://kinsta.com/blog/git-hooks/) - Advanced techniques
- [Git Hooks Tutorial - xCloud](https://xcloud.host/top-advanced-git-hooks-best-practices/) - 10 advanced practices
- [GitHub Actions Composite vs Reusable Workflows](https://kubermates.org/blog/github-actions-composite-vs-reusable-workflows-4bih/) - Orchestration patterns
- [Claude Code Slack Bot](https://github.com/mpociot/claude-code-slack-bot) - MCP Slack integration
- [Your Claude Engineer](https://github.com/coleam00/your-claude-engineer) - Multi-agent MCP harness
- [Claude Code MCP Documentation](https://code.claude.com/docs/en/mcp) - Tool connection guide

---

## Appendix: Quick Reference Card

**Most Common Patterns:**

```bash
# Pre-commit validation
PreToolUse: Bash(git commit) → lint + test + format

# Post-deploy monitoring
PostToolUse: Bash(git push main) → health check + Slack notify

# Test failure recovery
PostToolUseFailure: Bash(test) → retry + log + notify

# Dependency audit
PostToolUse: Bash(bun add) → security scan + license check

# Agent delegation
PostToolUseFailure: Bash(test) → spawn debugging agent
```

**Hook Variables:**

- `$TOOL_INPUT_FILE_PATH` - File being edited
- `$TOOL_RESULT` - Tool output/error
- `$CI` - Detect CI environment

**Exit Codes:**

- `0` - Success, continue
- `1` - Failure, block
- `2` - Warning, log only

---

**Document Status:** Research Complete | Ready for Implementation
**Next Steps:** Select patterns for DX improvement plan, integrate with existing workflow
