# Chat / Agent History UI – Feature Enumeration (Reference)

Reference UIs reviewed for chat history and agent-related panels. Ideas borrowed for TraceRTM chat history (concepts, not copy).

## 1. Kilocode (agent/chat history)

**Location:** `API/research/kilocode/webview-ui` (history + chat).

### History view / panel
- **History tab/view** – Dedicated full view for “all past tasks/chats”.
- **Search** – Text search with placeholder; when search is active, sort can switch to “most relevant”.
- **Sort** – Newest, Oldest, Most expensive, Most tokens, Most relevant (disabled when no search).
- **Workspace filter** – Current workspace vs all workspaces.
- **Favorites filter** – Checkbox “Show favorites only”.
- **Selection mode** – Toggle to enter/exit; “Select all” / “Deselect all” with count (selected / total).
- **Batch delete** – In selection mode: “Clear selection”, “Delete selected”; confirmation dialog for batch delete.
- **Pagination** – Page index + total pages; Previous/Next buttons.
- **List** – Virtualized list (Virtuoso) of history items.
- **Item variants** – “Full” (in history view) and “compact” (in preview).
- **Per-item actions** – Delete (opens single delete dialog), toggle selection in selection mode.
- **History preview** – “Recent tasks” (e.g. first 4) + “View all history” link that switches to full history tab.
- **Done** – Button to leave history and return to main chat/task view.
- **Delete dialogs** – Single-task and batch-task delete with confirmation.

### Chat / task UI (adjacent to history)
- Task header, task actions, share, mode selector, checkpoints, follow-up suggestions, etc. (not duplicated in Trace; only history list concepts used).

---

## 2. OpenCode (prompt history)

**Location:** `API/research/opencode/packages/opencode` TUI.

- **Prompt history** – Persisted as JSONL file; last N entries (e.g. 50).
- **Navigation** – Move up/down in history (e.g. arrow keys) to reuse previous prompt + parts.
- **Append on send** – New prompt appended to history; file append for persistence.
- **Trim** – When over max entries, trim and rewrite file (self-heal).
- **No dedicated “history panel”** – Inline in prompt (keyboard-driven).

---

## 3. TraceRTM – Borrowed for Chat History

Implemented (or planned) in Trace:

- **History entry point** – Button in chat header (“Chat history” / list icon) that opens history.
- **History panel/drawer** – Slide-over or in-place panel listing **conversations** (from existing chat store).
- **List content** – Title, date (created/updated), optional message count; optional project badge if `projectId` set.
- **Search** – Filter conversations by title (and optionally by date range).
- **Sort** – Newest first (default), Oldest first.
- **Filter by project** – Optional: “Current project” vs “All” when context has `projectId`.
- **Click to open** – Select conversation → set active, close history, show that thread.
- **Delete** – Per-conversation delete (existing store action); optional selection mode + batch delete later.
- **Close / Done** – Return to current chat view.
- **Persistence** – Conversations already in `chatStore` (localStorage); no new backend.

---

## 4. Not Implemented (Future)

- Favorites per conversation.
- Pagination (if conversation count grows large).
- Export (e.g. copy thread, markdown).
- “Most relevant” sort (would require search backend or local embedding).
