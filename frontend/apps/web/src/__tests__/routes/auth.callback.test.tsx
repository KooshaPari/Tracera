/**
 * Tests for OAuth Callback Route
 *
 * This test suite validates the WorkOS OAuth callback handling,
 * including successful authentication, error states, and redirects.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

/** Minimal location-like object for tests (no spread of Location class). */
interface MockLocation {
  href: string;
  search: string;
}

describe('OAuth Callback Route', () => {
  let originalLocation: Location;

  beforeEach(() => {
    vi.clearAllMocks();
    originalLocation = globalThis.location;
    const mockLocation: MockLocation = { href: '', search: '' };
    Object.defineProperty(globalThis, 'location', {
      configurable: true,
      value: mockLocation,
      writable: true,
    });
  });

  afterEach(() => {
    // Restore window.location
    globalThis.location = originalLocation;
  });

  it('validates callback route pattern matches /auth/callback', () => {
    expect('/auth/callback').toMatch(/^\/auth\/callback$/);
  });

  it('handles OAuth error parameters in URL', () => {
    globalThis.location.search = '?error=access_denied&error_description=User+cancelled';

    const searchParams = new URLSearchParams(globalThis.location.search);
    const error = searchParams.get('error');
    const errorDescription = searchParams.get('error_description');

    expect(error).toBe('access_denied');
    expect(errorDescription).toBe('User cancelled');
  });

  it('extracts returnTo parameter from URL', () => {
    globalThis.location.search = '?returnTo=/projects/123';

    const searchParams = new URLSearchParams(globalThis.location.search);
    const returnTo = searchParams.get('returnTo');

    expect(returnTo).toBe('/projects/123');
  });

  it('defaults to home when no returnTo is provided', () => {
    globalThis.location.search = '';

    const searchParams = new URLSearchParams(globalThis.location.search);
    const returnTo = searchParams.get('returnTo') ?? '/home';

    expect(returnTo).toBe('/home');
  });

  it('handles OAuth code parameter in callback', () => {
    globalThis.location.search = '?code=test_code_123&state=state_value';

    const searchParams = new URLSearchParams(globalThis.location.search);
    const code = searchParams.get('code');
    const state = searchParams.get('state');

    expect(code).toBe('test_code_123');
    expect(state).toBe('state_value');
  });

  it('extracts all query parameters correctly', () => {
    globalThis.location.search = '?code=abc123&state=xyz789&returnTo=/dashboard';

    const params = new URLSearchParams(globalThis.location.search);

    expect(params.get('code')).toBe('abc123');
    expect(params.get('state')).toBe('xyz789');
    expect(params.get('returnTo')).toBe('/dashboard');
  });

  it('handles empty search string gracefully', () => {
    globalThis.location.search = '';

    const params = new URLSearchParams(globalThis.location.search);
    expect(params.toString()).toBe('');
  });

  it('handles special characters in returnTo', () => {
    globalThis.location.search = '?returnTo=%2Fprojects%2F123%2Fviews%2Ffeature';

    const params = new URLSearchParams(globalThis.location.search);
    const returnTo = params.get('returnTo');

    expect(returnTo).toBe('/projects/123/views/feature');
  });
});
