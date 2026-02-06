const apiConstants = {
  apiPathSegment: '/api/',
  authLoginPath: '/auth/login',
  authLoginRedirect: '/auth/login',
  authMePath: '/api/v1/auth/me',
  authTokenKey: 'auth_token',
  contentTypeHeader: 'Content-Type',
  contentTypeJson: 'application/json',
  decimalRadix: 10,
  defaultRateLimitSeconds: 60,
  retryAfterHeader: 'Retry-After',
  secondsPerMinute: 60,
  settingsPath: '/settings',
  statusForbidden: 403,
  statusNotFound: 404,
  statusRateLimited: 429,
  statusServerError: 500,
  statusUnauthorized: 401,
};

export { apiConstants };
