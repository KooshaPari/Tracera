const authConstants = {
  authErrorMessages: {
    CSRF_TOKEN_MISSING: 'Security token missing, please refresh the page',
    INVALID_CREDENTIALS: 'Invalid email or password',
    INVALID_PASSWORD: 'Current password is incorrect',
    INVALID_TOKEN: 'Invalid or expired token',
    PASSWORD_MISMATCH: 'Passwords do not match',
    USER_DISABLED: 'This account has been disabled',
    USER_NOT_FOUND: 'User not found',
  },
  emptyLength: 0,
  httpForbidden: 403,
  httpServerErrorMin: 500,
  httpTooManyRequests: 429,
  httpUnauthorized: 401,
};

export default authConstants;
