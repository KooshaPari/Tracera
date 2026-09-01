import { describe, expect, it } from "vitest";

import packageJson from "../../../package.json";
import frontendPackageJson from "../../../../../package.json";
import vitestConfig from "../../../vitest.config";

describe("Vitest execution profile", () => {
  describe("CI invocation contract", () => {
    it("test script runs vitest in non-watch (run) mode", () => {
      const testScript = packageJson.scripts.test as string;
      // Must use `vitest run` to ensure bounded CI execution, not watch mode
      expect(testScript).toContain("vitest run");
      expect(testScript).not.toContain("vitest --watch");
      expect(testScript).not.toContain("vitest watch");
    });

    it("test:watch script enables watch mode for interactive development", () => {
      const watchScript = packageJson.scripts["test:watch"] as string;
      expect(watchScript).toContain("vitest");
      expect(watchScript).not.toContain("vitest run");
    });

    it("test:ui script enables the Vitest UI reporter", () => {
      const uiScript = packageJson.scripts["test:ui"] as string;
      expect(uiScript).toContain("--ui");
    });
  });

  describe("CI termination contract", () => {
    it("uses dot reporter for CI output (machine-parseable, non-verbose)", () => {
      const reporters = vitestConfig.test?.reporters;
      expect(reporters).toContain("dot");
    });

    it("disables UI browser interaction for CI runs", () => {
      const uiEnabled = vitestConfig.test?.ui;
      expect(uiEnabled).toBe(false);
    });

    it("test_unit script in root delegates to bounded vitest run", () => {
      const testUnitScript = frontendPackageJson.scripts["test:unit"] as string;
      expect(testUnitScript).toContain("vitest run");
    });
  });

  describe("include/exclude coverage for TanStack production route", () => {
    it("excludes the TanStack production /views/test route from test discovery", () => {
      const exclusions = vitestConfig.test?.exclude ?? [];
      const hasTestRouteExclusion = exclusions.some(
        (pattern) =>
          typeof pattern === "string" &&
          pattern.includes("projects.$projectId.views.test.tsx"),
      );
      expect(hasTestRouteExclusion).toBe(true);
    });

    it("excludes only one route pattern when filtering routes", () => {
      const exclusions = (vitestConfig.test?.exclude ?? []).filter((pattern) =>
        typeof pattern === "string" && pattern.includes("routes"),
      );
      expect(exclusions).toHaveLength(1);
      expect(exclusions[0]).toBe("src/routes/projects.$projectId.views.test.tsx");
    });

    it("includes standard test file patterns for test discovery", () => {
      const inclusions = vitestConfig.test?.include ?? [];
      expect(inclusions).toContain("src/**/*.{test,spec}.{ts,tsx}");
    });

    it("the excluded route is a real production route file, not a test file", () => {
      // projects.$projectId.views.test.tsx renders a real UI at path /projects/:projectId/views/test
      // It must be excluded so Vitest doesn't try to run it as a test suite
      const exclusions = vitestConfig.test?.exclude ?? [];
      const excludedRoute = exclusions.find(
        (p) =>
          typeof p === "string" && p === "src/routes/projects.$projectId.views.test.tsx",
      );
      expect(excludedRoute).toBeDefined();
    });
  });
});
