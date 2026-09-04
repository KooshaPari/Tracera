<script lang="ts">
  /**
   * Tracera desktop shell — Svelte entry point.
   *
   * This component is intentionally minimal: it provides the layout
   * chrome (header, sidebar, status pill) and delegates the actual work
   * to child components that talk to the Tracera REST API via Tauri
   * commands or direct fetch().
   *
   * Why Svelte instead of the React app already in ``apps/web``?
   * The Tauri shell is supposed to be tiny — no router, no virtual DOM,
   * no state-management library. Svelte compiles away, so the bundle
   * ships almost nothing extra to the desktop webview.
   */

  import { onMount } from "svelte";

  // ---------------------------------------------------------------------------
  // Reactive state
  // ---------------------------------------------------------------------------

  let serviceStatus: "starting" | "ready" | "error" = "starting";
  let servicePid: number | null = null;
  let lastError: string | null = null;
  let searchValue: string = "";
  let searchFocused: boolean = false;

  // ---------------------------------------------------------------------------
  // Tauri bindings (typed loosely because @tauri-apps/api is not in the
  // shell's dependency tree — we call the global ``__TAURI__`` API).
  // ---------------------------------------------------------------------------

  interface TauriGlobal {
    core: {
      invoke: (cmd: string, args?: Record<string, unknown>) => Promise<unknown>;
    };
    event: {
      listen: (
        event: string,
        handler: (e: { payload: unknown }) => void,
      ) => Promise<() => void>;
    };
  }

  function tauri(): TauriGlobal | null {
    if (typeof window === "undefined") return null;
    // Tauri exposes its API under window.__TAURI__ when withGlobalTauri
    // is enabled in tauri.conf.json.
    const w = window as unknown as { __TAURI__?: TauriGlobal };
    return w.__TAURI__ ?? null;
  }

  // ---------------------------------------------------------------------------
  // Lifecycle
  // ---------------------------------------------------------------------------

  onMount(async () => {
    const t = tauri();
    if (!t) {
      serviceStatus = "error";
      lastError = "window.__TAURI__ is not available — not running inside the desktop shell";
      return;
    }

    try {
      servicePid = (await t.core.invoke("service_pid")) as number | null;
      serviceStatus = "ready";
    } catch (err) {
      serviceStatus = "error";
      lastError = String(err);
    }

    // Forward tray-originated events to local handlers.
    await t.event.listen("tracera://focus-search", () => {
      searchFocused = true;
      // The actual focus is done via a CSS :focus binding below; this
      // just nudges Svelte to re-render.
    });

    await t.event.listen("tracera://open-settings", () => {
      // Placeholder — the real settings component lives outside this
      // minimal scaffold.
      console.info("settings event received");
    });
  });

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  function statusColor(s: typeof serviceStatus): string {
    switch (s) {
      case "ready":
        return "var(--color-status-ready, #22c55e)";
      case "starting":
        return "var(--color-status-starting, #f59e0b)";
      case "error":
        return "var(--color-status-error, #ef4444)";
    }
  }

  function statusLabel(s: typeof serviceStatus): string {
    switch (s) {
      case "ready":
        return "ready";
      case "starting":
        return "starting…";
      case "error":
        return "error";
    }
  }
</script>

<main class="tracera-shell" data-testid="tracera-shell">
  <header class="shell-header">
    <div class="brand">
      <span class="brand-mark" aria-hidden="true">◆</span>
      <h1 class="brand-name">Tracera</h1>
    </div>

    <div class="search">
      <input
        type="search"
        bind:value={searchValue}
        placeholder="Search items, links, journeys…"
        aria-label="Search"
        class:search-focused={searchFocused}
        on:blur={() => (searchFocused = false)}
      />
      <kbd class="shortcut">⌘K</kbd>
    </div>

    <div class="status" data-testid="service-status">
      <span class="status-dot" style:background={statusColor(serviceStatus)} aria-hidden="true"></span>
      <span class="status-text">Service: {statusLabel(serviceStatus)}</span>
      {#if servicePid !== null}
        <span class="status-pid" title="Companion service PID">pid {servicePid}</span>
      {/if}
    </div>
  </header>

  <section class="shell-body">
    <aside class="sidebar">
      <nav>
        <ul>
          <li><a href="#items">Items</a></li>
          <li><a href="#links">Links</a></li>
          <li><a href="#journeys">Journeys</a></li>
          <li><a href="#graph">Graph</a></li>
          <li><a href="#impact">Impact</a></li>
        </ul>
      </nav>
    </aside>

    <div class="content" role="region" aria-label="Main content">
      {#if serviceStatus === "error"}
        <div class="error-card" role="alert">
          <strong>Companion service unavailable</strong>
          <p>{lastError ?? "unknown error"}</p>
          <p class="hint">
            Start the backend with <code>tracera serve</code> or the
            <code>tracera-os-service</code> daemon.
          </p>
        </div>
      {:else if serviceStatus === "starting"}
        <p class="placeholder">Waiting for the Tracera companion service…</p>
      {:else}
        <p class="placeholder">
          Welcome to Tracera. Pick a section from the sidebar to begin.
        </p>
      {/if}
    </div>
  </section>

  <footer class="shell-footer">
    <span>Tracera Desktop — native shell for the Tracera web UI.</span>
    <span class="env" title="Runtime identifier">env: tauri-desktop</span>
  </footer>
</main>

<style>
  :global(:root) {
    --color-bg: #0f172a;
    --color-bg-elevated: #1e293b;
    --color-text: #e2e8f0;
    --color-text-muted: #94a3b8;
    --color-accent: #38bdf8;
    --color-status-ready: #22c55e;
    --color-status-starting: #f59e0b;
    --color-status-error: #ef4444;
    --radius: 6px;
  }

  .tracera-shell {
    display: grid;
    grid-template-rows: auto 1fr auto;
    height: 100vh;
    font-family:
      "Inter", "SF Pro Text", system-ui, -apple-system, "Segoe UI", sans-serif;
    background: var(--color-bg);
    color: var(--color-text);
  }

  .shell-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--color-bg-elevated);
    background: var(--color-bg-elevated);
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .brand-mark {
    color: var(--color-accent);
    font-size: 1.25rem;
  }
  .brand-name {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.02em;
  }

  .search {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--color-bg);
    border-radius: var(--radius);
    padding: 0.25rem 0.5rem;
  }
  .search input {
    flex: 1;
    background: transparent;
    border: 0;
    color: inherit;
    font: inherit;
    outline: none;
    padding: 0.25rem 0.25rem;
  }
  .search-focused input {
    /* Highlight when the tray fired a focus event. */
    box-shadow: 0 0 0 1px var(--color-accent);
    border-radius: var(--radius);
  }
  .shortcut {
    color: var(--color-text-muted);
    background: var(--color-bg-elevated);
    border-radius: 4px;
    padding: 0 0.4rem;
    font-family: ui-monospace, "SFMono-Regular", monospace;
    font-size: 0.75rem;
  }

  .status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--color-text-muted);
    font-size: 0.85rem;
  }
  .status-dot {
    width: 0.6rem;
    height: 0.6rem;
    border-radius: 999px;
  }
  .status-pid {
    color: var(--color-text-muted);
    font-family: ui-monospace, "SFMono-Regular", monospace;
    font-size: 0.75rem;
  }

  .shell-body {
    display: grid;
    grid-template-columns: 12rem 1fr;
    overflow: hidden;
  }

  .sidebar {
    background: var(--color-bg-elevated);
    padding: 1rem 0.5rem;
  }
  .sidebar ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  .sidebar a {
    display: block;
    padding: 0.5rem 0.75rem;
    border-radius: var(--radius);
    color: var(--color-text-muted);
    text-decoration: none;
  }
  .sidebar a:hover {
    background: var(--color-bg);
    color: var(--color-text);
  }

  .content {
    padding: 1.5rem;
    overflow: auto;
  }

  .error-card {
    border: 1px solid var(--color-status-error);
    background: rgba(239, 68, 68, 0.08);
    border-radius: var(--radius);
    padding: 1rem;
  }
  .hint {
    color: var(--color-text-muted);
    font-size: 0.85rem;
  }

  .placeholder {
    color: var(--color-text-muted);
  }

  .shell-footer {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 1rem;
    border-top: 1px solid var(--color-bg-elevated);
    font-size: 0.75rem;
    color: var(--color-text-muted);
  }
  .env {
    font-family: ui-monospace, "SFMono-Regular", monospace;
  }
</style>