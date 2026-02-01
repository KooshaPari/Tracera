# Dependency Cleanup: Textual Removal

**Date**: 2026-01-30
**Status**: ✅ Removed unused dependency

---

## Issue

Textual (TUI framework) was listed as a dependency but **never used** in the codebase.

### Analysis
- **Declared**: ✅ Listed in `pyproject.toml`
- **Installed**: ✅ Version 7.5.0 (5.2MB installed size)
- **Imported**: ❌ Zero imports in entire codebase
- **Used**: ❌ No TUI apps, screens, or widgets

### What We Actually Use
```python
# CLI framework
typer[all]>=0.21.1

# Terminal output (tables, colors, progress)
rich>=14.3.1
```

**Textual is for building interactive TUI apps** (like `htop`, `lazygit`).
**We're building a standard CLI** with commands and output.

---

## Changes Made

### 1. Removed from Dependencies
**File**: `pyproject.toml`

```diff
- "textual>=7.5.0",
```

### 2. Removed from Allow-Direct-References
**File**: `pyproject.toml`

```diff
- "textual.*",
```

---

## Impact

### Before
```bash
pip list | grep textual
# textual  7.5.0  (5.2MB)
```

### After
```bash
pip install -e .
# textual no longer installed
```

**Savings**: ~5.2MB installed size

---

## Verification

```bash
# No imports should exist
grep -r "from textual\|import textual" . --include="*.py" --exclude-dir={.venv,node_modules,ARCHIVE}
# Expected: No results

# Reinstall dependencies
pip install -e .

# Confirm textual removed
pip list | grep textual
# Expected: No results
```

---

## Why This Happened

Likely scenarios:
1. **Future-proofing**: Added for potential TUI features that were never built
2. **Copy-paste**: Copied from another project's dependencies
3. **Exploration**: Tried Textual during development, decided not to use it

---

## Related Dependencies (Kept)

| Package | Purpose | Status |
|---------|---------|--------|
| `typer[all]` | CLI framework (commands, args, help) | ✅ **Essential** |
| `rich` | Terminal output (tables, colors, progress) | ✅ **Essential** |
| ~~`textual`~~ | ~~TUI apps (screens, widgets, events)~~ | ❌ **Removed** |

---

## Recommendation

If you ever need **interactive TUI features** (like a dashboard that updates live), you could re-add Textual. But for standard CLI commands with output, **Typer + Rich is the perfect stack**.

**Current Stack is Optimal**: ✅ Typer + Rich
