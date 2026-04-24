/**
 * Authentication Helper for k6 Load Tests
 *
 * Provides authentication utilities for WorkOS-based auth flow
 * and session management across load test scenarios.
 */

import http from 'k6/http';
import { check, fail } from 'k6';
import { SharedArray } from 'k6/data';

// Base configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:4000';
const API_BASE_URL = `${BASE_URL}/api/v1`;

// Load test users from environment or use default test users
const TEST_USERS = new SharedArray('users', function () {
  const usersJson = __ENV.TEST_USERS;
  if (usersJson) {
    return JSON.parse(usersJson);
  }

  // Default test users for load testing
  return [
    { email: 'loadtest1@example.com', password: 'LoadTest123!' },
    { email: 'loadtest2@example.com', password: 'LoadTest123!' },
    { email: 'loadtest3@example.com', password: 'LoadTest123!' },
    { email: 'loadtest4@example.com', password: 'LoadTest123!' },
    { email: 'loadtest5@example.com', password: 'LoadTest123!' },
  ];
});

/**
 * Get a test user for the current VU
 * Distributes users across VUs for realistic load patterns
 */
export function getTestUser() {
  const vuId = __VU; // Virtual User ID
  const userIndex = (vuId - 1) % TEST_USERS.length;
  return TEST_USERS[userIndex];
}

/**
 * Perform authentication and return session token
 *
 * @param {Object} user - User credentials { email, password }
 * @returns {Object} - { token, sessionId, userId }
 */
export function authenticate(user) {
  // Step 1: Get CSRF token
  const csrfResponse = http.get(`${API_BASE_URL}/auth/csrf`, {
    tags: { name: 'auth_get_csrf' },
  });

  const csrfCheck = check(csrfResponse, {
    'CSRF token retrieved': (r) => r.status === 200,
    'CSRF token in response': (r) => r.json('csrf_token') !== undefined,
  });

  if (!csrfCheck) {
    fail('Failed to retrieve CSRF token');
  }

  const csrfToken = csrfResponse.json('csrf_token');
  const sessionCookie = csrfResponse.cookies['session'][0].value;

  // Step 2: Authenticate with WorkOS (or mock auth endpoint)
  const authPayload = JSON.stringify({
    email: user.email,
    password: user.password,
  });

  const authResponse = http.post(
    `${API_BASE_URL}/auth/login`,
    authPayload,
    {
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken,
        'Cookie': `session=${sessionCookie}`,
      },
      tags: { name: 'auth_login' },
    }
  );

  const authCheck = check(authResponse, {
    'Login successful': (r) => r.status === 200 || r.status === 201,
    'Auth token received': (r) => r.json('token') !== undefined || r.cookies['auth_token'] !== undefined,
  });

  if (!authCheck) {
    console.error(`Authentication failed for ${user.email}: ${authResponse.status} ${authResponse.body}`);
    fail(`Authentication failed for ${user.email}`);
  }

  // Extract auth token (could be in body or cookie)
  let authToken;
  const bodyToken = authResponse.json('token');
  const cookieToken = authResponse.cookies['auth_token'];

  if (bodyToken) {
    authToken = bodyToken;
  } else if (cookieToken && cookieToken.length > 0) {
    authToken = cookieToken[0].value;
  }

  return {
    token: authToken,
    sessionId: sessionCookie,
    userId: authResponse.json('user_id') || authResponse.json('user.id'),
    csrfToken: csrfToken,
  };
}

/**
 * Create authenticated request headers
 *
 * @param {Object} authData - Authentication data from authenticate()
 * @returns {Object} - Headers object for HTTP requests
 */
export function getAuthHeaders(authData) {
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  if (authData.token) {
    headers['Authorization'] = `Bearer ${authData.token}`;
  }

  if (authData.csrfToken) {
    headers['X-CSRF-Token'] = authData.csrfToken;
  }

  if (authData.sessionId) {
    headers['Cookie'] = `session=${authData.sessionId}`;
  }

  return headers;
}

/**
 * Verify authentication is still valid
 *
 * @param {Object} authData - Authentication data to verify
 * @returns {boolean} - True if auth is valid
 */
export function verifyAuth(authData) {
  const response = http.get(
    `${API_BASE_URL}/auth/verify`,
    {
      headers: getAuthHeaders(authData),
      tags: { name: 'auth_verify' },
    }
  );

  return check(response, {
    'Auth verification successful': (r) => r.status === 200,
  });
}

/**
 * Logout and invalidate session
 *
 * @param {Object} authData - Authentication data to invalidate
 */
export function logout(authData) {
  http.post(
    `${API_BASE_URL}/auth/logout`,
    null,
    {
      headers: getAuthHeaders(authData),
      tags: { name: 'auth_logout' },
    }
  );
}

/**
 * Setup function to be called in test setup()
 * Creates test users if they don't exist
 */
export function setupTestUsers() {
  console.log('Setting up test users for load testing...');

  // This would ideally call an admin endpoint to create test users
  // For now, assumes users exist or uses mock authentication

  return {
    baseUrl: BASE_URL,
    apiBaseUrl: API_BASE_URL,
    userCount: TEST_USERS.length,
  };
}

export default {
  getTestUser,
  authenticate,
  getAuthHeaders,
  verifyAuth,
  logout,
  setupTestUsers,
  BASE_URL,
  API_BASE_URL,
};
