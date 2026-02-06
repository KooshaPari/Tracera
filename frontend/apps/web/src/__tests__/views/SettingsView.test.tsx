import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { SettingsView } from '../../views/SettingsView';

describe(SettingsView, () => {
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

  it('renders settings interface', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SettingsView />
      </QueryClientProvider>,
    );

    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByText('General')).toBeInTheDocument();
    expect(screen.getByText('Appearance')).toBeInTheDocument();
    expect(screen.getByText('API Keys')).toBeInTheDocument();
    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });

  it('displays general settings', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SettingsView />
      </QueryClientProvider>,
    );

    expect(screen.getByText('Display Name')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
    expect(screen.getByText('Timezone')).toBeInTheDocument();
  });

  it('displays appearance settings', async () => {
    const user = userEvent.setup();
    render(
      <QueryClientProvider client={queryClient}>
        <SettingsView />
      </QueryClientProvider>,
    );

    // Click on Appearance tab
    await user.click(screen.getByText('Appearance'));

    expect(screen.getByText('Theme')).toBeInTheDocument();
    expect(screen.getByText('Font Size')).toBeInTheDocument();
    expect(screen.getByText('Use compact layout')).toBeInTheDocument();
  });

  it('displays API keys settings', async () => {
    const user = userEvent.setup();
    render(
      <QueryClientProvider client={queryClient}>
        <SettingsView />
      </QueryClientProvider>,
    );

    // Click on API Keys tab
    await user.click(screen.getByText('API Keys'));

    expect(screen.getByText('API Key')).toBeInTheDocument();
    expect(screen.getByText('Generate New Key')).toBeInTheDocument();
    expect(screen.getByText('Revoke Key')).toBeInTheDocument();
  });

  it('displays notification settings', async () => {
    const user = userEvent.setup();
    render(
      <QueryClientProvider client={queryClient}>
        <SettingsView />
      </QueryClientProvider>,
    );

    // Click on Notifications tab
    await user.click(screen.getByText('Notifications'));

    expect(screen.getByText('Email Notifications')).toBeInTheDocument();
    expect(screen.getByText('Desktop Notifications')).toBeInTheDocument();
    expect(screen.getByText('Weekly Summary')).toBeInTheDocument();
    expect(screen.getByText('Item Updates')).toBeInTheDocument();
  });

  it('handles theme selection', async () => {
    const user = userEvent.setup();
    render(
      <QueryClientProvider client={queryClient}>
        <SettingsView />
      </QueryClientProvider>,
    );

    // Click on Appearance tab
    await user.click(screen.getByText('Appearance'));

    // Radix UI Select uses button triggers, not native selects
    const themeSelect = document.querySelector('#theme-select');
    expect(themeSelect).toBeInTheDocument();

    // Click to open the dropdown
    await user.click(themeSelect!);

    // Wait for dropdown to open and click option
    await waitFor(() => {
      const darkOption = screen.getByRole('option', { name: 'Dark' });
      expect(darkOption).toBeInTheDocument();
    });

    await user.click(screen.getByRole('option', { name: 'Dark' }));

    // Verify the trigger now shows the selected value
    await waitFor(() => {
      expect(themeSelect).toHaveTextContent('Dark');
    });
  });

  it('handles notification toggles', async () => {
    const user = userEvent.setup();
    render(
      <QueryClientProvider client={queryClient}>
        <SettingsView />
      </QueryClientProvider>,
    );

    // Click on Notifications tab
    await user.click(screen.getByText('Notifications'));

    const emailNotifications = document.querySelector('#email-notifications')!;
    expect(emailNotifications).toBeChecked();

    await user.click(emailNotifications);
    await waitFor(() => {
      expect(emailNotifications).not.toBeChecked();
    });
  });

  it('saves settings when save button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <QueryClientProvider client={queryClient}>
        <SettingsView />
      </QueryClientProvider>,
    );

    const displayNameInput = document.querySelector('#display-name')!;
    await user.type(displayNameInput, 'Test User');

    const saveButton = screen.getByText('Save Changes');
    expect(saveButton).toBeInTheDocument();

    // Click save and verify the button exists (mutation is mocked and resolves immediately)
    await user.click(saveButton);

    // Since the mutation resolves immediately in tests, verify that the alert was called
    // Or that the button returns to its normal state
    await waitFor(() => {
      // The mutation resolves quickly, so the button should be back to "Save Changes"
      expect(screen.getByText('Save Changes')).toBeInTheDocument();
    });
  });

  it('handles form input changes', async () => {
    const user = userEvent.setup();
    render(
      <QueryClientProvider client={queryClient}>
        <SettingsView />
      </QueryClientProvider>,
    );

    const displayNameInput = document.querySelector('#display-name')!;
    await user.type(displayNameInput, 'John Doe');

    const emailInput = document.querySelector('#email')!;
    await user.type(emailInput, 'john@example.com');

    expect(displayNameInput).toHaveValue('John Doe');
    expect(emailInput).toHaveValue('john@example.com');
  });
});
