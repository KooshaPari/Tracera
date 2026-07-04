import { logger } from '@/lib/logger';

import { extractCSRFTokenFromResponse, handleCSRFError } from '../lib/csrf';
import { useConnectionStatusStore } from '../stores/connection-status-store';
import { apiConstants } from './client-constants';

interface ToastAction {
  label: string;
  onClick: () => void;
}

interface ToastOptions {
  action?: ToastAction | undefined;
  description: string;
}

interface IntegrationAuthBody {
  code?: string | undefined;
  detail?: string | undefined;
}

interface RateLimitBody {
  detail?: string | undefined;
  retry_after?: number | undefined;
}

const isRecordObject = (value: unknown): value is Record<string, unknown> =>
  Object.prototype.toString.call(value) === '[object Object]';

const parseJsonObject = async (response: Response): Promise<Record<string, unknown>> => {
  try {
    const data = await response.clone().json();
    if (isRecordObject(data)) {
      return data;
    }
    return {};
  } catch {
    return {};
  }
};

const parseIntegrationAuthBody = async (response: Response): Promise<IntegrationAuthBody> => {
  const data = await parseJsonObject(response);
  const code = typeof data['code'] === 'string' ? data['code'] : undefined;
  const detail = typeof data['detail'] === 'string' ? data['detail'] : undefined;
  return { code, detail };
};

const parseRateLimitBody = async (response: Response): Promise<RateLimitBody> => {
  const data = await parseJsonObject(response);
  const detail = typeof data['detail'] === 'string' ? data['detail'] : undefined;
  const retryAfter = typeof data['retry_after'] === 'number' ? data['retry_after'] : undefined;
  return { detail, retry_after: retryAfter };
};

const showToast = async (
  title: string,
  description: string,
  action?: ToastAction,
): Promise<boolean> => {
  if (!globalThis.window) {
    return false;
  }

  const { toast } = await import('sonner');
  const toastOptions: ToastOptions = { description };
  if (action) {
    toastOptions.action = action;
  }
  toast.error(title, toastOptions);
  return true;
};

const handleCsrf = async (response: Response): Promise<boolean> => {
  if (response.status !== apiConstants.statusForbidden) {
    return false;
  }

  const wasCsrfError = await handleCSRFError(response.clone());
  if (wasCsrfError) {
    logger.warn('[API Client] CSRF token was refreshed, request may need to be retried');
  }
  return wasCsrfError;
};

const showIntegrationAuthToast = async (detail: string): Promise<boolean> =>
  showToast('Connection expired', detail, {
    label: 'Settings',
    onClick: () => {
      if (globalThis.window) {
        globalThis.window.location.href = apiConstants.settingsPath;
      }
    },
  });

const getIntegrationAuthDetail = (body: IntegrationAuthBody): string | null => {
  if (body.code === 'integration_auth_required') {
    return body.detail ?? 'Reconnect this integration in Settings.';
  }
  return null;
};

const isUnauthorizedResponse = (response: Response): boolean =>
  response.status === apiConstants.statusUnauthorized;

const isLoginFailureResponse = (response: Response): boolean =>
  response.url.includes(apiConstants.authLoginPath);

const handleUnauthorizedBody = async (
  response: Response,
  handleLogout: () => void,
): Promise<boolean> => {
  const body = await parseIntegrationAuthBody(response);
  const detail = getIntegrationAuthDetail(body);
  if (detail) {
    return showIntegrationAuthToast(detail);
  }
  logger.warn('[Auth] Session expired or invalid - redirecting to login');
  handleLogout();
  return true;
};

const handleUnauthorized = async (
  response: Response,
  handleLogout: () => void,
): Promise<boolean> => {
  if (!isUnauthorizedResponse(response)) {
    return false;
  }
  if (isLoginFailureResponse(response)) {
    return true;
  }
  return handleUnauthorizedBody(response, handleLogout);
};

const buildRateLimitMessage = (seconds: number): string => {
  if (seconds >= apiConstants.secondsPerMinute) {
    return `Try again in ${Math.ceil(seconds / apiConstants.secondsPerMinute)} minute(s).`;
  }
  return `Try again in ${seconds} second(s).`;
};

const resolveRateLimitSeconds = (retryAfterHeader: string, body: RateLimitBody): number => {
  if (retryAfterHeader !== '') {
    return Number.parseInt(retryAfterHeader, 10);
  }
  return body.retry_after ?? apiConstants.defaultRateLimitSeconds;
};

const buildRateLimitDetail = (seconds: number, body: RateLimitBody): string => {
  const message = buildRateLimitMessage(seconds);
  return body.detail ?? message;
};

const handleRateLimited = async (response: Response): Promise<boolean> => {
  if (response.status !== apiConstants.statusRateLimited) {
    return false;
  }
  const body = await parseRateLimitBody(response);
  const retryAfterHeader = response.headers.get(apiConstants.retryAfterHeader) ?? '';
  const seconds = resolveRateLimitSeconds(retryAfterHeader, body);
  const detail = buildRateLimitDetail(seconds, body);
  await showToast('Rate limited', detail);
  return true;
};

const handleForbidden = async (response: Response, wasCsrfError: boolean): Promise<boolean> => {
  if (response.status === apiConstants.statusForbidden && !wasCsrfError) {
    await showToast('Access denied', "You don't have permission for this action.");
    return true;
  }
  return false;
};

const handleNotFound = async (response: Response): Promise<boolean> => {
  if (response.status !== apiConstants.statusNotFound) {
    return false;
  }
  const body = await parseIntegrationAuthBody(response);
  if (body.code === 'integration_not_found') {
    const detail = body.detail ?? 'The requested item was not found.';
    return showToast('Resource not found', detail);
  }
  return false;
};

const handleServerError = async (response: Response): Promise<boolean> => {
  if (response.status < apiConstants.statusServerError) {
    return false;
  }
  const message = `Backend error ${response.status}`;
  useConnectionStatusStore.getState().setLost(message);
  await showToast('Server error', "Connection issue. We'll retry; check back in a moment.");
  return true;
};

const handleNonCsrfResponses = async (
  response: Response,
  wasCsrfError: boolean,
  handleLogout: () => void,
): Promise<void> => {
  await handleUnauthorized(response, handleLogout);
  await handleRateLimited(response);
  await handleForbidden(response, wasCsrfError);
  await handleNotFound(response);
  await handleServerError(response);
};

const handleResponse = async (response: Response, handleLogout: () => void): Promise<Response> => {
  extractCSRFTokenFromResponse(response);
  const wasCsrfError = await handleCsrf(response);
  await handleNonCsrfResponses(response, wasCsrfError, handleLogout);
  return response;
};

const responseHandlers = {
  handleResponse,
};

export { responseHandlers };
