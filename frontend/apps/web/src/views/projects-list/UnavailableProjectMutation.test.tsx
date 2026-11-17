import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { Project } from "@tracertm/types";
import { CreateProjectDialog } from "./CreateProjectDialog";
import { EditProjectDialog } from "./EditProjectDialog";
import { ProjectDeleteDialog } from "./ProjectDeleteDialog";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("unavailable project writes", () => {
  it.each(["create", "edit", "delete"])("labels %s without offering a false write", (operation) => {
    const fetch = vi.fn();
    vi.stubGlobal("fetch", fetch);
    const props = { open: true, onOpenChange: vi.fn() };
    const project = { id: "persisted-project" } as Project;
    render(
      operation === "create" ? (
        <CreateProjectDialog {...props} />
      ) : operation === "edit" ? (
        <EditProjectDialog {...props} project={project} />
      ) : (
        <ProjectDeleteDialog {...props} project={project} onClosed={vi.fn()} />
      ),
    );
    expect(screen.getByRole("status").textContent).toContain("Not implemented yet");
    expect(screen.queryByRole("textbox")).toBeNull();
    expect(screen.queryByRole("button", { name: /initialize|save|delete$/i })).toBeNull();
    expect(fetch).not.toHaveBeenCalled();
  });
});
