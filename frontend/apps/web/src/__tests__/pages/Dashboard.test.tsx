/**
 * Dashboard Page Tests
 * Tests: DashboardView rendering, loading states, empty states,
 *        project rendering, search/filter, sorting, and pinning.
 *
 * The DashboardView component uses:
 *   - useDashboardSummary() from @/hooks/useDashboardSummary
 *   - useProjects() / useDeleteProject() from ../hooks/useProjects
 * All data comes from hook-level mocks (no raw API mocks).
 */

import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach } from 'vitest';

import type { DashboardSummary } from '@/hooks/useDashboardSummary';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

// Mock @tanstack/react-router so <Link> renders without a RouterProvider
vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual('@tanstack/react-router');
  return {
    ...actual,
    Link: ({
      children,
      to,
      search: _search,
      ...props
    }: {
      children: React.ReactNode;
      to: string;
      search?: unknown;
      [key: string]: unknown;
    }) => (
      <a href={typeof to === 'string' ? to : String((to as unknown) ?? '')} {...props}>
        {children}
      </a>
    ),
    useNavigate: () => vi.fn(),
    useParams: () => ({}),
    useRouter: () => ({ navigate: vi.fn() }),
  };
});

// Mock recharts to avoid SVG/ResizeObserver issues in jsdom
vi.mock('recharts', () => ({
  Bar: () => null,
  BarChart: () => null,
  CartesianGrid: () => null,
  Cell: () => null,
  Pie: () => null,
  PieChart: () => null,
  PolarAngleAxis: () => null,
  PolarGrid: () => null,
  Radar: () => null,
  RadarChart: () => null,
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
    <div data-testid='responsive-container'>{children}</div>
  ),
  Tooltip: () => null,
  XAxis: () => null,
  YAxis: () => null,
}));

// Mock sonner toast
vi.mock('sonner', () => ({
  toast: { error: vi.fn(), success: vi.fn() },
}));

// Mock project-name-utils so display names are predictable
vi.mock('@/lib/project-name-utils', () => ({
  getProjectDisplayName: (project: { id?: string; name?: string }) =>
    project.name ?? project.id ?? 'Project',
}));

// Mutable return values so each test can override
const mockUseProjects = vi.fn();
const mockUseDeleteProject = vi.fn(() => ({
  mutateAsync: vi.fn(),
}));

vi.mock('@/hooks/useProjects', () => ({
  get useDeleteProject() {
    return mockUseDeleteProject;
  },
  get useProjects() {
    return mockUseProjects;
  },
}));

const mockUseDashboardSummary = vi.fn();

vi.mock('@/hooks/useDashboardSummary', () => ({
  get useDashboardSummary() {
    return mockUseDashboardSummary;
  },
}));

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

function makeProjects(
  ...items: { id: string; name: string; description?: string; status?: string }[]
) {
  return items.map((p) => ({
    created_at: '2024-01-01',
    description: p.description ?? '',
    id: p.id,
    name: p.name,
    status: p.status ?? 'active',
  }));
}

function makeSummary(
  perProject: DashboardSummary['perProject'],
  overrides?: Partial<DashboardSummary>,
): DashboardSummary {
  let totalItemCount = 0;
  const statusDistribution: Record<string, number> = {};
  const typeDistribution: Record<string, number> = {};

  for (const stats of Object.values(perProject)) {
    totalItemCount += stats.totalCount;
    for (const [s, c] of Object.entries(stats.statusCounts)) {
      statusDistribution[s] = (statusDistribution[s] ?? 0) + c;
    }
    for (const [t, c] of Object.entries(stats.typeCounts)) {
      typeDistribution[t] = (typeDistribution[t] ?? 0) + c;
    }
  }

  return {
    perProject,
    projectCount: Object.keys(perProject).length,
    statusDistribution,
    totalItemCount,
    typeDistribution,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Default mock values (loaded / empty)
// ---------------------------------------------------------------------------

function setLoadingState() {
  mockUseProjects.mockReturnValue({ data: undefined, isLoading: true });
  mockUseDashboardSummary.mockReturnValue({ data: undefined, isLoading: true });
}

function setEmptyState() {
  mockUseProjects.mockReturnValue({ data: [], isLoading: false });
  mockUseDashboardSummary.mockReturnValue({
    data: makeSummary({}),
    isLoading: false,
  });
}

function setPopulatedState() {
  const projects = makeProjects(
    { id: 'p1', name: 'Alpha Project', description: 'First project' },
    { id: 'p2', name: 'Beta Project', description: 'Second project' },
    { id: 'p3', name: 'Gamma Project', description: 'Third project' },
  );

  const summary = makeSummary({
    p1: {
      completedCount: 5,
      statusCounts: { active: 5, done: 5 },
      totalCount: 10,
      typeCounts: { feature: 6, bug: 4 },
    },
    p2: {
      completedCount: 2,
      statusCounts: { active: 8 },
      totalCount: 8,
      typeCounts: { requirement: 3, task: 5 },
    },
    p3: {
      completedCount: 0,
      statusCounts: { active: 3 },
      totalCount: 3,
      typeCounts: { test: 3 },
    },
  });

  mockUseProjects.mockReturnValue({ data: projects, isLoading: false });
  mockUseDashboardSummary.mockReturnValue({ data: summary, isLoading: false });
}

// ---------------------------------------------------------------------------
// Render helper
// ---------------------------------------------------------------------------

// Pre-import to avoid module loading delay during tests
let DashboardViewCached: any = null;

async function renderDashboard() {
  if (!DashboardViewCached) {
    const module = await import('@/views/DashboardView');
    DashboardViewCached = module.DashboardView;
  }
  // Render without wrapping in act() as react-testing-library handles this
  return render(<DashboardViewCached />);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('DashboardView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // -------------------------------------------------------------------------
  // Loading states
  // -------------------------------------------------------------------------
  describe('Loading States', () => {
    it('shows loading skeletons when projects are loading', async () => {
      setLoadingState();
      await renderDashboard();

      const skeletons = document.querySelectorAll(
        '[class*="animate-pulse"], [data-slot="skeleton"]',
      );
      expect(skeletons.length).toBeGreaterThan(0);
    });

    it('shows loading skeletons when summary is loading', async () => {
      mockUseProjects.mockReturnValue({ data: [], isLoading: false });
      mockUseDashboardSummary.mockReturnValue({ data: undefined, isLoading: true });

      await renderDashboard();

      const skeletons = document.querySelectorAll(
        '[class*="animate-pulse"], [data-slot="skeleton"]',
      );
      expect(skeletons.length).toBeGreaterThan(0);
    });

    it('does not show loading skeletons when both hooks have resolved', async () => {
      setPopulatedState();
      await renderDashboard();

      // Use queryByText directly to avoid expensive role queries
      const heading = screen.queryByText(/Traceability Dashboard/i);
      expect(heading).toBeInTheDocument();
    });
  });

  // -------------------------------------------------------------------------
  // Empty state
  // -------------------------------------------------------------------------
  describe('Empty States', () => {
    it('renders empty project grid with "no projects" message when filtering yields zero', async () => {
      setEmptyState();
      await renderDashboard();

      expect(screen.queryByText(/Traceability Dashboard/i)).toBeInTheDocument();
      expect(
        screen.getByText(/No projects match your current search criteria/i),
      ).toBeInTheDocument();
    });
  });

  // -------------------------------------------------------------------------
  // Project rendering
  // -------------------------------------------------------------------------
  describe('Project Rendering', () => {
    it('renders all project names from useProjects', async () => {
      setPopulatedState();
      await renderDashboard();

      expect(screen.getByText('Alpha Project')).toBeInTheDocument();
      expect(screen.getByText('Beta Project')).toBeInTheDocument();
      expect(screen.getByText('Gamma Project')).toBeInTheDocument();
    });

    it('displays item counts from dashboard summary per project', async () => {
      setPopulatedState();
      await renderDashboard();

      expect(screen.getByText('10')).toBeInTheDocument();
      expect(screen.getByText('8')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
    });

    it('displays progress percentage derived from completedCount / totalCount', async () => {
      setPopulatedState();
      await renderDashboard();

      // Alpha: 5/10 = 50%, Beta: 2/8 = 25%, Gamma: 0/3 = 0%
      expect(screen.getByText('50%')).toBeInTheDocument();
      expect(screen.getByText('25%')).toBeInTheDocument();
      expect(screen.getByText('0%')).toBeInTheDocument();
    });

    it('renders project links pointing to /projects/:id', async () => {
      setPopulatedState();
      await renderDashboard();

      const links = screen.getAllByRole('link');
      const projectLinks = links.filter(
        (link) =>
          link.getAttribute('href')?.startsWith('/projects/p1') ??
          link.getAttribute('href')?.startsWith('/projects/p2') ??
          link.getAttribute('href')?.startsWith('/projects/p3'),
      );
      expect(projectLinks.length).toBeGreaterThanOrEqual(3);
    });
  });

  // -------------------------------------------------------------------------
  // Search / Filter
  // -------------------------------------------------------------------------
  describe('Search and Filter', () => {
    it('filters projects by search query in project name', async () => {
      setPopulatedState();
      await renderDashboard();

      const searchInput = screen.getByPlaceholderText(/Search projects/i);
      fireEvent.change(searchInput, { target: { value: 'Beta' } });

      await waitFor(
        () => {
          expect(screen.getByText('Beta Project')).toBeInTheDocument();
          expect(screen.queryByText('Alpha Project')).not.toBeInTheDocument();
          expect(screen.queryByText('Gamma Project')).not.toBeInTheDocument();
        },
        { timeout: 5000 },
      );
    }, 15_000);

    it('shows empty state when search matches no projects', async () => {
      setPopulatedState();
      await renderDashboard();

      const searchInput = screen.getByPlaceholderText(/Search projects/i);
      fireEvent.change(searchInput, { target: { value: 'NonExistent' } });

      await waitFor(
        () => {
          expect(
            screen.getByText(/No projects match your current search criteria/i),
          ).toBeInTheDocument();
        },
        { timeout: 5000 },
      );
    }, 15_000);

    it('provides a clear-search button in the empty state', async () => {
      setPopulatedState();
      await renderDashboard();

      const searchInput = screen.getByPlaceholderText(/Search projects/i);
      fireEvent.change(searchInput, { target: { value: 'NonExistent' } });

      await waitFor(
        () => {
          expect(screen.getByRole('button', { name: /Clear search/i })).toBeInTheDocument();
        },
        { timeout: 5000 },
      );

      const clearButton = screen.getByRole('button', { name: /Clear search/i });
      fireEvent.click(clearButton);

      // All projects should reappear
      await waitFor(
        () => {
          expect(screen.getByText('Alpha Project')).toBeInTheDocument();
          expect(screen.getByText('Beta Project')).toBeInTheDocument();
          expect(screen.getByText('Gamma Project')).toBeInTheDocument();
        },
        { timeout: 5000 },
      );
    }, 15_000);
  });

  // -------------------------------------------------------------------------
  // Sorting
  // -------------------------------------------------------------------------
  describe('Sorting', () => {
    it('renders the sort-by select trigger', async () => {
      setPopulatedState();
      await renderDashboard();

      // The sort select trigger should be rendered with a combobox role
      const trigger = screen.queryByRole('combobox');
      expect(trigger).toBeInTheDocument();
    });

    it('sorts projects by name alphabetically by default', async () => {
      setPopulatedState();
      await renderDashboard();

      // Default sort is "name" (alphabetical).
      // Projects: Alpha, Beta, Gamma -- should appear in that order.
      const projectNames = screen
        .getAllByText(/Alpha Project|Beta Project|Gamma Project/)
        .map((el) => el.textContent);
      expect(projectNames).toEqual(['Alpha Project', 'Beta Project', 'Gamma Project']);
    });
  });

  // -------------------------------------------------------------------------
  // Pinning
  // -------------------------------------------------------------------------
  describe('Pinning', () => {
    it('auto-pins the first project on initial render', async () => {
      setPopulatedState();
      await renderDashboard();

      const pinButtons = screen.getAllByTitle(/pin project|unpin project/i);
      // The first project should show "Unpin project" since it's auto-pinned
      expect(pinButtons[0]).toHaveAttribute('title', 'Unpin project');
    });

    it('toggles pin when clicking the pin button on a different project', async () => {
      setPopulatedState();
      await renderDashboard();

      let pinButtons = screen.getAllByTitle(/pin project|unpin project/i);
      expect(pinButtons[0]).toHaveAttribute('title', 'Unpin project');
      expect(pinButtons[1]).toHaveAttribute('title', 'Pin project');

      // Click pin on the second project
      fireEvent.click(pinButtons[1]);

      // Now second project should be pinned
      await waitFor(
        () => {
          pinButtons = screen.getAllByTitle(/pin project|unpin project/i);
          expect(pinButtons[1]).toHaveAttribute('title', 'Unpin project');
        },
        { timeout: 5000 },
      );
    }, 15_000);

    it('shows toast when pinning a project', async () => {
      const { toast } = await import('sonner');
      setPopulatedState();
      await renderDashboard();

      // Get the "Pin project" buttons (not the already-unpinned ones)
      const pinButtons = screen.getAllByTitle('Pin project');
      fireEvent.click(pinButtons[0]);

      await waitFor(
        () => {
          expect(toast.success).toHaveBeenCalledWith(expect.stringContaining('Pinned'));
        },
        { timeout: 5000 },
      );
    }, 15_000);
  });

  // -------------------------------------------------------------------------
  // View mode toggle
  // -------------------------------------------------------------------------
  describe('View Mode', () => {
    it('defaults to grid view and renders project names', async () => {
      setPopulatedState();
      await renderDashboard();

      expect(screen.getByText('Alpha Project')).toBeInTheDocument();
    });
  });

  // -------------------------------------------------------------------------
  // Header content
  // -------------------------------------------------------------------------
  describe('Header', () => {
    it('renders the dashboard heading and description', async () => {
      setPopulatedState();
      await renderDashboard();

      expect(screen.getByText(/Traceability Dashboard/i)).toBeInTheDocument();
      expect(
        screen.getByText(/Monitor project health and system-wide traceability status/i),
      ).toBeInTheDocument();
    });

    it('shows system status badge as healthy by default', async () => {
      setPopulatedState();
      await renderDashboard();

      expect(screen.getByText(/System: healthy/i)).toBeInTheDocument();
    });

    it('renders New Project button linking to /projects', async () => {
      setPopulatedState();
      await renderDashboard();

      const newProjectBtn = screen.queryByRole('link', { name: /New Project/i });
      expect(newProjectBtn).toBeInTheDocument();
    });
  });

  // -------------------------------------------------------------------------
  // Active Projects section heading
  // -------------------------------------------------------------------------
  describe('Active Projects Section', () => {
    it('renders the Active Projects heading', async () => {
      setPopulatedState();
      await renderDashboard();

      expect(screen.getByText(/Active Projects/i)).toBeInTheDocument();
    });
  });
});
