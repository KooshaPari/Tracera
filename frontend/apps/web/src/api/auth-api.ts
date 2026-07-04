import type {
  AuthKitAuthorizeResponse,
  AuthKitCallbackResponse,
  AuthKitRefreshResponse,
  AuthResponse,
  ChangePasswordRequest,
  ResetPasswordConfirm,
  ResetPasswordRequest,
  UpdateUserProfileRequest,
  User,
} from './auth-types';

import authConstants from './auth-constants';
import { AuthError } from './auth-types';
import { ensureCSRFToken, getStoredToken, handleAuthResponse } from './auth-utils';
import { client } from './client';

const { apiClient } = client;
const { safeApiCall } = client;

const get = apiClient.GET.bind(apiClient);
const post = apiClient.POST.bind(apiClient);
const put = apiClient.PUT.bind(apiClient);
const del = apiClient.DELETE.bind(apiClient);

const fetchCurrentUser = async (): Promise<User> =>
  handleAuthResponse(
    safeApiCall(
      get('/api/v1/auth/me', {
        params: { query: {} },
      }),
    ),
  );

interface AuthApi {
  changePassword: (request: ChangePasswordRequest) => Promise<void>;
  confirmPasswordReset: (request: ResetPasswordConfirm) => Promise<void>;
  deleteAccount: () => Promise<void>;
  exchangeCode: (code: string, state: string) => Promise<AuthKitCallbackResponse>;
  getAuthorizationUrl: (screenHint?: string) => Promise<AuthKitAuthorizeResponse>;
  getCurrentUser: () => Promise<User | undefined>;
  logout: () => Promise<void>;
  refresh: () => Promise<AuthResponse>;
  refreshAuthKitToken: (refreshToken: string) => Promise<AuthKitRefreshResponse>;
  requestEmailVerification: () => Promise<void>;
  requestPasswordReset: (request: ResetPasswordRequest) => Promise<void>;
  updateProfile: (updates: UpdateUserProfileRequest) => Promise<User>;
  verifyEmail: (token: string) => Promise<void>;
}

const authApi: AuthApi = {
  changePassword: async (request: ChangePasswordRequest): Promise<void> => {
    await ensureCSRFToken();
    await handleAuthResponse(
      safeApiCall(
        post('/api/v1/auth/change-password', {
          body: request,
        }),
      ),
    );
  },
  confirmPasswordReset: async (request: ResetPasswordConfirm): Promise<void> => {
    await ensureCSRFToken();
    await handleAuthResponse(
      safeApiCall(
        post('/api/v1/auth/reset-password/confirm', {
          body: request,
        }),
      ),
    );
  },
  deleteAccount: async (): Promise<void> => {
    await ensureCSRFToken();
    await handleAuthResponse(
      safeApiCall(
        del('/api/v1/auth/account', {
          params: { query: {} },
        }),
      ),
    );
  },
  exchangeCode: async (code: string, state: string): Promise<AuthKitCallbackResponse> => {
    await ensureCSRFToken();
    return handleAuthResponse(
      safeApiCall(
        post('/api/v1/auth/authkit/callback', {
          body: { code, state },
        }),
      ),
    );
  },
  getAuthorizationUrl: async (screenHint?: string): Promise<AuthKitAuthorizeResponse> => {
    const params: Record<string, string> = {};
    if (screenHint) {
      params['screen_hint'] = screenHint;
    }
    return handleAuthResponse(
      safeApiCall(
        get('/api/v1/auth/authkit/authorize', {
          params: { query: params },
        }),
      ),
    );
  },
  getCurrentUser: async (): Promise<User | undefined> => {
    const token = getStoredToken();
    if (token === undefined) {
      return undefined;
    }
    try {
      return await fetchCurrentUser();
    } catch (error) {
      if (error instanceof AuthError && error.statusCode === authConstants.httpUnauthorized) {
        return undefined;
      }
      throw error;
    }
  },
  logout: async (): Promise<void> => {
    await ensureCSRFToken();
    await handleAuthResponse(
      safeApiCall(
        post('/api/v1/auth/logout', {
          body: {},
        }),
      ),
    );
  },
  refresh: async (): Promise<AuthResponse> => {
    await ensureCSRFToken();
    return handleAuthResponse(
      safeApiCall(
        post('/api/v1/auth/refresh', {
          body: {},
        }),
      ),
    );
  },
  refreshAuthKitToken: async (refreshToken: string): Promise<AuthKitRefreshResponse> => {
    await ensureCSRFToken();
    return handleAuthResponse(
      safeApiCall(
        post('/api/v1/auth/authkit/refresh', {
          body: { refresh_token: refreshToken },
        }),
      ),
    );
  },
  requestEmailVerification: async (): Promise<void> => {
    await ensureCSRFToken();
    await handleAuthResponse(
      safeApiCall(
        post('/api/v1/auth/request-verification', {
          body: {},
        }),
      ),
    );
  },
  requestPasswordReset: async (request: ResetPasswordRequest): Promise<void> => {
    await ensureCSRFToken();
    await handleAuthResponse(
      safeApiCall(
        post('/api/v1/auth/reset-password', {
          body: request,
        }),
      ),
    );
  },
  updateProfile: async (updates: UpdateUserProfileRequest): Promise<User> => {
    await ensureCSRFToken();
    return handleAuthResponse(
      safeApiCall(
        put('/api/v1/auth/profile', {
          body: updates,
        }),
      ),
    );
  },
  verifyEmail: async (token: string): Promise<void> => {
    await ensureCSRFToken();
    await handleAuthResponse(
      safeApiCall(
        post('/api/v1/auth/verify-email', {
          body: { token },
        }),
      ),
    );
  },
};

export { authApi, type AuthApi };
