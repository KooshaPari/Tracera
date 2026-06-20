/**
 * Comprehensive Tests for TraceabilityMatrixView
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useItems } from '../../hooks/useItems';
import { useLinks } from '../../hooks/useLinks';
import { TraceabilityMatrixView } from '../../views/TraceabilityMatrixView';

// Mock TanStack Router
vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual('@tanstack/react-router');
  return {
    ...actual,
    Link: ({ children, to }: any) => (
      <a href={typeof to === 'string' ? to : to.toString()}>{children}</a>
    ),
    useNavigate: () => vi.fn(),
    useSearch: () => ({}),
  };
});

vi.mock('../../hooks/useItems', () => ({
  useItems: vi.fn(),
}));

vi.mock('../../hooks/useLinks', () => ({
  useLinks: vi.fn(),
}));

describe(TraceabilityMatrixView, () => {
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

  it('renders traceability matrix interface', () => {
    vi.mocked(useItems).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useLinks).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <TraceabilityMatrixView projectId='proj-test' />
      </QueryClientProvider>,
    );

    expect(screen.getByText('Traceability Matrix')).toBeInTheDocument();
    expect(screen.getByText(/Requirements coverage overview/i)).toBeInTheDocument();
  });

  it('displays loading state', () => {
    vi.mocked(useItems).mockReturnValue({
      data: undefined,
      error: null,
      isError: false,
      isLoading: true,
    } as any);

    vi.mocked(useLinks).mockReturnValue({
      data: undefined,
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <TraceabilityMatrixView projectId='proj-test' />
      </QueryClientProvider>,
    );

    // Should show skeleton/loading state
  });

  it('displays matrix with requirements and features', () => {
    const requirements = [
      { id: 'req-1', title: 'Requirement 1', type: 'requirement' },
      { id: 'req-2', title: 'Requirement 2', type: 'requirement' },
    ];

    const features = [
      { id: 'feat-1', title: 'Feature 1', type: 'feature' },
      { id: 'feat-2', title: 'Feature 2', type: 'feature' },
    ];

    const links = [
      { sourceId: 'req-1', targetId: 'feat-1' },
      { sourceId: 'req-2', targetId: 'feat-2' },
    ];

    vi.mocked(useItems).mockReturnValue({
      data: [...requirements, ...features],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useLinks).mockReturnValue({
      data: links,
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <TraceabilityMatrixView projectId='proj-test' />
      </QueryClientProvider>,
    );

    expect(screen.getByText('Requirement 1')).toBeInTheDocument();
    expect(screen.getByText('Feature 1')).toBeInTheDocument();
  });

  it('shows export button', () => {
    vi.mocked(useItems).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useLinks).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <TraceabilityMatrixView projectId='proj-test' />
      </QueryClientProvider>,
    );

    expect(screen.getByText('Export')).toBeInTheDocument();
  });

  it('handles empty state', () => {
    vi.mocked(useItems).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    vi.mocked(useLinks).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <TraceabilityMatrixView projectId='proj-test' />
      </QueryClientProvider>,
    );

    // Should render empty matrix
    expect(screen.getByText('Traceability Matrix')).toBeInTheDocument();
  });
});
