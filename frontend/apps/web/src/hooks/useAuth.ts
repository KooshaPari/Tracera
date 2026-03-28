import type { User } from '../stores/authStore';

import { useAuthStore } from '../stores/authStore';

export function useAuth() {
  const { user, token, isAuthenticated, isLoading, logout, refreshToken, updateProfile, redirectToAuthKit } =
    useAuthStore();

  return {
    isAuthenticated,
    isLoading,
    login: redirectToAuthKit,
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
