# BMM Automation - Documentation Index

Complete guide to the BMM workflow automation system.

## 📚 Documentation Files

### 🚀 Getting Started

1. **[QUICKSTART.md](./QUICKSTART.md)** - Start here!
   - 5-minute setup guide
   - Prerequisites check
   - First workflow execution
   - Common usage patterns
   - **Best for:** First-time users

### 📖 Complete Guide

2. **[README.md](./README.md)** - Full documentation
   - All features explained
   - Detailed usage examples
   - Configuration options
   - Troubleshooting guide
   - **Best for:** Understanding all capabilities

### 🏗️ Technical Details

3. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture
   - Component breakdown
   - CLI integration details
   - Structured output protocol
   - Parallel execution strategy
   - Extension points
   - **Best for:** Developers and contributors

### 📊 Overview

4. **[SUMMARY.md](./SUMMARY.md)** - High-level summary
   - What was created
   - How it works
   - Key benefits
   - Integration examples
   - **Best for:** Quick overview

### ✅ Delivery Report

5. **[DELIVERY.md](./DELIVERY.md)** - Project delivery
   - Requirements checklist
   - Deliverables list
   - Usage examples
   - Performance metrics
   - **Best for:** Project stakeholders

## 🎯 Quick Navigation

### By User Type

**New User:**
1. Read [QUICKSTART.md](./QUICKSTART.md)
2. Run `./scripts/bmm-auto.py init`
3. Run `./scripts/bmm-auto.py status`
4. Run `./scripts/bmm-auto.py next`

**Experienced User:**
1. Check [README.md](./README.md) for advanced options
2. Use `--parallel` for faster execution
3. Use `--phase` to run entire phases
4. Customize with `--cli` and `--verbose`

**Developer:**
1. Review [ARCHITECTURE.md](./ARCHITECTURE.md)
2. Understand component structure
3. Check extension points
4. Review structured output protocol

**Project Manager:**
1. Read [SUMMARY.md](./SUMMARY.md)
2. Review [DELIVERY.md](./DELIVERY.md)
3. Check performance metrics
4. Plan workflow execution

### By Task

**Installing:**
→ [QUICKSTART.md - Step 1-2](./QUICKSTART.md#step-1-prerequisites)

**Initializing:**
→ [QUICKSTART.md - Step 3](./QUICKSTART.md#step-3-initialize-your-project)

**Running Workflows:**
→ [README.md - Usage](./README.md#usage)

**Parallel Execution:**
→ [ARCHITECTURE.md - Parallel Execution](./ARCHITECTURE.md#parallel-execution-strategy)

**Troubleshooting:**
→ [README.md - Troubleshooting](./README.md#troubleshooting)

**Extending:**
→ [ARCHITECTURE.md - Extension Points](./ARCHITECTURE.md#extension-points)

**OpenSpec Integration:**
→ [README.md - OpenSpec](./README.md#integration-with-openspec)

## 📁 File Structure

```
scripts/
├── bmm-auto.py           # Main automation script (632 lines)
├── INDEX.md              # This file
├── QUICKSTART.md         # 5-minute guide (175 lines)
├── README.md             # Full documentation (266 lines)
├── ARCHITECTURE.md       # Technical details (150 lines)
├── SUMMARY.md            # Overview (150 lines)
└── DELIVERY.md           # Delivery report (150 lines)
```

## 🎓 Learning Path

### Beginner Path (30 minutes)

1. **Read:** [QUICKSTART.md](./QUICKSTART.md) (5 min)
2. **Install:** Prerequisites and setup (10 min)
3. **Initialize:** Run `bmm-auto init` (5 min)
4. **Execute:** Run first workflow (10 min)

### Intermediate Path (1 hour)

1. **Review:** [README.md](./README.md) (15 min)
2. **Practice:** Run multiple workflows (20 min)
3. **Experiment:** Try parallel execution (15 min)
4. **Explore:** Check status and options (10 min)

### Advanced Path (2 hours)

1. **Study:** [ARCHITECTURE.md](./ARCHITECTURE.md) (30 min)
2. **Understand:** Structured output protocol (20 min)
3. **Analyze:** Parallel execution strategy (20 min)
4. **Plan:** Extension or integration (50 min)

## 🔍 Common Questions

### "Where do I start?"
→ [QUICKSTART.md](./QUICKSTART.md)

### "How does it work?"
→ [ARCHITECTURE.md - Overview](./ARCHITECTURE.md#overview)

### "What can it do?"
→ [SUMMARY.md - Key Benefits](./SUMMARY.md#key-benefits)

### "How do I run workflows in parallel?"
→ [README.md - Advanced Options](./README.md#advanced-options)

### "Can I use it in other projects?"
→ Yes! See [DELIVERY.md - Cross-Project Portability](./DELIVERY.md#cross-project-portability)

### "How do I integrate with OpenSpec?"
→ [README.md - OpenSpec Integration](./README.md#integration-with-openspec)

### "What if something breaks?"
→ [README.md - Troubleshooting](./README.md#troubleshooting)

### "How do I extend it?"
→ [ARCHITECTURE.md - Extension Points](./ARCHITECTURE.md#extension-points)

## 📋 Cheat Sheet

### Essential Commands

```bash
# Initialize
./scripts/bmm-auto.py init

# Check status
./scripts/bmm-auto.py status

# Run next workflow
./scripts/bmm-auto.py next

# Run specific workflow
./scripts/bmm-auto.py run <workflow-id>

# Run entire phase
./scripts/bmm-auto.py run --phase <0|1|2|3>

# Run in parallel
./scripts/bmm-auto.py run --parallel

# Get help
./scripts/bmm-auto.py --help
```

### Common Workflows

```bash
# Discovery phase (parallel)
./scripts/bmm-auto.py run --phase 0 --parallel

# Planning phase
./scripts/bmm-auto.py run --phase 1

# Solutioning phase
./scripts/bmm-auto.py run --phase 2

# Implementation phase
./scripts/bmm-auto.py run --phase 3
```

## 🔗 External Resources

- **BMad Documentation:** `.bmad/bmm/docs/`
- **Workflow Definitions:** `.bmad/bmm/workflows/`
- **Agent Configurations:** `.bmad/bmm/agents/`
- **Auggie CLI Docs:** https://docs.augmentcode.com
- **Claude CLI Docs:** https://www.anthropic.com/claude

## 📞 Support

For help:
1. Check this INDEX for relevant documentation
2. Review the specific guide for your task
3. Check troubleshooting sections
4. Consult BMad documentation

## 🎉 Quick Wins

**5 minutes:**
- Initialize your project
- Check workflow status

**15 minutes:**
- Run your first workflow
- See automated execution

**30 minutes:**
- Run entire discovery phase
- Experience parallel execution

**1 hour:**
- Complete planning phase
- Understand the full workflow

---

**Start here:** [QUICKSTART.md](./QUICKSTART.md) 🚀

