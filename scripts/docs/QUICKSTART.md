# BMM Automation Quick Start

Get started with automated BMM workflows in 5 minutes.

## Step 1: Prerequisites

Ensure you have Python 3.8+ and one of these CLI tools:

```bash
# Check Python version
python3 --version

# Install Auggie CLI (recommended)
bun add -g @augmentcode/cli

# OR install Claude CLI
pip install claude-cli

# Verify installation
which auggie  # or: which claude
```

## Step 2: Make Script Executable

```bash
chmod +x scripts/python/bmm-auto.py
```

## Step 3: Initialize Your Project

```bash
# Run from project root
./scripts/python/bmm-auto.py init
```

This will:
1. Check if BMM is already initialized
2. If not, run the workflow-init workflow
3. Guide you through project setup (track, type, discovery options)
4. Create `docs/bmm-workflow-status.yaml`

## Step 4: Check Status

```bash
./scripts/python/bmm-auto.py status
```

You'll see:
- Project name and configuration
- Selected track (quick-flow/method/enterprise)
- Field type (greenfield/brownfield)
- All workflows with their status (pending/complete)
- Progress summary

## Step 5: Run Workflows

### Option A: Interactive (Recommended for First Time)

```bash
# Run next workflow
./scripts/python/bmm-auto.py next

# Or run specific workflow
./scripts/python/bmm-auto.py run brainstorm-project
```

### Option B: Batch Execution

```bash
# Run all Phase 0 (Discovery) workflows
./scripts/python/bmm-auto.py run --phase 0

# Run with parallel execution (faster)
./scripts/python/bmm-auto.py run --phase 0 --parallel
```

### Option C: Full Automation (Experimental)

```bash
# Run all workflows automatically
./scripts/python/bmm-auto.py run --auto
```

⚠️ **Note**: Auto mode is experimental. Interactive mode is recommended for quality control.

## Example: Complete Enterprise Workflow

```bash
# 1. Initialize
./scripts/python/bmm-auto.py init
# Answer: Enterprise Method, Greenfield, All discovery workflows

# 2. Run Discovery Phase (parallel for speed)
./scripts/python/bmm-auto.py run --phase 0 --parallel

# 3. Run Planning Phase
./scripts/python/bmm-auto.py run --phase 1

# 4. Run Solutioning Phase
./scripts/python/bmm-auto.py run --phase 2

# 5. Check final status
./scripts/python/bmm-auto.py status

# 6. Run Implementation (when ready)
./scripts/python/bmm-auto.py run --phase 3
```

## Common Workflows

### For TraceRTM (Current Project)

Based on your Enterprise Method + Greenfield setup:

```bash
# Phase 0: Discovery
./scripts/python/bmm-auto.py run brainstorm-project  # Creative exploration
./scripts/python/bmm-auto.py run research             # Technical analysis
./scripts/python/bmm-auto.py run product-brief        # Strategic planning

# Phase 1: Planning
./scripts/python/bmm-auto.py run prd                  # Requirements
./scripts/python/bmm-auto.py run validate-prd         # Validation
./scripts/python/bmm-auto.py run create-design        # UX Design

# Phase 2: Solutioning
./scripts/python/bmm-auto.py run create-architecture  # Architecture
./scripts/python/bmm-auto.py run test-design          # Test strategy
./scripts/python/bmm-auto.py run validate-architecture
./scripts/python/bmm-auto.py run create-epics-and-stories
./scripts/python/bmm-auto.py run implementation-readiness

# Phase 3: Implementation
./scripts/python/bmm-auto.py run sprint-planning
```

## Tips & Tricks

### 1. Use Aliases

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias bmm='./scripts/python/bmm-auto.py'
```

Then use:
```bash
bmm status
bmm next
bmm run --phase 0
```

### 2. Run from Any Directory

```bash
# Specify project root
bmm-auto --project-root /path/to/project status
```

### 3. Verbose Mode for Debugging

```bash
bmm-auto run --verbose brainstorm-project
```

### 4. Choose Specific CLI

```bash
# Force use of auggie
bmm-auto run --cli auggie

# Force use of claude
bmm-auto run --cli claude
```

## Troubleshooting

### Script won't run

```bash
# Make executable
chmod +x scripts/python/bmm-auto.py

# Or run with python directly
python3 scripts/python/bmm-auto.py status
```

### "No workflow status found"

You need to initialize first:
```bash
bmm-auto init
```

### Workflows not progressing

Check the workflow status file:
```bash
cat docs/bmm-workflow-status.yaml
```

Ensure workflows are marked correctly after completion.

## Next Steps

1. **Read the full README**: `scripts/docs/README.md`
2. **Understand BMM phases**: `.bmad/bmm/docs/`
3. **Customize agents**: `.bmad/bmm/agents/`
4. **Create custom workflows**: `.bmad/custom/workflows/`

## Integration with Other Tools

### With OpenSpec

```bash
# 1. Run BMM planning
bmm-auto run --phase 0 --phase 1 --phase 2

# 2. Sync to OpenSpec
cp docs/PRD.md openspec/specs/requirements.md
cp docs/architecture.md openspec/specs/architecture.md

# 3. Use OpenSpec for implementation
# /openspec:proposal, /openspec:apply, etc.
```

### With Git

```bash
# Commit after each phase
bmm-auto run --phase 0
git add docs/
git commit -m "Complete Phase 0: Discovery"

bmm-auto run --phase 1
git add docs/
git commit -m "Complete Phase 1: Planning"
```

## Support

- **Documentation**: `.bmad/bmm/docs/`
- **Examples**: `.bmad/bmm/reference/`
- **Workflow definitions**: `.bmad/bmm/workflows/`

