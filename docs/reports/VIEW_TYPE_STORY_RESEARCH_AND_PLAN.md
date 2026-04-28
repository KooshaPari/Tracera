# View Type "story" — Research and Plan

**Issue:** Users see "Unknown view" / "Unknown view type: story" when navigating to `/projects/:projectId/views/story` or when an item with `view: "story"` (or `"STORY"`) leads to that URL.

**Status:** Research complete; minimal fix already applied (story → FEATURE_VIEW). This document records research and optional follow-ups.

---

## 1. Research Summary

### 1.1 Where the error comes from

- **Route:** `frontend/apps/web/src/routes/projects.$projectId.views.$viewType.tsx`
- **Behavior:** The route renders a component based on the `viewType` URL param. A `switch (viewType)` had no `case "story"`, so it fell through to `default` and showed "Unknown view" / "Unknown view type: story".

### 1.2 How `/views/story` is reached

1. **Item redirect:** `frontend/apps/web/src/routes/items.$itemId.tsx` redirects `/items/:itemId` → `/projects/:projectId/views/:viewType/:itemId` using `viewType: item.view.toLowerCase()`. If the API returns `item.view === "STORY"` or `"story"`, the URL becomes `.../views/story/...`.
2. **Direct links:** Tables, trees, kanban, search, and detail views build links like `/projects/${projectId}/views/${String(item.view || "feature").toLowerCase()}/${item.id}`. Again, if `item.view` is `"story"`, the link is `.../views/story/...`.
3. **Backend:** Items can have `view` set to values that normalize to `"story"`:
   - **Item model** (`src/tracertm/models/item.py`): `view` is a `String(50)` column (no enum); any string can be stored.
   - **Local storage** (`src/tracertm/storage/local_storage.py`): When ingesting markdown, items are created with `view=item_type` where `item_type` is one of `"epic"`, `"story"`, `"test"`, `"task"`. So items can have `view="story"`.
   - **Item repository** (`src/tracertm/repositories/item_repository.py`): Creates items with `view=view or item_type`, so `view` can be story-like depending on caller.

So both API data and URL construction can produce `viewType === "story"`; the route must handle it.

### 1.3 View type definitions across the stack

| Layer | Location | "story" as view? | Notes |
|-------|----------|-------------------|--------|
| **Backend enum** | `src/tracertm/services/view_registry_service.py` | No | `ViewType` has FEATURE, EPIC, CODE, TEST, etc. No STORY. |
| **Backend item.view** | `Item.view` (DB column) | Yes (in practice) | String column; local_storage and callers set `view=item_type` (e.g. "story"). |
| **Frontend URL viewType** | `projects.$projectId.views.$viewType.tsx` | Yes (after fix) | Lowercase URL param; switch now has `case "story"` → FEATURE_VIEW. |
| **Frontend form view** | `CreateItemForm` viewTypes | No | Uppercase list: FEATURE, CODE, TEST, ... "story" is an **item type** under FEATURE (epic, feature, story, task). |
| **Frontend constants** | `config/constants.ts` VIEW_TYPES | No | Uppercase API-style list; FEATURE has itemTypes including "story". |

Conclusion: **"story" is an item type under the FEATURE view**, but the backend and URLs can also use "story" as a **view** value. The frontend route must accept `viewType === "story"` and map it to a known view (FEATURE is the right target).

### 1.4 Other places that use viewType

- **Breadcrumb** (`Breadcrumb.tsx`): Uses `params.viewType`; no allowlist. "story" will now show as "Story" in breadcrumb (title-cased).
- **GraphViewContainer / GraphView**: Use `item.view` (lowercased) for links; no route allowlist there.
- **Redirect tests** (`redirects.test.tsx`): Test uppercase → lowercase (e.g. "TEST" → "test"); no test for "story" yet.
- **Command palette**: Hardcodes viewType to feature/code/test/workflows when navigating to views; no "story" entry (not required if story → feature).

No other code path was found that validates viewType against a fixed list before navigation; the only gate was the route switch.

---

## 2. Plan

### 2.1 Recommended approach (implemented)

- **Treat "story" as an alias for the feature view.**
- **Change:** In `projects.$projectId.views.$viewType.tsx`, add `case "story":` next to `case "feature":` and render the same `FEATURE_VIEW`.
- **Result:** `/projects/:id/views/story` and `/projects/:id/views/story/:itemId` work without a dedicated Story view or new route. Feature view already supports story-type items (epic, feature, story, task).

This is the minimal, correct fix and is already in place.

### 2.2 Optional follow-ups

| Priority | Action | Rationale |
|----------|--------|-----------|
| Low | Add a unit test for `viewType === "story"` in the route (or redirect test with item.view "STORY" → path contains `/views/story/`) | Prevents regressions. |
| Low | Document in a short “URL view types” reference that `story` is an alias for `feature`. | Helps future maintainers. |
| Optional | Single source of truth for valid URL view types (e.g. array + switch generated from it) | Reduces drift; many view types today only live in the switch. |
| Optional | Backend: align Item.view with ViewType (e.g. normalize "story" → "FEATURE" on read/write) or add STORY to ViewType and registry | Only if product wants "story" as a first-class view in the API; current fix does not require it. |

### 2.3 What not to do

- **Do not** remove or block `viewType === "story"` in the route; items and redirects can produce this URL.
- **Do not** add a dedicated Story view page unless product explicitly requests a different UX for "story" vs "feature"; alias is sufficient for correctness.

---

## 3. Summary

- **Root cause:** Route had no handler for `viewType === "story"`; URLs with `.../views/story` or `.../views/story/:itemId` hit the default case.
- **Fix:** Map `"story"` to `FEATURE_VIEW` in `projects.$projectId.views.$viewType.tsx` (done).
- **Optional:** Add test for story view type, document story ↔ feature alias, consider a single allowlist for URL view types and/or backend alignment later.
