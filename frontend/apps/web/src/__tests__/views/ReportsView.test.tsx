import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { api } from '../../api/endpoints';
import { ReportsView } from '../../views/ReportsView';

// Mock the API
vi.mock('../../api/endpoints', () => ({
  api: {
    exportImport: {
      export: vi.fn(),
    },
    projects: {
      list: vi.fn(),
    },
  },
}));

describe(ReportsView, () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        mutations: { retry: false },
        queries: { retry: false },
      },
    });
    vi.clearAllMocks();
    vi.mocked(api.projects.list).mockResolvedValue([]);
  });

  it('renders reports interface', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ReportsView />
      </QueryClientProvider>,
    );

    expect(screen.getByRole('heading', { name: 'Intelligence Hub' })).toBeInTheDocument();
    expect(screen.getByText('Traceability Matrix')).toBeInTheDocument();
    expect(screen.getByText('Executive Summary')).toBeInTheDocument();
    expect(screen.getByText('Entity Registry')).toBeInTheDocument();
    expect(screen.getByText('Compliance Audit')).toBeInTheDocument();
  });

  it('displays report templates', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ReportsView />
      </QueryClientProvider>,
    );

    expect(screen.getByText('End-to-end mapping from reqs to implementation.')).toBeInTheDocument();
    expect(screen.getByText('High-level project health and risk assessment.')).toBeInTheDocument();
  });

  it('displays format badges for each template', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ReportsView />
      </QueryClientProvider>,
    );

    expect(screen.getAllByRole('button', { name: /Select PDF for/i })).toHaveLength(3);
    expect(screen.getAllByRole('button', { name: /Select XLSX for/i })).toHaveLength(3);
    expect(screen.getAllByRole('button', { name: /Select CSV for/i })).toHaveLength(2);
  });

  it('handles format selection', async () => {
    const user = userEvent.setup();
    render(
      <QueryClientProvider client={queryClient}>
        <ReportsView />
      </QueryClientProvider>,
    );

    const csvButton = screen.getByRole('button', {
      name: 'Select CSV for Traceability Matrix',
    });
    await user.click(csvButton);
    expect(csvButton).toHaveAttribute('aria-pressed', 'true');
  });

  it('displays project selector', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ReportsView />
      </QueryClientProvider>,
    );

    expect(screen.getByRole('combobox', { name: 'Project context' })).toHaveTextContent(
      'System-Wide Registry',
    );
  });

  it('generates report when button is clicked', async () => {
    const user = userEvent.setup();
    const { api } = await import('../../api/endpoints');
    const mockBlob = new Blob(['test'], { type: 'application/json' });
    (api.exportImport.export as any).mockResolvedValue(mockBlob);
    (api.projects.list as any).mockResolvedValue([{ id: 'proj-1', name: 'Test Project' }]);

    render(
      <QueryClientProvider client={queryClient}>
        <ReportsView />
      </QueryClientProvider>,
    );

    await user.click(screen.getByRole('combobox', { name: 'Project context' }));
    await user.click(await screen.findByRole('option', { name: 'Test Project' }));
    await user.click(
      screen.getByRole('button', { name: 'Select CSV for Traceability Matrix' }),
    );
    await user.click(screen.getByRole('button', { name: 'Compile Traceability Matrix' }));

    await waitFor(() => {
      expect(api.exportImport.export).toHaveBeenCalledWith('proj-1', 'csv');
    });
  });

  it('displays recent reports section', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ReportsView />
      </QueryClientProvider>,
    );

    expect(screen.getByText('Archive History')).toBeInTheDocument();
    expect(screen.getByText('Full Integrity Matrix')).toBeInTheDocument();
    expect(screen.getByText(/2h ago/)).toBeInTheDocument();
  });

  it('shows loading state during report generation', async () => {
    const user = userEvent.setup();
    const { api } = await import('../../api/endpoints');
    (api.exportImport.export as any).mockImplementation(
      async () =>
        new Promise((resolve) =>
          setTimeout(() => {
            resolve(new Blob());
          }, 500),
        ),
    );
    (api.projects.list as any).mockResolvedValue([{ id: 'proj-1', name: 'Test Project' }]);

    render(
      <QueryClientProvider client={queryClient}>
        <ReportsView />
      </QueryClientProvider>,
    );

    await user.click(screen.getByRole('combobox', { name: 'Project context' }));
    await user.click(await screen.findByRole('option', { name: 'Test Project' }));
    await user.click(
      screen.getByRole('button', { name: 'Select CSV for Traceability Matrix' }),
    );
    await user.click(screen.getByRole('button', { name: 'Compile Traceability Matrix' }));

    expect(
      screen.getByRole('button', { name: 'Compile Traceability Matrix (in progress)' }),
    ).toBeDisabled();
  });
});
