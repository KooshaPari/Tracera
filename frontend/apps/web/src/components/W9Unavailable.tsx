import type { ReactNode } from "react";
import { NotImplemented } from "./Availability";

// These views depend on operations absent from the SQLite Store contract.
// Do not mount their metric cards, demo fixtures, or mutation controls.
export const unavailableW9Views = new Set([
  "integrations",
  "test",
  "test-runs",
  "test-cases",
  "test-suites",
  "problem",
  "process",
  "qa-dashboard",
  "webhooks",
  "coverage",
  "journey",
]);

export function W9Unavailable({ path, children }: { path: string; children: ReactNode }) {
  const view = /\/views\/([^/]+)/.exec(path)?.[1];
  const unavailable =
    (view !== undefined && unavailableW9Views.has(view)) ||
    /^\/(reports|notifications|processes|test-runs|test-cases|test-suites|integrations|webhooks|agents|search|chat)(\/|$)/.test(
      path,
    ) ||
    /^\/projects\/[^/]+\/(agents|equivalence|temporal|specifications|compliance)(\/|$)/.test(path);
  if (!unavailable) return children;
  return (
    <section aria-label="Capability unavailable">
      <NotImplemented />
    </section>
  );
}
