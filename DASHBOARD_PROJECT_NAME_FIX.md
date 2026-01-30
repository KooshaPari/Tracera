# Dashboard Project Name Fix

**Date:** 2026-01-28

---

## ✅ Issue Fixed

**Problem:** Project slugs like `proj_staynest_001` were being displayed instead of human-readable names in the dashboard and throughout the application.

**Solution:** Created a utility function to convert project slugs/IDs to human-readable names and updated all views to use it.

---

## Changes Made

### 1. Created Project Name Utility (`frontend/apps/web/src/lib/project-name-utils.ts`)

- **`slugToDisplayName(slugOrName: string)`**: Converts slugs like `proj_staynest_001` → `StayNest Project`
- **`getProjectDisplayName(project)`**: Gets display name from project object, preferring `name` field if human-readable, otherwise converting ID

**Examples:**
- `proj_staynest_001` → `StayNest Project`
- `proj_todo_graph_001` → `Todo Graph Project`
- `proj_myapp_002` → `MyApp Project`
- `My Project Name` → `My Project Name` (already human-readable, returns as-is)

### 2. Updated Views

All views that display project names now use `getProjectDisplayName()`:

- ✅ **DashboardView.tsx** - Main dashboard with project cards, charts, and lists
- ✅ **ProjectsListView.tsx** - Projects list view
- ✅ **ProjectDetailView.tsx** - Project detail page header
- ✅ **SettingsView.tsx** - Settings project selector
- ✅ **ProjectSettingsView.tsx** - Project settings page

---

## How It Works

1. **Checks if name is human-readable**: If `project.name` exists and doesn't match the slug pattern (`proj_[a-z0-9_]+`), it uses the name as-is.

2. **Converts slug to display name**: 
   - Removes `proj_` prefix
   - Removes trailing numeric parts (like `001`, `002`)
   - Converts remaining parts to title case
   - Adds "Project" suffix

3. **Handles edge cases**: Works with snake_case, kebab-case, camelCase, and PascalCase formats.

---

## Testing

The fix handles:
- ✅ Projects with slug IDs (`proj_staynest_001`)
- ✅ Projects with human-readable names already set
- ✅ Projects with mixed case slugs
- ✅ Projects with numeric suffixes
- ✅ Edge cases (empty names, null values)

---

## Result

All project names in the dashboard and throughout the application now display as human-readable names instead of technical slugs.

**Before:** `proj_staynest_001`  
**After:** `StayNest Project`
