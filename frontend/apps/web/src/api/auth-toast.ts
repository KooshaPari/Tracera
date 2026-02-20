import { useAuthStore } from '../stores/auth-store';
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
  return 'Authentication failed';
};

const redirectToAuthKitWithToast = async (screenHint?: string): Promise<void> => {
  try {
    await useAuthStore.getState().redirectToAuthKit(screenHint);
  } catch (error) {
    const message = getLoginErrorMessage(error);
    if (hasWindow()) {
      const { toast } = await import('sonner');
      toast.error('Authentication failed', { description: message });
    }
    throw error;
  }
};

const loginWithCodeAndToast = async (code: string, state: string): Promise<void> => {
  try {
    await useAuthStore.getState().loginWithCode(code, state);
  } catch (error) {
    const message = getLoginErrorMessage(error);
    if (hasWindow()) {
      const { toast } = await import('sonner');
      toast.error('Authentication failed', { description: message });
    }
    throw error;
  }
};

const shouldLogoutOnError = (error: AuthError): boolean =>
  error.statusCode === authConstants.httpUnauthorized ||
  error.code === 'SESSION_EXPIRED' ||
  error.code === 'INVALID_TOKEN';

export {
  getLoginErrorMessage,
  loginWithCodeAndToast,
  redirectToAuthKitWithToast,
  shouldLogoutOnError,
};
