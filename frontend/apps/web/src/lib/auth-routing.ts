import { useAuthStore } from '@/stores/authStore';

export const hasStoredTokenOrIsE2E = (): boolean => {
  if (typeof globalThis.window === 'undefined') {
    return false;
  }

  const { isAuthenticated, token, user } = useAuthStore.getState();
  const hasToken = Boolean(token && token.trim());

  if ((globalThis as { __E2E__?: boolean }).__E2E__ || navigator?.webdriver) {
    return true;
  }

  return Boolean(isAuthenticated && user && hasToken);
};
