import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: string
  email: string
  name?: string
  avatar?: string
  role?: string
  metadata?: Record<string, any>
}

interface AuthState {
  // Auth state
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean

  // Actions
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
  updateProfile: (updates: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      // Actions
      setUser: (user) => {
        set({
          user,
          isAuthenticated: !!user,
        })
      },

      setToken: (token) => {
        if (token) {
          localStorage.setItem('auth_token', token)
        } else {
          localStorage.removeItem('auth_token')
        }
        set({ token })
      },

      login: async (email, _password) => {
        set({ isLoading: true })
        try {
          // TODO: Implement actual login API call
          // For now, mock authentication
          const mockUser: User = {
            id: '1',
            email,
            name: email.split('@')[0],
          }
          const mockToken = 'mock-jwt-token'

          get().setToken(mockToken)
          get().setUser(mockUser)
        } catch (error) {
          console.error('Login failed:', error)
          throw error
        } finally {
          set({ isLoading: false })
        }
      },

      logout: () => {
        get().setToken(null)
        get().setUser(null)
        set({ isAuthenticated: false })
      },

      refreshToken: async () => {
        // TODO: Implement token refresh logic
        console.log('Token refresh not implemented yet')
      },

      updateProfile: (updates) => {
        const currentUser = get().user
        if (currentUser) {
          set({
            user: { ...currentUser, ...updates },
          })
        }
      },
    }),
    {
      name: 'tracertm-auth-store',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
