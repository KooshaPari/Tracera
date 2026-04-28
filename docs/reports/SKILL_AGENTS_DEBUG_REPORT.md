# Skill-Based Agents Debug Report

**Date:** 2026-02-06
**Issue:** Skill() tool invocation failing for copilot-agent, codex-agent, cursor-agent, gemini-agent, codex-subagent

## Root Cause Analysis

### What Was Broken

1. **Wrong Directory Location**
   - Skills were initially created in `~/.claude/skills/`
   - **Correct location:** `~/.factory/skills/` (where Claude Code discovers skills)

2. **Invalid skill.json Files**
   - Created `skill.json` files in each skill directory
   - **Problem:** Claude Code does NOT use skill.json - skills are discovered purely from `SKILL.md` files
   - These files were unnecessary and have been removed

3. **Missing --help in Wrapper Scripts**
   - `cursor-agent` and `gemini-agent` scripts did not handle `--help` flag
   - Caused failures when testing script invocation
   - **Fixed:** Added show_help() functions and --help handling

4. **Non-Executable Script**
   - `codex-agent/scripts/run_codex.sh` was not executable
   - **Fixed:** Applied chmod +x

## Fixes Applied

### 1. Removed skill.json Files
```bash
rm ~/.claude/skills/*/skill.json
```
- Removed all skill.json files as they are not used by Claude Code
- Skills are discovered via SKILL.md files only

### 2. Updated Wrapper Scripts
Fixed `cursor-agent/scripts/run_cursor.sh`:
- Added show_help() function
- Added --help/-h flag handling
- Added prompt requirement check with error message

Fixed `gemini-agent/scripts/run_gemini.sh`:
- Added show_help() function
- Added --help/-h flag handling
- Documented all modes and capabilities

### 3. Made All Scripts Executable
```bash
chmod +x ~/.factory/skills/codex-agent/scripts/run_codex.sh
```

### 4. Copied Skills to Correct Location
```bash
cp -r ~/.claude/skills/{copilot-agent,codex-agent,cursor-agent,gemini-agent,codex-subagent}/* \
  ~/.factory/skills/{copilot-agent,codex-agent,cursor-agent,gemini-agent,codex-subagent}/
```

## Verification Results

### All Skills Validated

✓ **copilot-agent**
- Location: `~/.factory/skills/copilot-agent/`
- Files: `SKILL.md`, `scripts/run_copilot.sh`
- Script: Executable, --help works
- Model: Claude Haiku 4.5 (locked)

✓ **codex-agent**
- Location: `~/.factory/skills/codex-agent/`
- Files: `SKILL.md`, `scripts/run_codex.sh`
- Script: Executable, delegates to codex-subagent
- Model: GPT-5.3 Codex (locked)

✓ **cursor-agent**
- Location: `~/.factory/skills/cursor-agent/`
- Files: `SKILL.md`, `scripts/run_cursor.sh`
- Script: Executable, --help works
- Model: Gemini 3 Flash

✓ **gemini-agent**
- Location: `~/.factory/skills/gemini-agent/`
- Files: `SKILL.md`, `scripts/run_gemini.sh`
- Script: Executable, --help works
- Context: 1M+ tokens

✓ **codex-subagent**
- Location: `~/.factory/skills/codex-subagent/`
- Files: `SKILL.md`, `README.md`, `references/`, `scripts/run_codex_subagent.sh`
- Script: Executable, --help works
- Model: Configurable (gpt-5.1-mini, gpt-5.2, gpt-5.3)

## Skill() Tool Invocation Syntax

### copilot-agent
```python
Skill(
  skill="copilot-agent",
  args="--prompt 'implement REST API endpoint' --mode programmatic --cd /path/to/project"
)
```

### codex-agent
```python
Skill(
  skill="codex-agent",
  args="--prompt 'refactor authentication module' --mode workspace-write --cd /path/to/project"
)
```

### cursor-agent
```python
Skill(
  skill="cursor-agent",
  args="--prompt 'design OAuth flow architecture' --mode plan --cd /path/to/project"
)
```

### gemini-agent
```python
Skill(
  skill="gemini-agent",
  args="--prompt 'scan for OWASP vulnerabilities' --mode read-only --cd /path/to/project"
)
```

### codex-subagent
```python
Skill(
  skill="codex-subagent",
  args="--prompt 'analyze test coverage gaps' --model gpt-5.1-codex-mini --mode read-only --cd /path/to/project"
)
```

## Key Learnings

1. **Claude Code Skill Discovery**
   - Skills must be in `~/.factory/skills/` directory
   - Only `SKILL.md` file is required (no skill.json)
   - Wrapper scripts referenced in SKILL.md must be executable

2. **Skill File Structure**
   ```
   ~/.factory/skills/{skill-name}/
   ├── SKILL.md              (required - skill documentation)
   ├── scripts/              (optional - wrapper scripts)
   │   └── run_*.sh         (executable wrappers)
   └── README.md            (optional - additional docs)
   ```

3. **Wrapper Script Best Practices**
   - Always include --help/-h flag handling
   - Provide clear usage documentation
   - Make scripts executable (chmod +x)
   - Use absolute paths when referencing other scripts
   - Include error handling and validation

4. **Model Locking Pattern**
   - Use wrapper scripts to enforce model selection
   - Log and ignore override attempts
   - Document model lock in SKILL.md

## Status: READY FOR USE

All 5 skill-based agents are now properly configured and ready for Skill() tool invocation.

## Testing Commands

```bash
# Test all wrapper scripts
~/.factory/skills/copilot-agent/scripts/run_copilot.sh --help
~/.factory/skills/codex-agent/scripts/run_codex.sh --help
~/.factory/skills/cursor-agent/scripts/run_cursor.sh --help
~/.factory/skills/gemini-agent/scripts/run_gemini.sh --help
~/.factory/skills/codex-subagent/scripts/run_codex_subagent.sh --help
```

All commands execute successfully with proper help output.
