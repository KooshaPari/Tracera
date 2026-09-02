import { fireEvent, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { Project } from "@tracertm/types";

import { ProjectsListView } from "@/views/ProjectsListView";

const mocks = vi.hoisted(() => ({
  search: {} as Record<string, unknown>,
  useProjects: vi.fn(),
}));

vi.mock("@tanstack/react-router", () => ({
  useSearch: () => mocks.search,
}));

vi.mock("@/hooks/useProjects", () => ({
  useProjects: mocks.useProjects,
}));

vi.mock("@/views/projects-list/ProjectCard", () => ({
  ProjectCard: ({ project, onEdit }: { project: Project; onEdit: (value: Project) => void }) => (
    <article data-testid="project-card">
      <span data-testid="project-name">{project.name}</span>
      <button type="button" onClick={() => onEdit(project)}>
        Edit {project.name}
      </button>
    </article>
  ),
}));

interface OpenDialogProps {
  open: boolean;
}

vi.mock("@/views/projects-list/CreateProjectDialog", () => ({
  CreateProjectDialog: ({ open }: OpenDialogProps) =>
    open ? <div role="dialog" aria-label="Create registry" /> : null,
}));

vi.mock("@/views/projects-list/EditProjectDialog", () => ({
  EditProjectDialog: ({ open, project }: OpenDialogProps & { project?: Project }) =>
    open ? <div role="dialog" aria-label={`Edit ${project?.name ?? "registry"}`} /> : null,
}));

vi.mock("@/views/projects-list/ExportDialog", () => ({
  ExportDialog: ({ open }: OpenDialogProps) =>
    open ? <div role="dialog" aria-label="Export registries" /> : null,
}));

vi.mock("@/views/projects-list/ImportDialog", () => ({
  ImportDialog: ({ open }: OpenDialogProps) =>
    open ? <div role="dialog" aria-label="Import registries" /> : null,
}));

const makeProject = (id: string, name: string, createdAt: string): Project =>
  ({ createdAt, id, name }) as Project;

const projects = [
  makeProject("older", "Zulu Registry", "2024-01-01T00:00:00.000Z"),
  makeProject("newer", "Alpha Registry", "2024-03-01T00:00:00.000Z"),
];

const renderView = (): ReturnType<typeof render> => render(<ProjectsListView />);

describe("ProjectsListView", () => {
  beforeEach(() => {
    mocks.search = {};
    mocks.useProjects.mockReset();
    mocks.useProjects.mockReturnValue({ data: projects, isLoading: false });
  });

  it("renders the current registry actions and project cards", () => {
    renderView();

    expect(screen.getByRole("heading", { name: "Project Registry" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Export" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Import" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "New Registry" })).toBeInTheDocument();
    expect(screen.getAllByTestId("project-card")).toHaveLength(2);
  });

  it("shows the loading state without rendering stale project content", () => {
    mocks.useProjects.mockReturnValue({ data: projects, isLoading: true });

    const { container } = renderView();

    expect(container.querySelector(".animate-pulse")).toBeInTheDocument();
    expect(screen.queryByText("Alpha Registry")).not.toBeInTheDocument();
  });

  it("shows the vacant state when no projects exist", () => {
    mocks.useProjects.mockReturnValue({ data: [], isLoading: false });

    renderView();

    expect(screen.getByText("Registry Vacant")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Clear Filters" })).not.toBeInTheDocument();
  });

  it("filters by registry name and restores the list when cleared", async () => {
    const user = userEvent.setup();
    renderView();

    await user.type(screen.getByPlaceholderText("Filter registries..."), "missing");

    expect(screen.getByText("Registry Vacant")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Clear Filters" }));
    expect(screen.getAllByTestId("project-card")).toHaveLength(2);
  });

  it("sorts by newest sync date by default and reverses the order", async () => {
    const user = userEvent.setup();
    renderView();

    const names = (): string[] =>
      screen
        .getAllByTestId("project-card")
        .map((card) => within(card).getByTestId("project-name").textContent ?? "");

    expect(names()).toEqual(["Alpha Registry", "Zulu Registry"]);
    await user.click(screen.getByRole("button", { name: "Reverse sort order" }));
    expect(names()).toEqual(["Zulu Registry", "Alpha Registry"]);
  });

  it("sorts by registry identifier", async () => {
    const user = userEvent.setup();
    renderView();

    await user.click(screen.getByRole("combobox"));
    await user.click(await screen.findByRole("option", { name: "Identifier" }));

    expect(screen.getAllByTestId("project-card").map((card) => card.textContent)).toEqual([
      "Zulu RegistryEdit Zulu Registry",
      "Alpha RegistryEdit Alpha Registry",
    ]);

    await user.click(screen.getByRole("button", { name: "Reverse sort order" }));
    expect(screen.getAllByTestId("project-card").map((card) => card.textContent)).toEqual([
      "Alpha RegistryEdit Alpha Registry",
      "Zulu RegistryEdit Zulu Registry",
    ]);
  });

  it.each([
    ["Export", "Export registries"],
    ["Import", "Import registries"],
    ["New Registry", "Create registry"],
  ])("opens the %s workflow", async (buttonName, dialogName) => {
    const user = userEvent.setup();
    renderView();

    await user.click(screen.getByRole("button", { name: buttonName }));

    expect(screen.getByRole("dialog", { name: dialogName })).toBeInTheDocument();
  });

  it("opens the create workflow from the route search action", () => {
    mocks.search = { action: "create" };

    renderView();

    expect(screen.getByRole("dialog", { name: "Create registry" })).toBeInTheDocument();
  });

  it("opens the selected registry editor", () => {
    renderView();

    fireEvent.click(screen.getByRole("button", { name: "Edit Alpha Registry" }));

    expect(screen.getByRole("dialog", { name: "Edit Alpha Registry" })).toBeInTheDocument();
  });
});
