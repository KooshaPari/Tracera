import { describe, expect, it } from "vitest";

import packageJson from "../../../package.json";
import frontendPackageJson from "../../../../../package.json";
import vitestConfig from "../../../vitest.config";

describe("Vitest execution profile", () => {
  it("keeps default and scripted test runs bounded for CI", () => {
    expect(vitestConfig.test?.reporters).toEqual(["dot"]);
    expect(vitestConfig.test?.ui).toBe(false);
    expect(packageJson.scripts.test).toBe("vitest run --reporter=dot --no-ui");
    expect(packageJson.scripts["test:watch"]).toBe("vitest --reporter=dot --no-ui");
    expect(packageJson.scripts["test:ui"]).toBe("vitest --ui --reporter=verbose");
    expect(frontendPackageJson.scripts["test:unit"]).toBe("npm --prefix apps/web test --");
  });

  it("ignores only the TanStack route whose public segment is named test", () => {
    const exclusions = vitestConfig.test?.exclude ?? [];

    expect(exclusions).toContain("src/routes/projects.$projectId.views.test.tsx");
    expect(exclusions.filter((pattern) => pattern.includes("routes"))).toEqual([
      "src/routes/projects.$projectId.views.test.tsx",
    ]);
  });
});
