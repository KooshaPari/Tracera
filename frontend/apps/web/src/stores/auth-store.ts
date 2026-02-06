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
const REFRESH_INTERVAL_MS = REFRESH_INTERVAL_MINUTES * SECONDS_PER_MINUTE * MILLISECONDS_PER_SECOND;

// SSR-safe storage that only accesses localStorage on the client
const noopStorage = {
  getItem: (_key: string) => null,
  removeItem: (_key: string) => {},
  setItem: (_key: string, _value: string) => {},
};

const getStorage = () => {
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
  avatar?: string;
  email: string;
  id: string;
  metadata?: UserMetadata;
  name?: string;
  role?: string;
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

const parseLoginResponse = (data: unknown): { user: User; token?: string } | undefined => {
  if (!isRecordObject(data)) {
    return undefined;
  }
  const userValue = data['user'];
  if (!isUser(userValue)) {
    return undefined;
  }
  // Check for 'token' (backend) or 'access_token' (legacy/standard)
  const token = readStringField(data, 'token') || readStringField(data, 'access_token');
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
  const token = readStringField(data, 'token') || readStringField(data, 'access_token');
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
  isAuthenticated: boolean;
  isLoading: boolean;
  refreshTimer: NodeJS.Timeout | null;
  token: string | null;
  user: User | null;
}

interface AuthStateActions {
  initializeAutoRefresh: () => void;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
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
  isAuthenticated: false,
  isLoading: false,
  refreshTimer: null,
  token: null,
  user: null,
});

const normalizeToken = (token: string | null): string | null => {
  const normalized = token?.trim();
  return normalized ? normalized : null;
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
  const headers = new Headers(options.headers || {});
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
  setAccount: (account) => set({ account }),
  setToken: (token) => {
    const normalizedToken = normalizeToken(token);
    persistToken(normalizedToken);
    set({ token: normalizedToken });
  },
  setUser: (user) => {
    set({
      isAuthenticated: Boolean(user),
      user,
    });
  },
});

const createLoginAction = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<AuthStateActions, 'login'> => ({
  login: async (email, password) => {
    set({ isLoading: true });
    try {
      if (!email || !password) {
        throw new Error('Email and password are required');
      }

      const { data, response } = await fetchJson('/api/v1/auth/login', {
        body: JSON.stringify({ email, password }),
        credentials: 'include', // Important for HttpOnly cookies
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
      });

      if (!response.ok) {
        const detail =
          isRecordObject(data) && typeof data['error'] === 'string'
            ? data['error']
            : 'Login failed';
        throw new Error(`${detail}: ${response.status}`);
      }

      const parsed = parseLoginResponse(data);
      if (!parsed) {
        throw new Error('Invalid response from login endpoint');
      }

      get().setUser(parsed.user);
      if (parsed.token) {
        get().setToken(parsed.token);
      }
      get().initializeAutoRefresh();
    } catch (error) {
      set({ isAuthenticated: false, token: null, user: null });
      logger.error('Login failed:', error);
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },
});

const createLogoutAction = (
  set: StoreSetter,
  get: StoreGetter,
): Pick<AuthStateActions, 'logout'> => ({
  logout: async () => {
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
      set({ isAuthenticated: false });

      // Notify React Query to clear cache on logout
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('auth:logout'));
      }
    }
  },
});

const createSessionActions = (
  get: StoreGetter,
): Pick<AuthStateActions, 'refreshToken' | 'switchAccount' | 'validateSession'> => ({
  refreshToken: async () => {
    try {
      const { data, response } = await fetchJson('/api/v1/auth/refresh', {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
      });

      if (!response.ok) {
        await get().logout();
        return;
      }

      const parsed = parseRefreshResponse(data);
      if (parsed?.user) {
        get().setUser(parsed.user);
      }
      if (parsed?.token) {
        get().setToken(parsed.token);
      }
    } catch (error) {
      logger.error('Token refresh failed:', error);
      await get().logout();
    }
  },
  switchAccount: async (accountId: string) => {
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
  validateSession: async () => {
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
  updateProfile: (updates) => {
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
  initializeAutoRefresh: () => {
    get().stopAutoRefresh();

    const timer = setInterval(() => {
      get()
        .refreshToken()
        .catch((error) => logger.error('Auto refresh failed:', error));
    }, REFRESH_INTERVAL_MS);

    set({ refreshTimer: timer });
  },
  stopAutoRefresh: () => {
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
  ...createLoginAction(set, get),
  ...createLogoutAction(set, get),
  ...createSessionActions(get),
  ...createProfileActions(set, get),
  ...createAutoRefreshActions(set, get),
});

export const useAuthStore = create<AuthState>()(
  persist((set, get) => buildAuthStore(set, get), {
    name: 'tracertm-auth-store',
    partialize: (state) => ({
      account: state.account,
      isAuthenticated: state.isAuthenticated,
      token: state.token,
      user: state.user,
    }),
    storage: createJSONStorage(() => getStorage()),
  }),
);
