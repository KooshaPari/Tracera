import type { AuthResponse, LoginRequest } from './auth-types';

import { useAuthStore } from '../stores/auth-store';
import { authApi } from './auth-api';
import authConstants from './auth-constants';
import { AuthError } from './auth-types';
import { getAuthErrorMessage, hasWindow, parseErrorData } from './auth-utils';
import { client } from './client';

const apiErrorClass = client.ApiError;

const getLoginErrorMessage = (error: unknown): string => {
  if (error instanceof AuthError) {
    return getAuthErrorMessage(error);
  }
  if (error instanceof apiErrorClass) {
    const { message, code, details } = parseErrorData(error.data);
    const fallbackMessage = message !== '' ? message : error.statusText;
    return getAuthErrorMessage(new AuthError(fallbackMessage, error.status, code, details));
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'Login failed';
};

const loginWithToast = async (credentials: LoginRequest): Promise<AuthResponse> => {
  try {
    return await authApi.login(credentials);
  } catch (error) {
    const message = getLoginErrorMessage(error);
    if (hasWindow()) {
      const { toast } = await import('sonner');
      toast.error('Login failed', { description: message });
    }
    throw error;
  }
};

const loginWithToastStore = async (email: string, password: string): Promise<void> => {
  try {
    await useAuthStore.getState().login(email, password);
  } catch (error) {
    let message = 'Login failed';
    if (error instanceof Error && error.message !== '') {
      ({ message } = error);
    }
    if (hasWindow()) {
      const { toast } = await import('sonner');
      toast.error('Login failed', { description: message });
    }
    throw error;
  }
};

const shouldLogoutOnError = (error: AuthError): boolean =>
  error.statusCode === authConstants.httpUnauthorized ||
  error.code === 'SESSION_EXPIRED' ||
  error.code === 'INVALID_TOKEN';

export { getLoginErrorMessage, loginWithToast, loginWithToastStore, shouldLogoutOnError };
