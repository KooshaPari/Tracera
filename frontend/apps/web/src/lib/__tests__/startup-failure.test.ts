import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import { renderFrontendStartupFailure } from "../startup-failure";

describe("renderFrontendStartupFailure", () => {
  beforeEach(() => {
    document.body.replaceChildren();
    const root = document.createElement("div");
    root.id = "root";
    document.body.append(root);
  });

  it("renders an accessible terminal state without error interpolation", () => {
    renderFrontendStartupFailure();

    expect(screen.getByRole("alert")).toHaveTextContent("Dashboard startup failed");
    expect(
      screen.getByRole("button", { name: "Reload the dashboard after a startup failure" }),
    ).toHaveTextContent("Reload dashboard");
    expect(document.querySelector("#root script")).toBeNull();
  });

  it("does nothing when the application root is unavailable", () => {
    document.querySelector("#root")?.remove();

    expect(() => renderFrontendStartupFailure()).not.toThrow();
  });
});
