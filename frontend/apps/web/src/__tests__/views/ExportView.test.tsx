import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ExportView } from '../../views/ExportView';

// Mock the API
vi.mock('../../api/endpoints', () => ({
  api: {
    exportImport: {
      export: vi.fn(),
    },
    projects: {
      list: vi.fn().mockResolvedValue([]),
    },
  },
}));

const user = userEvent.setup();

describe(ExportView, () => {
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

  it('renders export interface', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ExportView />
      </QueryClientProvider>,
    );

    // Check heading exists
    expect(screen.getByRole('heading', { name: /Export Project/i })).toBeInTheDocument();
    // Check format label exists
    expect(screen.getByText('Export Format')).toBeInTheDocument();
    // Check button exists
    expect(screen.getByRole('button', { name: /Export Project/i })).toBeInTheDocument();
  });

  it('displays format options', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ExportView />
      </QueryClientProvider>,
    );

    // Format options are in Select component - they show in the description list
    expect(screen.getByText(/JSON:/)).toBeInTheDocument();
    expect(screen.getByText(/CSV:/)).toBeInTheDocument();
    expect(screen.getByText(/Markdown:/)).toBeInTheDocument();
  });

  it('shows format details', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ExportView />
      </QueryClientProvider>,
    );

    expect(screen.getByText(/JSON:/)).toBeInTheDocument();
    expect(screen.getByText(/CSV:/)).toBeInTheDocument();
    expect(screen.getByText(/Markdown:/)).toBeInTheDocument();
  });

  it('disables export button when no project selected', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ExportView />
      </QueryClientProvider>,
    );

    const exportButton = screen.getByRole('button', {
      name: /Export Project/i,
    });
    expect(exportButton).toBeDisabled();
  });

  it('enables export button when project is selected', async () => {
    const { api } = await import('../../api/endpoints');
    (api.projects.list as any).mockResolvedValue([{ id: 'proj-1', name: 'Test Project' }]);

    render(
      <QueryClientProvider client={queryClient}>
        <ExportView />
      </QueryClientProvider>,
    );

    // Wait for projects to load
    await waitFor(() => {
      expect(api.projects.list).toHaveBeenCalled();
    });

    // Open the project select and choose a project
    const projectSelect = screen.getByRole('combobox', { name: /Project/i });
    await user.click(projectSelect);

    // Select "Test Project"
    const option = await screen.findByRole('option', { name: 'Test Project' });
    await user.click(option);

    // Check button is now enabled
    await waitFor(() => {
      const exportButton = screen.getByRole('button', {
        name: /Export Project/i,
      });
      expect(exportButton).not.toBeDisabled();
    });
  });

  it('triggers download on export', async () => {
    const { api } = await import('../../api/endpoints');
    const mockBlob = new Blob(['test data'], { type: 'application/json' });
    (api.exportImport.export as any).mockResolvedValue(mockBlob);
    (api.projects.list as any).mockResolvedValue([{ id: 'proj-1', name: 'Test Project' }]);

    // Render first, then set up spies
    render(
      <QueryClientProvider client={queryClient}>
        <ExportView />
      </QueryClientProvider>,
    );

    // Wait for projects to load
    await waitFor(() => {
      expect(api.projects.list).toHaveBeenCalled();
    });

    // Now set up URL and document spies (after render)
    const mockUrl = 'blob:test-url';
    vi.spyOn(globalThis.URL, 'createObjectURL').mockReturnValue(mockUrl);
    vi.spyOn(globalThis.URL, 'revokeObjectURL').mockImplementation(() => {});

    // Select a project
    const projectSelect = screen.getByRole('combobox', { name: /Project/i });
    await user.click(projectSelect);
    const option = await screen.findByRole('option', { name: 'Test Project' });
    await user.click(option);

    // Wait for button to be enabled
    await waitFor(() => {
      const exportButton = screen.getByRole('button', {
        name: /Export Project/i,
      });
      expect(exportButton).not.toBeDisabled();
    });

    // Click export
    const exportButton = screen.getByRole('button', {
      name: /Export Project/i,
    });
    await user.click(exportButton);

    // Verify export was called
    await waitFor(() => {
      expect(api.exportImport.export).toHaveBeenCalledWith('proj-1', 'json');
    });
  });
});
