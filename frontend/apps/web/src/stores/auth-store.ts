import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';

import { getCSRFHeaders } from '@/lib/csrf';
import { logger } from '@/lib/logger';

const API_BASE_URL_DEFAULT = 'http://localhost:4000';
const AUTH_TOKEN_KEY = 'auth_token';
const HTTP_UNAUTHORIZED = Number('401');
const REFRESH_INTERVAL_MINUTES = Number('20');
const SECONDS_PER_MINUTE = Number('60');
const MILLISECONDS_PER_SECOND = Number('1000');
const BODY_PREVIEW_LIMIT = Number('150');
const REFRESH_INTERVAL_MS = REFRESH_INTERVAL_MINUTES * SECONDS_PER_MINUTE * MILLISECONDS_PER_SECOND;

interface StorageAdapter {
  getItem: (key: string) => string | null;
  removeItem: (key: string) => void;
  setItem: (key: string, value: string) => void;
}

const noopStorage: StorageAdapter = {
  getItem: (_key: string): string | null => null,
  removeItem: (_key: string): void => {},
  setItem: (_key: string, _value: string): void => {},
};

const getStorage = (): StorageAdapter => {
  // Check if we're in a browser environment with proper localStorage
  if (
    typeof globalThis.window === 'undefined' ||
    typeof localStorage === 'undefined' ||
    typeof localStorage.getItem !== 'function'
  ) {
    return noopStorage;
  }
  return localStorage;
};

const getApiBaseUrl = (): string => import.meta.env.VITE_API_URL || API_BASE_URL_DEFAULT;

const isRecordObject = (value: unknown): value is Record<string, unknown> =>
  Object.prototype.toString.call(value) === '[object Object]';

const readStringField = (obj: Record<string, unknown>, key: string): string | undefined => {
  const value = obj[key];
  if (typeof value === 'string') {
    return value;
  }
  return undefined;
};

/**
 * User metadata from authentication
 */
export type UserMetadata = Record<string, string | number | boolean | object | null | undefined>;

export interface User {
  avatar?: string | undefined;
  email: string;
  id: string;
  metadata?: UserMetadata | undefined;
  name?: string | undefined;
  role?: string | undefined;
}

export interface Account {
  account_type: string;
  id: string;
  name: string;
  slug: string;
}

const isUser = (value: unknown): value is User => {
  if (!isRecordObject(value)) {
    return false;
  }
  return typeof value['id'] === 'string' && typeof value['email'] === 'string';
};

const isAccount = (value: unknown): value is Account => {
  if (!isRecordObject(value)) {
    return false;
  }
  return (
    typeof value['id'] === 'string' &&
    typeof value['name'] === 'string' &&
    typeof value['slug'] === 'string' &&
    typeof value['account_type'] === 'string'
  );
};

const parseLoginResponse = (
  data: unknown,
): { user: User; token?: string | undefined } | undefined => {
  if (!isRecordObject(data)) {
    return undefined;
  }
  const userValue = data['user'];
  if (!isUser(userValue)) {
    return undefined;
  }
  // Check for 'token' (backend) or 'access_token' (legacy/standard)
  const token = readStringField(data, 'token') ?? readStringField(data, 'access_token');
  return { token, user: userValue };
};

const parseSessionResponse = (data: unknown): { account?: Account; user?: User } | undefined => {
  if (!isRecordObject(data)) {
    return undefined;
  }
  const response: { account?: Account; user?: User } = {};
  const userValue = data['user'];
  if (isUser(userValue)) {
    response.user = userValue;
  }
  const accountValue = data['account'];
  if (isAccount(accountValue)) {
    response.account = accountValue;
  }
  return response;
};

const parseRefreshResponse = (data: unknown): { token?: string; user?: User } | undefined => {
  if (!isRecordObject(data)) {
    return undefined;
  }
  const response: { token?: string; user?: User } = {};
  const userValue = data['user'];
  if (isUser(userValue)) {
    response.user = userValue;
  }
  const token = readStringField(data, 'token') ?? readStringField(data, 'access_token');
  if (token !== undefined) {
    response.token = token;
  }
  return response;
};

const parseAccountResponse = (data: unknown): { account?: Account } | undefined => {
  if (!isRecordObject(data)) {
    return undefined;
  }
  const accountValue = data['account'];
  if (isAccount(accountValue)) {
    return { account: accountValue };
  }
  return {};
};

interface AuthStateData {
  account: Account | null;
  authKitRefreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  refreshTimer: NodeJS.Timeout | null;
  token: string | null;
  user: User | null;
}

interface AuthStateActions {
  initializeAutoRefresh: () => void;
  loginWithCode: (code: string, state: string) => Promise<void>;
  logout: () => Promise<void>;
  redirectToAuthKit: (screenHint?: string) => Promise<void>;
  refreshToken: () => Promise<void>;
  setAccount: (account: Account | null) => void;
  setToken: (token: string | null) => void;
  setUser: (user: User | null) => void;
  stopAutoRefresh: () => void;
  switchAccount: (accountId: string) => Promise<void>;
  updateProfile: (updates: Partial<User>) => void;
  validateSession: () => Promise<boolean>;
}

type AuthState = AuthStateData & AuthStateActions;

type StoreSetter = (
  partial: Partial<AuthState> | ((state: AuthState) => Partial<AuthState> | AuthState),
) => void;

type StoreGetter = () => AuthState;

const createInitialState = (): AuthStateData => ({
  account: null,
  authKitRefreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  refreshTimer: null,
  token: null,
  user: null,
});

const normalizeToken = (token: string | null): string | null => {
  const normalized = token?.trim();
  return normalized ?? null;
};

const persistToken = (token: string | null): void => {
  if (typeof localStorage === 'undefined') {
    return;
  }
  if (token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
  } else {
    localStorage.removeItem(AUTH_TOKEN_KEY);
  }
};

const fetchJson = async (
  path: string,
  options: RequestInit,
): Promise<{ data?: unknown; response: Response }> => {
  const headers = new Headers(options.headers ?? {});
  const csrfHeaders = getCSRFHeaders(options.method ?? 'GET');
  for (const [key, value] of Object.entries(csrfHeaders)) {
    headers.set(key, value);
  }

  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...options,
    headers,
  });
  let data: unknown;
  try {
    data = await response.json();
  } catch {
    data = undefined;
  }
  return { data, response };
};

const createSetterActions = (
  set: StoreSetter,
): Pick<AuthStateActions, 'setAccount' | 'setToken' | 'setUser'> => ({
  setAccount: (account): void => {
    set({ account });
  },
  setToken: (token): void => {
    const normalizedToken = normalizeToken(token);
    persistToken(normalizedToken);
    set({ token: normalizedToken });
  },
  setUser: (user): void => {
    set({
      isAuthenticated: Boolean(user),
      user,
    });
  },
});

const createAuthKitActions = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<AuthStateActions, 'loginWithCode' | 'redirectToAuthKit'> => ({
  loginWithCode: async (code, state): Promise<void> => {
    set({ isLoading: true });
    try {
      if (!code || !state) {
        throw new Error('Authorization code and state are required');
      }

      const { data, response } = await fetchJson('/api/v1/auth/authkit/callback', {
        body: JSON.stringify({ code, state }),
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
      });

      if (!response.ok) {
        const detail =
          isRecordObject(data) && typeof data['error'] === 'string'
            ? data['error']
            : 'Authentication failed';
        throw new Error(`${detail}: ${response.status}`);
      }

      const parsed = parseLoginResponse(data);
      if (!parsed) {
        throw new Error('Invalid response from callback endpoint');
      }

      get().setUser(parsed.user);
      if (parsed.token) {
        get().setToken(parsed.token);
      }
      // Store AuthKit refresh token
      if (isRecordObject(data)) {
        const refreshToken = readStringField(data as Record<string, unknown>, 'refresh_token');
        if (refreshToken) {
          set({ authKitRefreshToken: refreshToken });
        }
      }
      get().initializeAutoRefresh();
    } catch (error) {
      set({ authKitRefreshToken: null, isAuthenticated: false, token: null, user: null });
      logger.error('AuthKit login failed:', error);
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },
  redirectToAuthKit: async (screenHint?: string): Promise<void> => {
    set({ isLoading: true });
    try {
      const params = screenHint ? `?screen_hint=${encodeURIComponent(screenHint)}` : '';
      const { data, response } = await fetchJson(`/api/v1/auth/authkit/authorize${params}`, {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        method: 'GET',
      });

      if (!response.ok) {
        const bodyHint =
          data !== undefined
            ? ` (body: ${typeof data === 'string' ? data.slice(0, 100) : JSON.stringify(data)?.slice(0, 100)})`
            : ' (body: non-JSON or empty)';
        throw new Error(`Failed to get authorization URL: ${response.status}${bodyHint}`);
      }

      if (!isRecordObject(data)) {
        const typeHint =
          data === undefined ? 'undefined (JSON parse failed or empty body)' : typeof data;
        let bodyPreview = String(data);
        if (typeof data === 'string') {
          bodyPreview = data.slice(0, BODY_PREVIEW_LIMIT);
        } else if (data !== null && typeof data === 'object') {
          bodyPreview = JSON.stringify(data).slice(0, BODY_PREVIEW_LIMIT);
        }
        logger.error('AuthKit authorize: invalid response shape', {
          type: typeHint,
          bodyPreview,
          url: `${getApiBaseUrl()}/api/v1/auth/authkit/authorize`,
        });
        throw new Error(
          `Invalid authorization response: expected JSON object with authorization_url, got ${typeHint}. ` +
            `Check that the backend at ${getApiBaseUrl()} is running and returns valid JSON.`,
        );
      }

      const authorizationUrl = readStringField(
        data as Record<string, unknown>,
        'authorization_url',
      );
      if (!authorizationUrl) {
        throw new Error('No authorization URL in response');
      }

      // Store state for CSRF verification on callback
      const authState = readStringField(data as Record<string, unknown>, 'state');
      if (authState) {
        sessionStorage.setItem('authkit_state', authState);
      }

      // Redirect to AuthKit hosted UI
      window.location.href = authorizationUrl;
    } catch (error) {
      set({ isLoading: false });
      logger.error('AuthKit redirect failed:', error);
      throw error;
    }
  },
});

const createLogoutAction = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<AuthStateActions, 'logout'> => ({
  logout: async (): Promise<void> => {
    try {
      get().stopAutoRefresh();
      await fetchJson('/api/v1/auth/logout', {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
      }).catch(() => {
        logger.warn('Logout API call failed, clearing local state');
      });
    } catch (error) {
      logger.error('Logout error:', error);
    } finally {
      get().setToken(null);
      get().setUser(null);
      set({ authKitRefreshToken: null, isAuthenticated: false });

      // Clear AuthKit state from session storage
      if (typeof sessionStorage !== 'undefined') {
        sessionStorage.removeItem('authkit_state');
      }

      // Notify React Query to clear cache on logout
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('auth:logout'));
      }
    }
  },
});

const createSessionActions = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<AuthStateActions, 'refreshToken' | 'switchAccount' | 'validateSession'> => ({
  refreshToken: async (): Promise<void> => {
    try {
      const currentRefreshToken = get().authKitRefreshToken;
      if (!currentRefreshToken) {
        await get().logout();
        return;
      }

      const { data, response } = await fetchJson('/api/v1/auth/authkit/refresh', {
        body: JSON.stringify({ refresh_token: currentRefreshToken }),
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
      });

      if (!response.ok) {
        await get().logout();
        return;
      }

      const parsed = parseRefreshResponse(data);
      if (parsed?.token) {
        get().setToken(parsed.token);
      }
      if (isRecordObject(data)) {
        const newRefreshToken = readStringField(data, 'refresh_token');
        if (newRefreshToken) {
          set({ authKitRefreshToken: newRefreshToken });
        }
      }
      if (parsed?.user) {
        get().setUser(parsed.user);
      }
    } catch (error) {
      logger.error('Token refresh failed:', error);
      await get().logout();
    }
  },
  switchAccount: async (accountId: string): Promise<void> => {
    if (!get().user) {
      throw new Error('Not authenticated');
    }

    try {
      const { data, response } = await fetchJson(`/api/v1/accounts/${accountId}/switch`, {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to switch account');
      }

      const parsed = parseAccountResponse(data);
      if (parsed?.account) {
        get().setAccount(parsed.account);
      }
    } catch (error) {
      logger.error('Failed to switch account:', error);
      throw error;
    }
  },
  validateSession: async (): Promise<boolean> => {
    try {
      const token = normalizeToken(get().token);
      if (!token) {
        return false;
      }

      const { data, response } = await fetchJson('/api/v1/auth/me', {
        credentials: 'include',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        method: 'GET',
      });

      if (response.status === HTTP_UNAUTHORIZED) {
        await get().logout();
        return false;
      }

      if (!response.ok) {
        throw new Error(`Session validation failed: ${response.status}`);
      }

      const parsed = parseSessionResponse(data);
      if (parsed?.user) {
        get().setUser(parsed.user);
      }
      if (parsed?.account) {
        get().setAccount(parsed.account);
      }

      return true;
    } catch (error) {
      logger.error('Session validation error:', error);
      await get().logout();
      return false;
    }
  },
});

const createProfileActions = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<AuthStateActions, 'updateProfile'> => ({
  updateProfile: (updates): void => {
    const currentUser = get().user;
    if (currentUser) {
      set({ user: { ...currentUser, ...updates } });
    }
  },
});

const createAutoRefreshActions = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<AuthStateActions, 'initializeAutoRefresh' | 'stopAutoRefresh'> => ({
  initializeAutoRefresh: (): void => {
    get().stopAutoRefresh();

    const timer = setInterval(() => {
      get()
        .refreshToken()
        .catch((error) => {
          logger.error('Auto refresh failed:', error);
        });
    }, REFRESH_INTERVAL_MS);

    set({ refreshTimer: timer });
  },
  stopAutoRefresh: (): void => {
    const timer = get().refreshTimer;
    if (timer) {
      clearInterval(timer);
      set({ refreshTimer: null });
    }
  },
});

const buildAuthStore = (set: StoreSetter, get: StoreGetter): AuthState => ({
  ...createInitialState(),
  ...createSetterActions(set),
  ...createAuthKitActions(set, get),
  ...createLogoutAction(set, get),
  ...createSessionActions(set, get),
  ...createProfileActions(set, get),
  ...createAutoRefreshActions(set, get),
});

export const useAuthStore = create<AuthState>()(
  persist<AuthState>((set, get) => buildAuthStore(set, get), {
    name: 'tracertm-auth-store',
    partialize: (state: AuthState) =>
      ({
        account: state.account,
        authKitRefreshToken: state.authKitRefreshToken,
        isAuthenticated: state.isAuthenticated,
        token: state.token,
        user: state.user,
      }) as unknown as AuthState,
    storage: createJSONStorage(() => getStorage()),
  }),
);
