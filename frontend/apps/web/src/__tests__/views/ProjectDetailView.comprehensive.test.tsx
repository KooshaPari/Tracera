/**
 * Comprehensive Tests for ProjectDetailView
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useItems } from "../../hooks/useItems";
import { useLinks } from "../../hooks/useLinks";
import { useProject } from "../../hooks/useProjects";
import { ProjectDetailView } from "../../views/ProjectDetailView";

// Mock TanStack Router
vi.mock("@tanstack/react-router", async () => {
  const actual = await vi.importActual("@tanstack/react-router");
  return {
    ...actual,
    Link: ({ children, to }: any) => (
      <a href={typeof to === "string" ? to : to.toString()}>{children}</a>
    ),
    useNavigate: () => vi.fn(),
    useParams: () => ({ projectId: "proj-1" }),
    useSearch: () => ({}),
  };
});

vi.mock("../../hooks/useItems", () => ({
  useItems: vi.fn(),
}));

vi.mock("../../hooks/useLinks", () => ({
  useLinks: vi.fn(),
}));

vi.mock("../../hooks/useProjects", () => ({
  useProject: vi.fn(),
  useUpdateProject: vi.fn(),
}));

describe(ProjectDetailView, () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        mutations: { retry: false },
        queries: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  it("renders project detail with tabs", () => {
    vi.mocked(useProject).mockReturnValue({
      data: {
        description: "Test description",
        id: "proj-1",
        name: "Test Project",
      },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useItems).mockReturnValue({
      data: { items: [], total: 0 },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useLinks).mockReturnValue({
      data: { links: [], total: 0 },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ProjectDetailView />
      </QueryClientProvider>,
    );

    // Text appears multiple times, use getAllByText
    expect(screen.getAllByText("Test Project").length).toBeGreaterThan(0);
  });

  it("displays project statistics", () => {
    vi.mocked(useProject).mockReturnValue({
      data: {
        id: "proj-1",
        name: "Test Project",
      },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useItems).mockReturnValue({
      data: {
        items: [
          { id: "item-1", status: "todo", title: "Item 1", type: "feature" },
          { id: "item-2", status: "done", title: "Item 2", type: "feature" },
        ],
        total: 2,
      },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useLinks).mockReturnValue({
      data: { links: [{ id: "link-1" }], total: 1 },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ProjectDetailView />
      </QueryClientProvider>,
    );

    expect(screen.getByText(/Total Items/i)).toBeInTheDocument();
  });

  it("exposes project views", () => {
    vi.mocked(useProject).mockReturnValue({
      data: {
        id: "proj-1",
        name: "Test Project",
      },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useItems).mockReturnValue({
      data: { items: [], total: 0 },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useLinks).mockReturnValue({
      data: { links: [], total: 0 },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ProjectDetailView />
      </QueryClientProvider>,
    );

    expect(screen.getByRole("link", { name: "Features" })).toHaveAttribute(
      "href",
      "/projects/proj-1/views/feature",
    );
    expect(screen.getByRole("link", { name: "Traceability" })).toHaveAttribute(
      "href",
      "/projects/proj-1/views/graph",
    );
  });

  it("displays items by type", () => {
    vi.mocked(useProject).mockReturnValue({
      data: {
        id: "proj-1",
        name: "Test Project",
      },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useItems).mockReturnValue({
      data: {
        items: [
          {
            id: "item-1",
            priority: "high",
            status: "todo",
            title: "Feature 1",
            type: "feature",
          },
          {
            id: "item-2",
            priority: "medium",
            status: "in_progress",
            title: "Requirement 1",
            type: "requirement",
          },
        ],
        total: 2,
      },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useLinks).mockReturnValue({
      data: { links: [], total: 0 },
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <ProjectDetailView />
      </QueryClientProvider>,
    );

    expect(screen.getByText("Feature 1")).toBeInTheDocument();
  });
});
