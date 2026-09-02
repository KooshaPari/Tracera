import { describe, expect, it } from "vitest";

import { isProtectedBackendPath } from "../../api/client-core";

describe(isProtectedBackendPath, () => {
  it.each([
    "/api/v1/coverage-matrix",
    "/evidence",
    "/evidence/ev-123",
    "/sdlc-pm/sprints",
    "/org-intel/teams",
  ])("recognizes protected Tracera backend route %s", (pathname) => {
    expect(isProtectedBackendPath(pathname)).toBe(true);
  });

  it.each(["/health", "/ready", "/assets/app.js", "/not-a-tracera-route"])(
    "does not attach bearer credentials to public or static route %s",
    (pathname) => {
      expect(isProtectedBackendPath(pathname)).toBe(false);
    },
  );
});
