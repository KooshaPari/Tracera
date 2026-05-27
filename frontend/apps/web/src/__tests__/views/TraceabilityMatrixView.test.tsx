/**
 * Comprehensive Tests for TraceabilityMatrixView
 * @vitest-environment jsdom
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi, type Mock } from 'vitest';
import { toast } from 'sonner';

vi.mock('sonner', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

vi.mock('@/api/traceMatrixExport', () => ({
  downloadTraceMatrixFromApi: vi.fn(),
}));

import { downloadTraceMatrixFromApi } from '@/api/traceMatrixExport';

import { useItems } from '../../hooks/useItems';
import { useLinks } from '../../hooks/useLinks';
import { TraceabilityMatrixView } from '../../views/TraceabilityMatrixView';

vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual('@tanstack/react-router');
  return {
    ...actual,
    Link: ({ children, to }: { children: React.ReactNode; to: string }) => (
      <a href={typeof to === 'string' ? to : String(to)}>{children}</a>
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

function mockItems(overrides: Partial<ReturnType<typeof useItems>> = {}) {
  (useItems as Mock).mockReturnValue({
    data: { items: [], total: 0 },
    error: null,
    isError: false,
    isLoading: false,
    ...overrides,
  } as ReturnType<typeof useItems>);
}

function mockLinks(overrides: Partial<ReturnType<typeof useLinks>> = {}) {
  (useLinks as Mock).mockReturnValue({
    data: { links: [] },
    error: null,
    isError: false,
    isLoading: false,
    ...overrides,
  } as ReturnType<typeof useLinks>);
}

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
    mockItems();
    mockLinks();

    render(
      <QueryClientProvider client={queryClient}>
        <TraceabilityMatrixView projectId='proj-test' />
      </QueryClientProvider>,
    );

    expect(screen.getByText('Traceability Matrix')).toBeInTheDocument();
    expect(
      screen.getByText(/Requirements coverage mapped to functional features/i),
    ).toBeInTheDocument();
  });

  it('displays loading state', () => {
    mockItems({ data: undefined, isLoading: true });
    mockLinks({ data: undefined, isLoading: false });

    render(
      <QueryClientProvider client={queryClient}>
        <TraceabilityMatrixView projectId='proj-test' />
      </QueryClientProvider>,
    );

    expect(screen.getByTestId('matrix-loading')).toBeInTheDocument();
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

    mockItems({
      data: { items: [...requirements, ...features], total: 4 },
    });
    mockLinks({
      data: {
        links: [
          { sourceId: 'req-1', targetId: 'feat-1' },
          { sourceId: 'req-2', targetId: 'feat-2' },
        ],
      },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <TraceabilityMatrixView projectId='proj-test' />
      </QueryClientProvider>,
    );

    expect(screen.getByText('Requirement 1')).toBeInTheDocument();
    expect(screen.getByText('Feature 1')).toBeInTheDocument();
  });

  it('shows export button', () => {
    mockItems();
    mockLinks();

    render(
      <QueryClientProvider client={queryClient}>
        <TraceabilityMatrixView projectId='proj-test' />
      </QueryClientProvider>,
    );

    expect(screen.getByRole('button', { name: /export csv/i })).toBeInTheDocument();
  });

  it('blocks export when matrix has no rows or columns', async () => {
    const user = userEvent.setup();
    mockItems();
    mockLinks();

    render(
      <QueryClientProvider client={queryClient}>
        <TraceabilityMatrixView projectId='proj-test' />
      </QueryClientProvider>,
    );

    await user.click(screen.getByRole('button', { name: /export csv/i }));
    expect(toast.error).toHaveBeenCalledWith(
      'Nothing to export — add requirements and features first',
    );
  });

  it('handles empty state', () => {
    mockItems();
    mockLinks();

    render(
      <QueryClientProvider client={queryClient}>
        <TraceabilityMatrixView projectId='proj-test' />
      </QueryClientProvider>,
    );

    expect(screen.getByText('Traceability Matrix')).toBeInTheDocument();
    expect(screen.getByTestId('matrix-empty-requirements')).toBeInTheDocument();
  });

  it('shows error state when items fail to load', () => {
    mockItems({
      data: undefined,
      isError: true,
      error: new Error('API unavailable'),
    });
    mockLinks();

    render(
      <QueryClientProvider client={queryClient}>
        <TraceabilityMatrixView projectId='proj-test' />
      </QueryClientProvider>,
    );

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText('API unavailable')).toBeInTheDocument();
  });
});
