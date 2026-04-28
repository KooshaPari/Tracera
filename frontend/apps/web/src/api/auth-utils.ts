import type { AuthErrorDetails } from './auth-types';

import { fetchCSRFToken, getCSRFToken } from '../lib/csrf';
import { useAuthStore } from '../stores/auth-store';
import authConstants from './auth-constants';
import { AuthError } from './auth-types';
import { client } from './client';

const isRecordObject = (value: unknown): value is Record<string, unknown> =>
  Object.prototype.toString.call(value) === '[object Object]';

const readStringField = (obj: Record<string, unknown>, key: string): string | undefined => {
  const value = obj[key];
  if (typeof value === 'string') {
    return value;
  }
  return undefined;
};

const readDetailsField = (obj: Record<string, unknown>): AuthErrorDetails | undefined => {
  const value = obj['details'];
  if (isRecordObject(value)) {
    return value;
  }
  return undefined;
};

const buildErrorResult = (
  data: Record<string, unknown>,
): { message: string; code?: string; details?: AuthErrorDetails } => {
  const message = readStringField(data, 'message') ?? '';
  const code = readStringField(data, 'code');
  const details = readDetailsField(data);
  const result: {
    message: string;
    code?: string;
    details?: AuthErrorDetails;
  } = { message };
  if (code !== undefined && code !== '') {
    result.code = code;
  }
  if (details !== undefined) {
    result.details = details;
  }
  return result;
};

const parseErrorData = (
  data: unknown,
): {
  message: string;
  code?: string;
  details?: AuthErrorDetails;
} => {
  if (!isRecordObject(data)) {
    return { message: '' };
  }
  return buildErrorResult(data);
};

const ensureCSRFToken = async (): Promise<string> => {
  let token = normalizeToken(getCSRFToken());
  if (token === undefined) {
    try {
      token = normalizeToken(await fetchCSRFToken());
    } catch (error) {
      let originalError = 'Unknown error';
      if (error instanceof Error) {
        originalError = error.message;
      }
      throw new AuthError(
        'Failed to fetch CSRF token',
        authConstants.httpForbidden,
        'CSRF_TOKEN_MISSING',
        { originalError },
      );
    }
  }
  if (token === undefined) {
    throw new AuthError(
      'CSRF token not available',
      authConstants.httpForbidden,
      'CSRF_TOKEN_MISSING',
    );
  }
  return token;
};

const handleAuthResponse = async <TResponse>(
  promise: Promise<{ data?: TResponse; error?: unknown; response: Response }> | null | undefined,
): Promise<TResponse> => {
  try {
    return await client.handleApiResponse(promise);
  } catch (error) {
    if (error instanceof client.ApiError) {
      const { message, code, details } = parseErrorData(error.data);
      const fallbackMessage = message !== '' ? message : error.message;
      throw new AuthError(fallbackMessage, error.status, code, details);
    }
    throw error;
  }
};

const hasWindow = (): boolean => 'window' in globalThis;

const normalizeToken = (value: unknown): string | undefined => {
  if (typeof value === 'string') {
    const trimmed = value.trim();
    if (trimmed.length === authConstants.emptyLength) {
      return undefined;
    }
    return trimmed;
  }
  if (typeof value === 'number') {
    return String(value);
  }
  return undefined;
};

const getStoredToken = (): string | undefined => {
  const storeToken = useAuthStore.getState().token;
  if (hasWindow()) {
    const storageToken = globalThis.window.localStorage.getItem('auth_token');
    return normalizeToken(storageToken ?? storeToken);
  }
  return normalizeToken(storeToken);
};

const isAuthError = (error: unknown): error is AuthError => error instanceof AuthError;

const getAuthErrorMessage = (error: AuthError): string => {
  const { code } = error;
  const authErrorCodes = [
    'CSRF_TOKEN_MISSING',
    'INVALID_CREDENTIALS',
    'INVALID_PASSWORD',
    'INVALID_TOKEN',
    'PASSWORD_MISMATCH',
    'USER_DISABLED',
    'USER_NOT_FOUND',
  ] as const;

  if (code !== undefined && authErrorCodes.includes(code as any)) {
    return authConstants.authErrorMessages[code as keyof typeof authConstants.authErrorMessages];
  }
  if (error.statusCode === authConstants.httpTooManyRequests) {
    return 'Too many login attempts, please try again later';
  }
  if (error.statusCode >= authConstants.httpServerErrorMin) {
    return 'Server error, please try again later';
  }
  if (error.message !== '') {
    return error.message;
  }
  return 'Authentication failed';
};

export {
  ensureCSRFToken,
  getAuthErrorMessage,
  getStoredToken,
  handleAuthResponse,
  hasWindow,
  isAuthError,
  normalizeToken,
  parseErrorData,
};
