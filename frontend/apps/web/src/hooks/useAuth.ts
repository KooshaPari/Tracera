import type { User } from '../stores/authStore';

import { useAuthStore } from '../stores/authStore';

export function useAuth() {
  const { user, token, isAuthenticated, isLoading, loginWithCode, logout, refreshToken, updateProfile } =
    useAuthStore();

  return {
    isAuthenticated,
    isLoading,
    login: loginWithCode,
    loginWithCode,
    logout,
    refreshToken,
    token,
    updateProfile,
    user,
  };
}

export function useUser(): User | null {
  return useAuthStore((state) => state.user);
}

export function useIsAuthenticated(): boolean {
  return useAuthStore((state) => state.isAuthenticated);
}
