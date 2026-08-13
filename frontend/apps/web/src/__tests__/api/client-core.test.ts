import { describe, expect, it } from "vitest";

import { clientCore } from "@/api/client-core";
import { API_ORIGIN } from "@/config/api-origin";

describe("clientCore", () => {
  it("returns the configured backend origin for a backend path", () => {
    expect(clientCore.getBackendURL("/api/v1/evidence")).toBe(API_ORIGIN);
  });
});
