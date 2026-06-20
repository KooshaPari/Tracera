# Claude Code V4 Research Synthesis
**Date:** 2026-02-06
**Team:** dx-improvement-research
**Sources:** 40+ community resources + 3 methodology frameworks

## Executive Summary

Combined research from methodology frameworks (GSD, OpenSpec, BMAD) and Claude Code V4 community reveals a clear path to hybrid automation:

**Key Finding:** Manual slash commands should transition to **auto-detected workflows** triggered by context, file patterns, git events, and methodology markers.

---

## Research Findings Combined

### From Methodology Research
- **GSD:** 200k subagent contexts, atomic commits, phase-based execution
- **OpenSpec:** Artifact gates (proposal → spec → design), systematic workflow
- **BMAD:** YAML orchestration, event-driven rules, specialized agents

### From Reddit/Community Research
- **MCP Tool Search:** 85% context reduction enables massive automation
- **Hook Input Modification:** v2.0.10+ can modify tool inputs transparently
- **Custom Agents:** Isolated contexts, auto-invoked like tools
- **Pain Points:** Quality regression, context loss, manual ceremony

---

## Hybrid Architecture Design

### Layer 1: Orchestration (BMAD)
- YAML workflow definitions
- Event-driven automation (when/then)
- Multi-agent coordination

### Layer 2: Context Efficiency (GSD)
- 200k subagent spawning
- Atomic commits per task
- Aggressive delegation

### Layer 3: Artifact Discipline (OpenSpec)
- proposal → spec → design gates
- Progressive disclosure
- Systematic workflow enforcement

### Layer 4: Community Patterns (V4)
- MCP Tool Search lazy loading
- Hook input modification
- Background parallel execution
- Custom agent auto-delegation

---

## Automation Opportunities Identified

### Hook Automation (High Priority)
1. **File Protection** - PreToolUse blocks .env, bun.lock, secrets
2. **Auto-test Running** - PostToolUse after code edits
3. **Context Injection** - UserPromptSubmit loads git context
4. **Session Summaries** - SessionEnd generates phase reports
5. **Phase Execution** - Setup hook for repo initialization

### Auto-Trigger Patterns
1. **Context Detection** - "add auth" → /dev:feature pipeline
2. **File Patterns** - *.test.ts changes → run tests
3. **Git Events** - pre-commit → run linters
4. **Explicit Markers** - `// @trace:review` → code review
5. **Methodology Workflows** - propose/impl/validate keywords

### Progressive Elicitation
- AskUserQuestion at checkpoints (not termination)
- Multi-round spec refinement
- Architectural choice points

---

## Recommended Implementation Phases

### Phase 1: Hook System (Week 1)
- File protection hooks (.env, bun.lock)
- Auto-test running (PostToolUse)
- Context injection (UserPromptSubmit)
- Session summaries (SessionEnd)

### Phase 2: Auto-Detection (Week 2)
- Context pattern matching
- File change detection
- Git event integration
- Methodology keyword triggers

### Phase 3: Agent Specialization (Week 3-4)
- Frontend agent (React/Vite isolated)
- Backend agent (Go isolated)
- Docs agent (markdown standards)
- Test agent (gap analysis)

### Phase 4: Workflow Integration (Month 2)
- YAML workflow definitions
- OpenSpec artifact gates
- GSD phase execution
- Background task coordination

---

## Critical Insights

### Quality Regression Mitigation
**Problem:** Model making broken attempts vs thinking through
**Solution:**
- CLAUDE.md persistent context
- Skills for progressive disclosure
- Checkpoints for state summarization

### Context Budget Management
**Problem:** 200k → 70k with all MCPs enabled
**Solution:**
- MCP Tool Search lazy loading
- `disabledMcpServers` per project
- Aggressive subagent delegation

### Manual Ceremony Reduction
**Problem:** Too many slash commands needed
**Solution:**
- Auto-detection replaces manual triggers
- Hooks enforce deterministically
- Background tasks enable parallelization

---

## Sources Summary

**Methodology Frameworks:**
- Get Shit Done: https://github.com/glittercowboy/get-shit-done
- OpenSpec: https://github.com/Fission-AI/OpenSpec
- BMAD Method: https://github.com/bmad-code-org/BMAD-METHOD

**Community Research:**
- TheDecipherist V4 Guide (240K views)
- affaan-m Hackathon Configs (10+ months production)
- 40+ community resources (DataCamp, builder.io, alexop.dev, etc.)

**Research Gaps:**
- Plan Mode + AskUserQuestion integration
- Session teleportation mechanics
- Advanced multi-agent coordination
- Production observability patterns
