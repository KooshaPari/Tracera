---
description: Share a quick agent briefing referencing canonical docs
argument-hint: <task-context>
---

Compose an agent briefing for `$ARGUMENTS` before coding:

- Reference `AGENTS.md`, relevant `docs/plans/*.md`, and `work-prompts/` entries.
- Summarize build/test commands and guardrails that apply.
- Specify success criteria, evidence required (tests, logs), and constraints (paths, tooling).
- **Subagent deployment:** Include when to use **native CLI subagents** (Cursor Agent, Gemini CLI, Codex subagent, Copilot CLI, Claude Code) vs **thegent subagents** (`thegent run gemini`, `thegent run droid`, `thegent run cursor`, etc.). Use native for tool-specific behavior; use thegent for cross-provider orchestration, droids, or model/env control. See `docs/reference/THGENT_QUICK_REFERENCE.md`.

Respond with:

Briefing:
- Context: <what we're doing and why>
- Constraints: <paths, tooling, guardrails>
- Evidence: <tests, artifacts, docs to update>
- References: <doc links>
