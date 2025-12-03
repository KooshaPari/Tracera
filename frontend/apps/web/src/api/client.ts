import createClient from 'openapi-fetch'

// API client configuration
const API_BASE_URL = import.meta.env?.VITE_API_URL || 'http://localhost:8000'

// Generic paths type - will be replaced with generated types when available
type Paths = Record<string, any>

// Create typed API client
export const apiClient = createClient<Paths>({
  baseUrl: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Validate apiClient is initialized
if (!apiClient) {
  console.error('API client failed to initialize')
  throw new Error('API client initialization failed')
}

// Add request interceptor for auth tokens
apiClient.use({
  onRequest: async ({ request }) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      request.headers.set('Authorization', `Bearer ${token}`)
    }
    return request
  },
  onResponse: async ({ response }) => {
    // Handle unauthorized
    if (response.status === 401) {
      localStorage.removeItem('auth_token')
      if (typeof globalThis.window !== 'undefined') {
        globalThis.window.location.href = '/login'
      }
    }
    return response
  },
})

// Helper to handle API errors
export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: unknown
  ) {
    super(`API Error ${status}: ${statusText}`)
    this.name = 'ApiError'
  }
}

// Helper to safely get a promise from API client methods
export function safeApiCall<T>(
  apiCall: Promise<{ data?: T; error?: unknown; response: Response }> | null | undefined
): Promise<{ data?: T; error?: unknown; response: Response }> {
  if (!apiCall) {
    return Promise.reject(new ApiError(500, 'API request failed: promise is null', undefined))
  }
  return apiCall
}

export async function handleApiResponse<T>(
  promise: Promise<{ data?: T; error?: unknown; response: Response }> | null | undefined
): Promise<T> {
  if (!promise) {
    throw new ApiError(500, 'API request failed: promise is null', undefined)
  }

  const { data, error, response } = await promise

  if (error) {
    throw new ApiError(response?.status || 500, response?.statusText || 'Unknown error', error)
  }

  if (!data) {
    throw new ApiError(response?.status || 500, 'No data returned', undefined)
  }

  return data
}

// Export API base URL for WebSocket connections
export { API_BASE_URL }
