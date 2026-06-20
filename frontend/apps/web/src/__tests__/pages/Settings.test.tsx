/**
 * Comprehensive Settings Page Tests
 * Tests: Settings sections, form submissions, preferences, integrations
 */

import { QueryClient } from '@tanstack/react-query';
import { RouterProvider, createMemoryHistory, createRouter } from '@tanstack/react-router';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { routeTree } from '@/routeTree.gen';

vi.mock('@/api/settings', () => ({
  fetchSettings: vi.fn(),
  resetSettings: vi.fn(),
  updateSettings: vi.fn(),
}));

describe('Settings Page', () => {
  let queryClient: QueryClient;
  let router: any;
  let history: any;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        mutations: { retry: false },
        queries: { gcTime: 0, retry: false },
      },
    });

    history = createMemoryHistory({
      initialEntries: ['/settings'],
    });

    router = createRouter({
      context: { queryClient },
      history,
      routeTree,
    });

    vi.clearAllMocks();
  });

  afterEach(() => {
    queryClient.clear();
  });

  describe('Page Rendering', () => {
    it('renders settings page with navigation', async () => {
      const { fetchSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        appearance: {},
        general: {},
        integrations: {},
        notifications: {},
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /settings/i })).toBeInTheDocument();
      });

      expect(screen.getByRole('link', { name: /general/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /notifications/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /appearance/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /integrations/i })).toBeInTheDocument();
    });

    it('highlights active settings section', async () => {
      const { fetchSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        general: {},
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        const generalLink = screen.getByRole('link', { name: /general/i });
        expect(generalLink).toHaveClass('active');
      });
    });
  });

  describe('General Settings', () => {
    it('displays general settings fields', async () => {
      const { fetchSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        general: {
          dateFormat: 'YYYY-MM-DD',
          language: 'en',
          siteName: 'TraceRTM',
          timezone: 'UTC',
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByLabelText(/site name/i)).toHaveValue('TraceRTM');
      });

      expect(screen.getByLabelText(/language/i)).toHaveValue('en');
      expect(screen.getByLabelText(/timezone/i)).toHaveValue('UTC');
      expect(screen.getByLabelText(/date format/i)).toHaveValue('YYYY-MM-DD');
    });

    it('updates general settings', async () => {
      const { fetchSettings, updateSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        general: {
          siteName: 'Old Name',
        },
      });
      vi.mocked(updateSettings).mockResolvedValue({
        general: {
          siteName: 'New Name',
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByLabelText(/site name/i)).toBeInTheDocument();
      });

      const input = screen.getByLabelText(/site name/i);
      await userEvent.clear(input);
      await userEvent.type(input, 'New Name');

      const saveButton = screen.getByRole('button', { name: /save changes/i });
      await userEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/settings saved/i)).toBeInTheDocument();
      });
    });

    it('validates required fields', async () => {
      const { fetchSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        general: {
          siteName: 'TraceRTM',
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByLabelText(/site name/i)).toBeInTheDocument();
      });

      const input = screen.getByLabelText(/site name/i);
      await userEvent.clear(input);

      const saveButton = screen.getByRole('button', { name: /save changes/i });
      await userEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/site name is required/i)).toBeInTheDocument();
      });
    });

    it('resets to defaults', async () => {
      const { fetchSettings, resetSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        general: {
          language: 'es',
          siteName: 'Custom Name',
        },
      });
      vi.mocked(resetSettings).mockResolvedValue({
        general: {
          language: 'en',
          siteName: 'TraceRTM',
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByLabelText(/site name/i)).toHaveValue('Custom Name');
      });

      const resetButton = screen.getByRole('button', {
        name: /reset to defaults/i,
      });
      await userEvent.click(resetButton);

      await waitFor(() => {
        expect(screen.getByText(/confirm reset/i)).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('button', { name: /confirm/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/site name/i)).toHaveValue('TraceRTM');
      });
    });
  });

  describe('Notification Settings', () => {
    it('displays notification preferences', async () => {
      const { fetchSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        notifications: {
          email: true,
          frequency: 'immediate',
          push: false,
          slack: true,
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /notifications/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /notifications/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/email notifications/i)).toBeChecked();
      });

      expect(screen.getByLabelText(/push notifications/i)).not.toBeChecked();
      expect(screen.getByLabelText(/slack notifications/i)).toBeChecked();
    });

    it('toggles notification channels', async () => {
      const { fetchSettings, updateSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        notifications: {
          email: false,
        },
      });
      vi.mocked(updateSettings).mockResolvedValue({
        notifications: {
          email: true,
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /notifications/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /notifications/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/email notifications/i)).not.toBeChecked();
      });

      const checkbox = screen.getByLabelText(/email notifications/i);
      await userEvent.click(checkbox);

      await waitFor(() => {
        expect(screen.getByLabelText(/email notifications/i)).toBeChecked();
      });
    });

    it('configures notification frequency', async () => {
      const { fetchSettings, updateSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        notifications: {
          frequency: 'immediate',
        },
      });
      vi.mocked(updateSettings).mockResolvedValue({
        notifications: {
          frequency: 'daily',
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /notifications/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /notifications/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/frequency/i)).toBeInTheDocument();
      });

      const select = screen.getByLabelText(/frequency/i);
      await userEvent.click(select);
      await userEvent.click(screen.getByRole('option', { name: /daily/i }));

      const saveButton = screen.getByRole('button', { name: /save/i });
      await userEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/settings saved/i)).toBeInTheDocument();
      });
    });

    it('manages notification filters', async () => {
      const { fetchSettings, updateSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        notifications: {
          filters: {
            itemTypes: ['feature', 'bug'],
            priorities: ['high', 'critical'],
          },
        },
      });
      vi.mocked(updateSettings).mockResolvedValue({
        notifications: {
          filters: {
            itemTypes: ['feature', 'bug', 'doc'],
            priorities: ['high', 'critical'],
          },
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /notifications/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /notifications/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/item types/i)).toBeInTheDocument();
      });

      const itemTypes = screen.getByLabelText(/item types/i);
      await userEvent.click(itemTypes);
      await userEvent.click(screen.getByRole('option', { name: /documentation/i }));

      const saveButton = screen.getByRole('button', { name: /save/i });
      await userEvent.click(saveButton);

      await waitFor(() => {
        expect(updateSettings).toHaveBeenCalled();
      });
    });
  });

  describe('Appearance Settings', () => {
    it('displays theme options', async () => {
      const { fetchSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        appearance: {
          accentColor: '#3b82f6',
          fontSize: 'medium',
          theme: 'dark',
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /appearance/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /appearance/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/theme/i)).toHaveValue('dark');
      });

      expect(screen.getByLabelText(/accent color/i)).toHaveValue('#3b82f6');
      expect(screen.getByLabelText(/font size/i)).toHaveValue('medium');
    });

    it('changes theme', async () => {
      const { fetchSettings, updateSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        appearance: {
          theme: 'light',
        },
      });
      vi.mocked(updateSettings).mockResolvedValue({
        appearance: {
          theme: 'dark',
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /appearance/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /appearance/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/theme/i)).toBeInTheDocument();
      });

      const themeSelect = screen.getByLabelText(/theme/i);
      await userEvent.click(themeSelect);
      await userEvent.click(screen.getByRole('option', { name: /dark/i }));

      await waitFor(() => {
        expect(document.documentElement).toHaveClass('dark');
      });
    });

    it('selects custom accent color', async () => {
      const { fetchSettings, updateSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        appearance: {
          accentColor: '#3b82f6',
        },
      });
      vi.mocked(updateSettings).mockResolvedValue({
        appearance: {
          accentColor: '#ef4444',
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /appearance/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /appearance/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/accent color/i)).toBeInTheDocument();
      });

      const colorPicker = screen.getByLabelText(/accent color/i);
      await userEvent.clear(colorPicker);
      await userEvent.type(colorPicker, '#ef4444');

      const saveButton = screen.getByRole('button', { name: /save/i });
      await userEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/settings saved/i)).toBeInTheDocument();
      });
    });

    it('adjusts font size', async () => {
      const { fetchSettings, updateSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        appearance: {
          fontSize: 'medium',
        },
      });
      vi.mocked(updateSettings).mockResolvedValue({
        appearance: {
          fontSize: 'large',
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /appearance/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /appearance/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/font size/i)).toBeInTheDocument();
      });

      const fontSizeSelect = screen.getByLabelText(/font size/i);
      await userEvent.click(fontSizeSelect);
      await userEvent.click(screen.getByRole('option', { name: /large/i }));

      await waitFor(() => {
        expect(document.documentElement).toHaveClass('text-lg');
      });
    });
  });

  describe('Integration Settings', () => {
    it('displays available integrations', async () => {
      const { fetchSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        integrations: {
          github: { connected: true, repo: 'org/repo' },
          jira: { connected: false },
          slack: { channel: '#general', connected: true },
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /integrations/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /integrations/i }));

      await waitFor(() => {
        expect(screen.getByText(/github/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/jira/i)).toBeInTheDocument();
      expect(screen.getByText(/slack/i)).toBeInTheDocument();
    });

    it('shows connected integration status', async () => {
      const { fetchSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        integrations: {
          github: { connected: true, repo: 'org/repo' },
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /integrations/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /integrations/i }));

      await waitFor(() => {
        const githubSection = screen.getByTestId('integration-github');
        expect(within(githubSection).getByText(/connected/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/org\/repo/i)).toBeInTheDocument();
    });

    it('connects new integration', async () => {
      const { fetchSettings, updateSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        integrations: {
          jira: { connected: false },
        },
      });
      vi.mocked(updateSettings).mockResolvedValue({
        integrations: {
          jira: { connected: true, project: 'PROJ' },
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /integrations/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /integrations/i }));

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /connect jira/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('button', { name: /connect jira/i }));

      await waitFor(() => {
        expect(screen.getByRole('dialog', { name: /connect jira/i })).toBeInTheDocument();
      });

      await userEvent.type(screen.getByLabelText(/api token/i), 'test-token');
      await userEvent.type(screen.getByLabelText(/project key/i), 'PROJ');

      await userEvent.click(screen.getByRole('button', { name: /connect/i }));

      await waitFor(() => {
        expect(screen.getByText(/jira connected/i)).toBeInTheDocument();
      });
    });

    it('disconnects integration', async () => {
      const { fetchSettings, updateSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        integrations: {
          slack: { channel: '#general', connected: true },
        },
      });
      vi.mocked(updateSettings).mockResolvedValue({
        integrations: {
          slack: { connected: false },
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /integrations/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /integrations/i }));

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /disconnect slack/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('button', { name: /disconnect slack/i }));

      await waitFor(() => {
        expect(screen.getByText(/confirm disconnect/i)).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('button', { name: /confirm/i }));

      await waitFor(() => {
        expect(screen.getByText(/slack disconnected/i)).toBeInTheDocument();
      });
    });

    it('configures integration settings', async () => {
      const { fetchSettings, updateSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        integrations: {
          slack: {
            channel: '#general',
            connected: true,
            notifications: ['item-created', 'item-updated'],
          },
        },
      });
      vi.mocked(updateSettings).mockResolvedValue({
        integrations: {
          slack: {
            channel: '#dev',
            connected: true,
            notifications: ['item-created', 'item-updated', 'item-deleted'],
          },
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /integrations/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /integrations/i }));

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /configure slack/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('button', { name: /configure slack/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/channel/i)).toBeInTheDocument();
      });

      const channelInput = screen.getByLabelText(/channel/i);
      await userEvent.clear(channelInput);
      await userEvent.type(channelInput, '#dev');

      await userEvent.click(screen.getByLabelText(/notify on delete/i));

      await userEvent.click(screen.getByRole('button', { name: /save/i }));

      await waitFor(() => {
        expect(screen.getByText(/settings saved/i)).toBeInTheDocument();
      });
    });
  });

  describe('Security Settings', () => {
    it('displays security options', async () => {
      const { fetchSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        security: {
          allowedIPs: [],
          sessionTimeout: 3600,
          twoFactorEnabled: false,
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /security/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /security/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/two-factor authentication/i)).toBeInTheDocument();
      });

      expect(screen.getByLabelText(/session timeout/i)).toBeInTheDocument();
    });

    it('enables two-factor authentication', async () => {
      const { fetchSettings, updateSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        security: {
          twoFactorEnabled: false,
        },
      });
      vi.mocked(updateSettings).mockResolvedValue({
        security: {
          twoFactorEnabled: true,
          twoFactorSecret: 'SECRET',
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /security/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /security/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/two-factor authentication/i)).toBeInTheDocument();
      });

      await userEvent.click(screen.getByLabelText(/two-factor authentication/i));

      await waitFor(() => {
        expect(screen.getByText(/scan qr code/i)).toBeInTheDocument();
      });

      await userEvent.type(screen.getByLabelText(/verification code/i), '123456');
      await userEvent.click(screen.getByRole('button', { name: /verify/i }));

      await waitFor(() => {
        expect(screen.getByText(/two-factor enabled/i)).toBeInTheDocument();
      });
    });

    it('configures session timeout', async () => {
      const { fetchSettings, updateSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        security: {
          sessionTimeout: 3600,
        },
      });
      vi.mocked(updateSettings).mockResolvedValue({
        security: {
          sessionTimeout: 7200,
        },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /security/i })).toBeInTheDocument();
      });

      await userEvent.click(screen.getByRole('link', { name: /security/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/session timeout/i)).toBeInTheDocument();
      });

      const timeoutSelect = screen.getByLabelText(/session timeout/i);
      await userEvent.click(timeoutSelect);
      await userEvent.click(screen.getByRole('option', { name: /2 hours/i }));

      const saveButton = screen.getByRole('button', { name: /save/i });
      await userEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/settings saved/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error when settings fail to load', async () => {
      const { fetchSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockRejectedValue(new Error('Failed to load settings'));

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByText(/failed to load settings/i)).toBeInTheDocument();
      });

      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });

    it('shows error when update fails', async () => {
      const { fetchSettings, updateSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        general: { siteName: 'Test' },
      });
      vi.mocked(updateSettings).mockRejectedValue(new Error('Update failed'));

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByLabelText(/site name/i)).toBeInTheDocument();
      });

      const input = screen.getByLabelText(/site name/i);
      await userEvent.clear(input);
      await userEvent.type(input, 'New Name');

      const saveButton = screen.getByRole('button', { name: /save/i });
      await userEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/update failed/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper form labels', async () => {
      const { fetchSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        general: { siteName: 'Test' },
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        const inputs = screen.getAllByRole('textbox');
        inputs.forEach((input) => {
          expect(input).toHaveAccessibleName();
        });
      });
    });

    it('supports keyboard navigation', async () => {
      const { fetchSettings } = await import('@/api/settings');

      vi.mocked(fetchSettings).mockResolvedValue({
        general: {},
      });

      render(<RouterProvider router={router} />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /general/i })).toBeInTheDocument();
      });

      await userEvent.tab();
      expect(screen.getByRole('link', { name: /general/i })).toHaveFocus();

      await userEvent.tab();
      expect(screen.getByRole('link', { name: /notifications/i })).toHaveFocus();
    });
  });
});
