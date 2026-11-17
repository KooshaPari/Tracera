import { describe, expect, it } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { W9Unavailable, unavailableW9Views } from "./W9Unavailable";

describe("unavailable resource views", () => {
  it.each([...unavailableW9Views])("labels %s without mounting its zero-filled content", (view) => {
    render(
      <W9Unavailable path={`/projects/p/views/${view}`}>
        <span>Fake zero metrics</span>
      </W9Unavailable>,
    );
    expect(screen.getByRole("status").textContent).toContain("Not implemented yet");
    expect(screen.queryByText("Fake zero metrics")).toBeNull();
    cleanup();
  });
  it("preserves implemented views", () => {
    render(
      <W9Unavailable path="/projects/p/views/code">
        <span>Persisted items</span>
      </W9Unavailable>,
    );
    expect(screen.getByText("Persisted items")).toBeDefined();
    cleanup();
  });
});
