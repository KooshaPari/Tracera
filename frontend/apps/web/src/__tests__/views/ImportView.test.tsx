import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ImportView } from '../../views/ImportView';

// Mock the API
vi.mock('../../api/endpoints', () => ({
  api: {
    exportImport: {
      import: vi.fn(),
    },
    projects: {
      list: vi.fn(),
    },
  },
}));

describe(ImportView, () => {
  let queryClient: QueryClient;
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        mutations: { retry: false },
        queries: { retry: false },
      },
    });
    user = userEvent.setup();
    vi.clearAllMocks();
  });

  it('renders import interface', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ImportView />
      </QueryClientProvider>,
    );

    expect(screen.getByText('Import Project Data')).toBeInTheDocument();
    expect(screen.getByText('Import Format')).toBeInTheDocument();
    expect(screen.getByText('Import Data')).toBeInTheDocument();
  });

  it('displays format options', async () => {
    const { api } = await import('../../api/endpoints');
    (api.projects.list as any).mockResolvedValue([]);

    render(
      <QueryClientProvider client={queryClient}>
        <ImportView />
      </QueryClientProvider>,
    );

    // Click format select to open dropdown
    const formatSelect = document.querySelector('#format-select');
    await user.click(formatSelect!);

    // Wait for options to appear
    await waitFor(() => {
      expect(screen.getByRole('option', { name: 'JSON' })).toBeInTheDocument();
      expect(screen.getByRole('option', { name: 'CSV' })).toBeInTheDocument();
    });
  });

  it('shows format requirements', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ImportView />
      </QueryClientProvider>,
    );

    expect(screen.getByText(/Format Requirements:/)).toBeInTheDocument();
  });

  it('handles format selection', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ImportView />
      </QueryClientProvider>,
    );

    const formatSelect = document.querySelector('#format-select');
    expect(formatSelect).toBeInTheDocument();

    // Click to open dropdown
    await user.click(formatSelect!);

    // Wait for dropdown and click CSV option
    await waitFor(
      () => {
        const csvOption = screen.queryByRole('option', { name: 'CSV' });
        if (csvOption) {
          return true;
        }
        throw new Error('CSV option not found');
      },
      { timeout: 2000 },
    );

    await user.click(screen.getByRole('option', { name: 'CSV' }));

    // Verify the trigger shows selected value
    await waitFor(() => {
      expect(formatSelect).toHaveTextContent('CSV');
    });
  });

  it('handles file upload', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ImportView />
      </QueryClientProvider>,
    );

    const file = new File(['test data'], 'test.json', {
      type: 'application/json',
    });
    const fileInput = screen.getByLabelText('Upload File (Optional)');

    await user.upload(fileInput, file);

    await waitFor(() => {
      const textarea = screen.getByPlaceholderText(/Paste JSON data here/);
      expect(textarea).toHaveValue('test data');
    });
  });

  it('handles text input', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ImportView />
      </QueryClientProvider>,
    );

    const textarea = screen.getByPlaceholderText(/Paste JSON data here/);
    fireEvent.change(textarea, { target: { value: '{"items": []}' } });

    expect(textarea).toHaveValue('{"items": []}');
  });

  it('disables import button when no data', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ImportView />
      </QueryClientProvider>,
    );

    const importButton = screen.getByText('Import Data');
    expect(importButton).toBeDisabled();
  });

  it('enables import button when data is provided', async () => {
    const { api } = await import('../../api/endpoints');
    (api.projects.list as any).mockResolvedValue([{ id: 'proj-1', name: 'Test Project' }]);

    render(
      <QueryClientProvider client={queryClient}>
        <ImportView />
      </QueryClientProvider>,
    );

    // Wait for projects to load
    await waitFor(() => {
      expect(screen.getByText('Project')).toBeInTheDocument();
    });

    // Select a project
    const projectSelect = document.querySelector('#project-select');
    await user.click(projectSelect!);
    await waitFor(() => {
      expect(screen.getByRole('option', { name: 'Test Project' })).toBeInTheDocument();
    });
    await user.click(screen.getByRole('option', { name: 'Test Project' }));

    // Add data
    const textarea = screen.getByPlaceholderText(/Paste JSON data here/);
    fireEvent.change(textarea, { target: { value: '{"items": []}' } });

    // Button should be enabled
    await waitFor(() => {
      const importButton = screen.getByText('Import Data');
      expect(importButton).not.toBeDisabled();
    });
  });

  it('shows success message after successful import', async () => {
    const { api } = await import('../../api/endpoints');
    (api.exportImport.import as any).mockResolvedValue({
      error_count: 0,
      errors: [],
      imported_count: 5,
      success: true,
    });
    (api.projects.list as any).mockResolvedValue([{ id: 'proj-1', name: 'Test Project' }]);

    render(
      <QueryClientProvider client={queryClient}>
        <ImportView />
      </QueryClientProvider>,
    );

    // Wait for projects to load and select one
    await waitFor(() => {
      expect(screen.getByText('Project')).toBeInTheDocument();
    });

    const projectSelect = document.querySelector('#project-select');
    await user.click(projectSelect!);
    await waitFor(() => {
      expect(screen.getByRole('option', { name: 'Test Project' })).toBeInTheDocument();
    });
    await user.click(screen.getByRole('option', { name: 'Test Project' }));

    // Add data
    const textarea = screen.getByPlaceholderText(/Paste JSON data here/);
    fireEvent.change(textarea, { target: { value: '{"items": []}' } });

    // Click import button
    const importButton = screen.getByText('Import Data');
    await user.click(importButton);

    // Check for rendered success message (not alert)
    await waitFor(() => {
      expect(screen.getByText('Import Results')).toBeInTheDocument();
      expect(screen.getByText(/Imported:/)).toBeInTheDocument();
      expect(screen.getByText('5 items')).toBeInTheDocument();
    });
  });

  it('shows error message on import failure', async () => {
    const { api } = await import('../../api/endpoints');
    const alertMock = vi.spyOn(globalThis, 'alert').mockImplementation(() => {});

    (api.exportImport.import as any).mockRejectedValue(new Error('Import failed'));
    (api.projects.list as any).mockResolvedValue([{ id: 'proj-1', name: 'Test Project' }]);

    render(
      <QueryClientProvider client={queryClient}>
        <ImportView />
      </QueryClientProvider>,
    );

    // Wait for projects to load and select one
    await waitFor(() => {
      expect(screen.getByText('Project')).toBeInTheDocument();
    });

    const projectSelect = document.querySelector('#project-select');
    await user.click(projectSelect!);
    await waitFor(() => {
      expect(screen.getByRole('option', { name: 'Test Project' })).toBeInTheDocument();
    });
    await user.click(screen.getByRole('option', { name: 'Test Project' }));

    // Add data
    const textarea = screen.getByPlaceholderText(/Paste JSON data here/);
    fireEvent.change(textarea, { target: { value: '{"items": []}' } });

    // Click import button
    const importButton = screen.getByText('Import Data');
    await user.click(importButton);

    // Check that alert was called with error message
    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith(expect.stringContaining('Import failed'));
    });

    alertMock.mockRestore();
  });

  it('displays import errors when present', async () => {
    const { api } = await import('../../api/endpoints');
    (api.exportImport.import as any).mockResolvedValue({
      error_count: 2,
      errors: ['Error 1', 'Error 2'],
      imported_count: 3,
      success: true,
    });
    (api.projects.list as any).mockResolvedValue([{ id: 'proj-1', name: 'Test Project' }]);

    render(
      <QueryClientProvider client={queryClient}>
        <ImportView />
      </QueryClientProvider>,
    );

    // Wait for projects to load and select one
    await waitFor(() => {
      expect(screen.getByText('Project')).toBeInTheDocument();
    });

    const projectSelect = document.querySelector('#project-select');
    await user.click(projectSelect!);
    await waitFor(() => {
      expect(screen.getByRole('option', { name: 'Test Project' })).toBeInTheDocument();
    });
    await user.click(screen.getByRole('option', { name: 'Test Project' }));

    // Add data
    const textarea = screen.getByPlaceholderText(/Paste JSON data here/);
    fireEvent.change(textarea, { target: { value: '{"items": []}' } });

    // Click import button
    const importButton = screen.getByText('Import Data');
    await user.click(importButton);

    // Check for rendered error details in results card
    await waitFor(() => {
      expect(screen.getByText('Import Results')).toBeInTheDocument();
      expect(screen.getByText(/Errors:/)).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
      expect(screen.getByText('Error 1')).toBeInTheDocument();
      expect(screen.getByText('Error 2')).toBeInTheDocument();
    });
  });
});
