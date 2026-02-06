import { renderHook, act } from '@testing-library/react';

import { AuthTokenProvider, useAuthToken } from './AuthTokenContext';

describe('AuthTokenContext', () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it('should initialize with no token', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthTokenProvider>{children}</AuthTokenProvider>
    );

    const { result } = renderHook(() => useAuthToken(), { wrapper });

    expect(result.current.getToken()).toBeNull();
    expect(result.current.isTokenExpired()).toBeTruthy();
  });

  it('should store token in sessionStorage', async () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthTokenProvider>{children}</AuthTokenProvider>
    );

    const { result } = renderHook(() => useAuthToken(), { wrapper });
    const testToken = 'test-token-123';

    await act(async () => {
      result.current.setToken(testToken);
    });

    expect(result.current.getToken()).toBe(testToken);
    expect(sessionStorage.getItem('auth_token_secure')).toBe(testToken);
  });

  it('should not store token in localStorage', async () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthTokenProvider>{children}</AuthTokenProvider>
    );

    const { result } = renderHook(() => useAuthToken(), { wrapper });
    const testToken = 'test-token-123';

    await act(async () => {
      result.current.setToken(testToken);
    });

    expect(localStorage.getItem('auth_token_secure')).toBeNull();
    expect(localStorage.getItem('auth_token')).toBeNull();
  });

  it('should track token expiry', async () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthTokenProvider>{children}</AuthTokenProvider>
    );

    const { result } = renderHook(() => useAuthToken(), { wrapper });
    const testToken = 'test-token-123';
    const futureExpiry = Date.now() + 60 * 60 * 1000; // 1 hour from now

    await act(async () => {
      result.current.setToken(testToken);
      result.current.setTokenExpiry(futureExpiry);
    });

    expect(result.current.getTokenExpiresAt()).toBe(futureExpiry);
    expect(result.current.isTokenExpired()).toBeFalsy();
  });

  it('should detect expired tokens', async () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthTokenProvider>{children}</AuthTokenProvider>
    );

    const { result } = renderHook(() => useAuthToken(), { wrapper });
    const testToken = 'test-token-123';
    const pastExpiry = Date.now() - 1000; // 1 second ago

    await act(async () => {
      result.current.setToken(testToken);
      result.current.setTokenExpiry(pastExpiry);
    });

    expect(result.current.isTokenExpired()).toBeTruthy();
  });

  it('should clear token and expiry', async () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthTokenProvider>{children}</AuthTokenProvider>
    );

    const { result } = renderHook(() => useAuthToken(), { wrapper });
    const testToken = 'test-token-123';

    await act(async () => {
      result.current.setToken(testToken);
      result.current.setTokenExpiry(Date.now() + 3_600_000);
    });

    expect(result.current.getToken()).toBe(testToken);

    await act(async () => {
      result.current.clearToken();
    });

    expect(result.current.getToken()).toBeNull();
    expect(result.current.getTokenExpiresAt()).toBeNull();
    expect(sessionStorage.getItem('auth_token_secure')).toBeNull();
  });

  it('should recover from corrupted sessionStorage', async () => {
    // Simulate corrupted sessionStorage
    sessionStorage.setItem('auth_token_secure', 'valid-token');
    sessionStorage.setItem('auth_token_expiry', 'invalid-expiry');

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthTokenProvider>{children}</AuthTokenProvider>
    );

    const { result } = renderHook(() => useAuthToken(), { wrapper });

    // Should recover gracefully
    expect(result.current.getToken()).toBe('valid-token');
  });

  it('should auto-clear expired stored tokens on init', async () => {
    // Pre-populate sessionStorage with expired token
    const expiredTime = Date.now() - 1000; // 1 second ago
    sessionStorage.setItem('auth_token_secure', 'expired-token');
    sessionStorage.setItem('auth_token_expiry', expiredTime.toString());

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthTokenProvider>{children}</AuthTokenProvider>
    );

    const { result } = renderHook(() => useAuthToken(), { wrapper });

    expect(result.current.getToken()).toBeNull();
    expect(sessionStorage.getItem('auth_token_secure')).toBeNull();
  });

  it('should handle multiple setToken calls', async () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthTokenProvider>{children}</AuthTokenProvider>
    );

    const { result } = renderHook(() => useAuthToken(), { wrapper });

    await act(async () => {
      result.current.setToken('token-1');
    });
    expect(result.current.getToken()).toBe('token-1');

    await act(async () => {
      result.current.setToken('token-2');
    });
    expect(result.current.getToken()).toBe('token-2');

    expect(sessionStorage.getItem('auth_token_secure')).toBe('token-2');
  });

  it('should throw error when used outside provider', () => {
    const { result } = renderHook(() => useAuthToken());

    expect(result.error).toEqual(Error('useAuthToken must be used within AuthTokenProvider'));
  });
});
