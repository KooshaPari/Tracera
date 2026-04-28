import type { ReactNode } from 'react';

import { useAuthStore } from '../stores/auth-store';

/**
 * Auth token context - delegates to auth-store (Zustand).
 * Kept for compatibility with code that imports AuthTokenProvider/useAuthToken.
 */
export function AuthTokenProvider({ children }: { children: ReactNode }) {
  return <>{children}</>;
}

export function useAuthToken() {
  const token = useAuthStore((state) => state.token);
  return token ?? undefined;
}
