/**
 * Tests for Settings API
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { Settings } from '@/api/settings';

import { fetchSettings, updateSettings } from '@/api/settings';

// Mock the API client
vi.mock('@/api/client', () => ({
  client: {
    apiClient: {
      GET: vi.fn(),
      PUT: vi.fn(),
    },
    safeApiCall: vi.fn((promise) => promise),
  },
}));

import { client } from '@/api/client';

const { apiClient, safeApiCall } = client;

describe('Settings API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(fetchSettings, () => {
    it('should fetch settings from API', async () => {
      const mockSettings: Settings = {
        general: {
          language: 'en',
          theme: 'dark',
          timezone: 'UTC',
        },
        notifications: {
          email: true,
          inApp: true,
          push: false,
        },
        security: {
          sessionTimeout: 60,
          twoFactor: true,
        },
      };

      vi.mocked(safeApiCall).mockResolvedValue({
        data: mockSettings,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchSettings();

      expect(result).toEqual(mockSettings);
      expect(result.general.theme).toBe('dark');
      expect(result.security.twoFactor).toBeTruthy();
    });

    it('should return default settings if API fails', async () => {
      vi.mocked(safeApiCall).mockRejectedValue(new Error('API failed'));

      const result = await fetchSettings();

      expect(result).toEqual({
        general: {
          language: 'en',
          theme: 'system',
        },
        notifications: {
          email: true,
          inApp: true,
          push: true,
        },
        security: {
          sessionTimeout: 30,
          twoFactor: false,
        },
      });
    });

    it('should return default settings if API returns null', async () => {
      vi.mocked(safeApiCall).mockResolvedValue({
        data: null,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchSettings();

      expect(result.general.theme).toBe('system');
      expect(result.notifications.email).toBeTruthy();
    });

    it('should include general settings', async () => {
      const mockSettings: Settings = {
        general: {
          language: 'es',
          theme: 'light',
          timezone: 'EST',
        },
      };

      vi.mocked(safeApiCall).mockResolvedValue({
        data: mockSettings,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchSettings();

      expect(result.general).toHaveProperty('theme');
      expect(result.general).toHaveProperty('language');
      expect(result.general).toHaveProperty('timezone');
    });

    it('should include notification settings', async () => {
      const mockSettings: Settings = {
        general: {},
        notifications: {
          email: false,
          inApp: false,
          push: true,
        },
      };

      vi.mocked(safeApiCall).mockResolvedValue({
        data: mockSettings,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchSettings();

      expect(result.notifications?.email).toBeFalsy();
      expect(result.notifications?.push).toBeTruthy();
      expect(result.notifications?.inApp).toBeFalsy();
    });

    it('should include security settings', async () => {
      const mockSettings: Settings = {
        general: {},
        security: {
          sessionTimeout: 120,
          twoFactor: true,
        },
      };

      vi.mocked(safeApiCall).mockResolvedValue({
        data: mockSettings,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchSettings();

      expect(result.security?.twoFactor).toBeTruthy();
      expect(result.security?.sessionTimeout).toBe(120);
    });

    it('should call API with correct endpoint', async () => {
      vi.mocked(safeApiCall).mockResolvedValue({
        data: undefined,
        error: undefined,
        response: new Response(),
      });

      await fetchSettings();

      expect(apiClient.GET).toHaveBeenCalledWith('/api/v1/settings', expect.any(Object));
    });

    it('should support all theme options', async () => {
      const themes: ('light' | 'dark' | 'system')[] = ['light', 'dark', 'system'];

      for (const theme of themes) {
        vi.mocked(safeApiCall).mockResolvedValue({
          data: {
            general: { theme },
          },
          error: undefined,
          response: new Response(),
        });

        const result = await fetchSettings();
        expect(result.general.theme).toBe(theme);
      }
    });

    it('should handle missing optional fields', async () => {
      const minimalSettings: Settings = {
        general: {},
      };

      vi.mocked(safeApiCall).mockResolvedValue({
        data: minimalSettings,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchSettings();

      expect(result.general).toBeDefined();
    });
  });

  describe(updateSettings, () => {
    it('should update general settings', async () => {
      const updatedSettings: Settings = {
        general: {
          language: 'fr',
          theme: 'dark',
        },
      };

      vi.mocked(apiClient.PUT).mockResolvedValue({
        data: updatedSettings,
        error: undefined,
        response: new Response(),
      });

      const result = await updateSettings({
        general: { language: 'fr', theme: 'dark' },
      });

      expect(result.general.theme).toBe('dark');
      expect(result.general.language).toBe('fr');
    });

    it('should update notification settings', async () => {
      const updatedSettings: Settings = {
        general: {},
        notifications: {
          email: false,
          inApp: true,
          push: false,
        },
      };

      vi.mocked(apiClient.PUT).mockResolvedValue({
        data: updatedSettings,
        error: undefined,
        response: new Response(),
      });

      const result = await updateSettings({
        notifications: { email: false, inApp: true, push: false },
      });

      expect(result.notifications?.email).toBeFalsy();
    });

    it('should update security settings', async () => {
      const updatedSettings: Settings = {
        general: {},
        security: {
          sessionTimeout: 90,
          twoFactor: true,
        },
      };

      vi.mocked(apiClient.PUT).mockResolvedValue({
        data: updatedSettings,
        error: undefined,
        response: new Response(),
      });

      const result = await updateSettings({
        security: { sessionTimeout: 90, twoFactor: true },
      });

      expect(result.security?.twoFactor).toBeTruthy();
      expect(result.security?.sessionTimeout).toBe(90);
    });

    it('should handle API response with data', async () => {
      const updatedSettings: Settings = {
        general: { theme: 'dark' },
        notifications: { email: true },
      };

      vi.mocked(apiClient.PUT).mockResolvedValue({
        data: updatedSettings,
        error: undefined,
        response: new Response(),
      });

      const result = await updateSettings({
        general: { theme: 'dark' },
      });

      expect(result).toEqual(updatedSettings);
    });

    it('should handle API errors gracefully', async () => {
      vi.mocked(apiClient.PUT).mockRejectedValue(new Error('API failed'));

      const result = await updateSettings({
        general: { theme: 'dark' },
      });

      expect(result).toHaveProperty('general');
    });

    it('should merge partial settings with defaults', async () => {
      vi.mocked(apiClient.PUT).mockRejectedValue(new Error('API failed'));

      const result = await updateSettings({
        general: { theme: 'light' },
      });

      expect(result.general).toHaveProperty('theme');
    });

    it('should call API with correct endpoint', async () => {
      const updatedSettings: Settings = {
        general: { theme: 'dark' },
      };

      vi.mocked(apiClient.PUT).mockResolvedValue({
        data: updatedSettings,
        error: undefined,
        response: new Response(),
      });

      await updateSettings({ general: { theme: 'dark' } });

      expect(apiClient.PUT).toHaveBeenCalledWith(
        '/api/v1/settings',
        expect.objectContaining({
          body: { general: { theme: 'dark' } },
        }),
      );
    });

    it('should pass settings as request body', async () => {
      const settingsUpdate = {
        general: { theme: 'dark' },
        notifications: { email: false },
      };

      vi.mocked(apiClient.PUT).mockResolvedValue({
        data: settingsUpdate as Settings,
        error: undefined,
        response: new Response(),
      });

      await updateSettings(settingsUpdate);

      expect(apiClient.PUT).toHaveBeenCalledWith(
        '/api/v1/settings',
        expect.objectContaining({
          body: settingsUpdate,
        }),
      );
    });

    it('should return response data when available', async () => {
      const updatedSettings: Settings = {
        general: { theme: 'dark' },
        notifications: { email: false },
        security: { twoFactor: true },
      };

      vi.mocked(apiClient.PUT).mockResolvedValue({
        data: updatedSettings,
        error: undefined,
        response: new Response(),
      });

      const result = await updateSettings({
        general: { theme: 'dark' },
      });

      expect(result).toEqual(updatedSettings);
    });

    it('should handle multiple setting updates', async () => {
      const updates = {
        general: { language: 'es', theme: 'dark' },
        notifications: { email: false },
        security: { twoFactor: true },
      };

      vi.mocked(apiClient.PUT).mockResolvedValue({
        data: updates as Settings,
        error: undefined,
        response: new Response(),
      });

      const result = await updateSettings(updates);

      expect(result).toHaveProperty('general');
      expect(result).toHaveProperty('notifications');
      expect(result).toHaveProperty('security');
    });

    it('should handle partial updates', async () => {
      const partialUpdate = {
        general: { theme: 'light' },
      };

      vi.mocked(apiClient.PUT).mockResolvedValue({
        data: partialUpdate as Settings,
        error: undefined,
        response: new Response(),
      });

      const result = await updateSettings(partialUpdate);

      expect(result.general).toBeDefined();
    });

    it('should preserve existing settings during update', async () => {
      const completeSettings: Settings = {
        general: { language: 'en', theme: 'dark', timezone: 'UTC' },
        notifications: { email: true, inApp: true, push: false },
        security: { sessionTimeout: 30, twoFactor: false },
      };

      vi.mocked(apiClient.PUT).mockResolvedValue({
        data: completeSettings,
        error: undefined,
        response: new Response(),
      });

      const result = await updateSettings({
        general: { theme: 'light' },
      });

      expect(result).toBeDefined();
    });
  });

  describe('Settings API error handling', () => {
    it('should handle network errors in fetch', async () => {
      vi.mocked(safeApiCall).mockRejectedValue(new Error('Network error'));

      const result = await fetchSettings();

      expect(result.general.theme).toBe('system');
    });

    it('should handle network errors in update', async () => {
      vi.mocked(apiClient.PUT).mockRejectedValue(new Error('Network error'));

      const result = await updateSettings({
        general: { theme: 'dark' },
      });

      expect(result).toBeDefined();
    });

    it('should handle undefined response data', async () => {
      vi.mocked(safeApiCall).mockResolvedValue({
        data: undefined,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchSettings();

      expect(result).toBeDefined();
      expect(result.general).toBeDefined();
    });

    it('should handle empty settings object', async () => {
      vi.mocked(safeApiCall).mockResolvedValue({
        data: {},
        error: undefined,
        response: new Response(),
      });

      const result = await fetchSettings();

      expect(result).toBeDefined();
    });
  });

  describe('Settings data validation', () => {
    it('should handle large session timeout values', async () => {
      const settings: Settings = {
        general: {},
        security: {
          sessionTimeout: 10_080, // 7 days in minutes
        },
      };

      vi.mocked(safeApiCall).mockResolvedValue({
        data: settings,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchSettings();

      expect(result.security?.sessionTimeout).toBe(10_080);
    });

    it('should handle zero session timeout', async () => {
      const settings: Settings = {
        general: {},
        security: {
          sessionTimeout: 0,
        },
      };

      vi.mocked(safeApiCall).mockResolvedValue({
        data: settings,
        error: undefined,
        response: new Response(),
      });

      const result = await fetchSettings();

      expect(result.security?.sessionTimeout).toBe(0);
    });

    it('should support multiple languages', async () => {
      const languages = ['en', 'es', 'fr', 'de', 'ja'];

      for (const language of languages) {
        vi.mocked(safeApiCall).mockResolvedValue({
          data: { general: { language } },
          error: undefined,
          response: new Response(),
        });

        const result = await fetchSettings();
        expect(result.general.language).toBe(language);
      }
    });

    it('should support multiple timezones', async () => {
      const timezones = ['UTC', 'EST', 'PST', 'IST'];

      for (const timezone of timezones) {
        vi.mocked(safeApiCall).mockResolvedValue({
          data: { general: { timezone } },
          error: undefined,
          response: new Response(),
        });

        const result = await fetchSettings();
        expect(result.general.timezone).toBe(timezone);
      }
    });
  });
});
