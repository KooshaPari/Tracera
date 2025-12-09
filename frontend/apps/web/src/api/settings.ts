// Settings API stub
import { apiClient, handleApiResponse, safeApiCall } from './client'

export interface Settings {
  general: {
    theme?: 'light' | 'dark' | 'system'
    language?: string
    timezone?: string
  }
  notifications?: {
    email?: boolean
    push?: boolean
    inApp?: boolean
  }
  security?: {
    twoFactor?: boolean
    sessionTimeout?: number
  }
}

export const fetchSettings = async (): Promise<Settings> => {
  // Try to fetch from settings endpoint, fallback to defaults
  try {
    const response = await safeApiCall(apiClient.GET('/api/v1/settings', {}))
    if (response.data) {
      return response.data as Settings
    }
  } catch {
    // Return default settings if endpoint doesn't exist
  }
  return {
    general: {
      theme: 'system',
      language: 'en',
    },
    notifications: {
      email: true,
      push: true,
      inApp: true,
    },
    security: {
      twoFactor: false,
      sessionTimeout: 30,
    },
  }
}

export const updateSettings = async (settings: Partial<Settings>): Promise<Settings> => {
  try {
    const response = await apiClient.PUT('/api/v1/settings', {
      body: settings,
    })
    if (response.data) {
      return response.data as Settings
    }
  } catch {
    // Return merged settings if endpoint doesn't exist
  }
  return {
    general: {},
    ...settings,
  } as Settings
}
