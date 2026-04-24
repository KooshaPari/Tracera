/**
 * Authentication API Contract Tests
 *
 * Consumer: TraceRTM-Web
 * Provider: TraceRTM-API
 * Domain: Authentication
 */

import { describe, it, beforeAll, afterAll } from 'vitest';
import {
  createPactProvider,
  setupPact,
  teardownPact,
  like,
  uuid,
  iso8601DateTime,
  errorResponse,
  standardResponse,
  withAuth,
  providerStates,
} from '../setup';

const provider = createPactProvider('TraceRTM-Web-Auth');

describe('Authentication Contract Tests', () => {
  beforeAll(async () => {
    await setupPact(provider);
  });

  afterAll(async () => {
    await teardownPact(provider);
  });

  describe('POST /api/v1/auth/login', () => {
    it('should login with valid credentials', async () => {
      await provider.addInteraction({
        states: [{ description: providerStates.userExists }],
        uponReceiving: 'a login request with valid credentials',
        withRequest: {
          method: 'POST',
          path: '/api/v1/auth/login',
          headers: {
            'Content-Type': 'application/json',
          },
          body: {
            email: 'user@example.com',
            password: 'ValidPassword123!',
          },
        },
        willRespondWith: standardResponse({
          token: like('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'),
          refreshToken: like('refresh-token-abc123'),
          expiresAt: iso8601DateTime(),
          user: {
            id: uuid('user-123'),
            email: like('user@example.com'),
            name: like('Test User'),
            role: like('user'),
            createdAt: iso8601DateTime(),
          },
        }),
      });

      // Test the actual API call
      const response = await fetch('http://localhost:8080/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'user@example.com',
          password: 'ValidPassword123!',
        }),
      });

      const data = await response.json();
      console.assert(response.status === 200, 'Login should return 200');
      console.assert(data.token, 'Response should include token');
      console.assert(data.user.id, 'Response should include user');
    });

    it('should reject invalid credentials', async () => {
      await provider.addInteraction({
        states: [{ description: providerStates.userNotFound }],
        uponReceiving: 'a login request with invalid credentials',
        withRequest: {
          method: 'POST',
          path: '/api/v1/auth/login',
          headers: {
            'Content-Type': 'application/json',
          },
          body: {
            email: 'invalid@example.com',
            password: 'wrongpassword',
          },
        },
        willRespondWith: errorResponse('Invalid credentials', 'INVALID_CREDENTIALS', 401),
      });

      const response = await fetch('http://localhost:8080/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'invalid@example.com',
          password: 'wrongpassword',
        }),
      });

      console.assert(response.status === 401, 'Invalid login should return 401');
    });

    it('should reject malformed request', async () => {
      await provider.addInteraction({
        states: [],
        uponReceiving: 'a login request with missing fields',
        withRequest: {
          method: 'POST',
          path: '/api/v1/auth/login',
          headers: {
            'Content-Type': 'application/json',
          },
          body: {
            email: 'user@example.com',
            // password missing
          },
        },
        willRespondWith: errorResponse('Missing required field: password', 'VALIDATION_ERROR', 400),
      });

      const response = await fetch('http://localhost:8080/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'user@example.com' }),
      });

      console.assert(response.status === 400, 'Malformed request should return 400');
    });
  });

  describe('POST /api/v1/auth/logout', () => {
    it('should logout authenticated user', async () => {
      await provider.addInteraction({
        states: [{ description: providerStates.userAuthenticated }],
        uponReceiving: 'a logout request',
        withRequest: {
          method: 'POST',
          path: '/api/v1/auth/logout',
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          success: like(true),
          message: like('Logged out successfully'),
        }),
      });

      const response = await fetch('http://localhost:8080/api/v1/auth/logout', {
        method: 'POST',
        headers: { Authorization: 'Bearer test-token' },
      });

      console.assert(response.status === 200, 'Logout should return 200');
    });

    it('should reject unauthenticated logout', async () => {
      await provider.addInteraction({
        states: [{ description: providerStates.userUnauthorized }],
        uponReceiving: 'a logout request without authentication',
        withRequest: {
          method: 'POST',
          path: '/api/v1/auth/logout',
          headers: {
            'Content-Type': 'application/json',
          },
        },
        willRespondWith: errorResponse('Authentication required', 'UNAUTHORIZED', 401),
      });

      const response = await fetch('http://localhost:8080/api/v1/auth/logout', {
        method: 'POST',
      });

      console.assert(response.status === 401, 'Unauthenticated logout should return 401');
    });
  });

  describe('GET /api/v1/auth/me', () => {
    it('should return current user info', async () => {
      await provider.addInteraction({
        states: [{ description: providerStates.userAuthenticated }],
        uponReceiving: 'a request for current user info',
        withRequest: {
          method: 'GET',
          path: '/api/v1/auth/me',
          headers: withAuth(),
        },
        willRespondWith: standardResponse({
          id: uuid('user-123'),
          email: like('user@example.com'),
          name: like('Test User'),
          role: like('user'),
          preferences: like({}),
          createdAt: iso8601DateTime(),
          updatedAt: iso8601DateTime(),
        }),
      });

      const response = await fetch('http://localhost:8080/api/v1/auth/me', {
        headers: { Authorization: 'Bearer test-token' },
      });

      const data = await response.json();
      console.assert(response.status === 200, 'Should return 200');
      console.assert(data.email, 'Should include email');
    });

    it('should reject unauthenticated request', async () => {
      await provider.addInteraction({
        states: [{ description: providerStates.userUnauthorized }],
        uponReceiving: 'a request for user info without authentication',
        withRequest: {
          method: 'GET',
          path: '/api/v1/auth/me',
          headers: {
            'Content-Type': 'application/json',
          },
        },
        willRespondWith: errorResponse('Authentication required', 'UNAUTHORIZED', 401),
      });

      const response = await fetch('http://localhost:8080/api/v1/auth/me');

      console.assert(response.status === 401, 'Should return 401');
    });
  });

  describe('POST /api/v1/auth/refresh', () => {
    it('should refresh access token', async () => {
      await provider.addInteraction({
        states: [{ description: 'valid refresh token exists' }],
        uponReceiving: 'a token refresh request',
        withRequest: {
          method: 'POST',
          path: '/api/v1/auth/refresh',
          headers: {
            'Content-Type': 'application/json',
          },
          body: {
            refreshToken: like('refresh-token-abc123'),
          },
        },
        willRespondWith: standardResponse({
          token: like('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'),
          refreshToken: like('new-refresh-token-xyz789'),
          expiresAt: iso8601DateTime(),
        }),
      });

      const response = await fetch('http://localhost:8080/api/v1/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refreshToken: 'refresh-token-abc123' }),
      });

      const data = await response.json();
      console.assert(response.status === 200, 'Should return 200');
      console.assert(data.token, 'Should include new token');
    });

    it('should reject invalid refresh token', async () => {
      await provider.addInteraction({
        states: [{ description: 'invalid refresh token' }],
        uponReceiving: 'a refresh request with invalid token',
        withRequest: {
          method: 'POST',
          path: '/api/v1/auth/refresh',
          headers: {
            'Content-Type': 'application/json',
          },
          body: {
            refreshToken: like('invalid-token'),
          },
        },
        willRespondWith: errorResponse('Invalid refresh token', 'INVALID_TOKEN', 401),
      });

      const response = await fetch('http://localhost:8080/api/v1/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refreshToken: 'invalid-token' }),
      });

      console.assert(response.status === 401, 'Should return 401');
    });
  });

  describe('POST /api/v1/auth/verify', () => {
    it('should verify valid token', async () => {
      await provider.addInteraction({
        states: [{ description: 'valid token exists' }],
        uponReceiving: 'a token verification request',
        withRequest: {
          method: 'POST',
          path: '/api/v1/auth/verify',
          headers: {
            'Content-Type': 'application/json',
          },
          body: {
            token: like('valid-token-abc123'),
          },
        },
        willRespondWith: standardResponse({
          valid: like(true),
          userId: uuid('user-123'),
          expiresAt: iso8601DateTime(),
        }),
      });

      const response = await fetch('http://localhost:8080/api/v1/auth/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: 'valid-token-abc123' }),
      });

      const data = await response.json();
      console.assert(response.status === 200, 'Should return 200');
      console.assert(data.valid === true, 'Token should be valid');
    });

    it('should reject invalid token', async () => {
      await provider.addInteraction({
        states: [{ description: 'invalid token' }],
        uponReceiving: 'a verification request with invalid token',
        withRequest: {
          method: 'POST',
          path: '/api/v1/auth/verify',
          headers: {
            'Content-Type': 'application/json',
          },
          body: {
            token: like('invalid-token'),
          },
        },
        willRespondWith: standardResponse({
          valid: like(false),
          reason: like('Token expired'),
        }),
      });

      const response = await fetch('http://localhost:8080/api/v1/auth/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: 'invalid-token' }),
      });

      const data = await response.json();
      console.assert(response.status === 200, 'Should return 200');
      console.assert(data.valid === false, 'Token should be invalid');
    });
  });

  describe('GET /api/v1/csrf-token', () => {
    it('should return CSRF token', async () => {
      await provider.addInteraction({
        states: [],
        uponReceiving: 'a request for CSRF token',
        withRequest: {
          method: 'GET',
          path: '/api/v1/csrf-token',
          headers: {
            'Content-Type': 'application/json',
          },
        },
        willRespondWith: standardResponse({
          token: like('csrf-token-abc123'),
          expiresAt: iso8601DateTime(),
        }),
      });

      const response = await fetch('http://localhost:8080/api/v1/csrf-token');

      const data = await response.json();
      console.assert(response.status === 200, 'Should return 200');
      console.assert(data.token, 'Should include CSRF token');
    });
  });
});
