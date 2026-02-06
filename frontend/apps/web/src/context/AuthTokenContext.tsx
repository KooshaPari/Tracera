import React, { createContext, useContext, useCallback, useState, useEffect } from 'react';
import { logger } from '@/lib/logger';

interface AuthTokenContextType {
  token: string | null;
  setToken: (token: string | null) => void;
  clearToken: () => void;
  getToken: () => string | null;
  isTokenExpired: () => boolean;
  setTokenExpiry: (expiresAt: number) => void;
  getTokenExpiresAt: () => number | null;
}

const AuthTokenContext = createContext<AuthTokenContextType | undefined>(undefined);

const TOKEN_KEY = 'auth_token_secure';
const TOKEN_EXPIRY_KEY = 'auth_token_expiry';

/**
 * AuthTokenProvider - Manages secure token storage in sessionStorage
 *
 * SECURITY FEATURES:
 * - Tokens stored in sessionStorage (cleared when browser closes)
 * - Never stored in localStorage
 * - Never logged to console
 * - Expiry tracking for automatic refresh
 * - React Context for safe multi-tab access
 */
export function AuthTokenProvider({ children }: { children: React.ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [expiresAt, setExpiresAt] = useState<number | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize token from sessionStorage on mount
  useEffect(() => {
    try {
      const storedToken = sessionStorage.getItem(TOKEN_KEY);
      const storedExpiry = sessionStorage.getItem(TOKEN_EXPIRY_KEY);

      if (storedToken) {
        setTokenState(storedToken);
        if (storedExpiry) {
          const expiryNum = parseInt(storedExpiry, 10);
          setExpiresAt(expiryNum);

          // Check if token is already expired
          if (expiryNum < Date.now()) {
            logger.warn('AuthToken: Stored token is expired, clearing');
            sessionStorage.removeItem(TOKEN_KEY);
            sessionStorage.removeItem(TOKEN_EXPIRY_KEY);
            setTokenState(null);
            setExpiresAt(null);
          }
        }
      }
    } catch (error) {
      logger.error('AuthToken: Failed to initialize from storage', error);
    } finally {
      setIsInitialized(true);
    }
  }, []);

  const setToken = useCallback((newToken: string | null) => {
    if (newToken) {
      try {
        // Store in sessionStorage only (not localStorage)
        sessionStorage.setItem(TOKEN_KEY, newToken);
        setTokenState(newToken);
        logger.debug('AuthToken: Token stored securely');
      } catch (error) {
        logger.error('AuthToken: Failed to store token', error);
      }
    } else {
      clearToken();
    }
  }, []);

  const setTokenExpiry = useCallback((expiresAtMs: number) => {
    try {
      sessionStorage.setItem(TOKEN_EXPIRY_KEY, expiresAtMs.toString());
      setExpiresAt(expiresAtMs);
      logger.debug('AuthToken: Token expiry updated');
    } catch (error) {
      logger.error('AuthToken: Failed to store token expiry', error);
    }
  }, []);

  const getToken = useCallback(() => {
    return token;
  }, [token]);

  const getTokenExpiresAt = useCallback(() => {
    return expiresAt;
  }, [expiresAt]);

  const isTokenExpired = useCallback(() => {
    if (!expiresAt) return true;
    return Date.now() >= expiresAt;
  }, [expiresAt]);

  const clearToken = useCallback(() => {
    try {
      sessionStorage.removeItem(TOKEN_KEY);
      sessionStorage.removeItem(TOKEN_EXPIRY_KEY);
      setTokenState(null);
      setExpiresAt(null);
      logger.debug('AuthToken: Token cleared');
    } catch (error) {
      logger.error('AuthToken: Failed to clear token', error);
    }
  }, []);

  const value: AuthTokenContextType = {
    token,
    setToken,
    clearToken,
    getToken,
    isTokenExpired,
    setTokenExpiry,
    getTokenExpiresAt,
  };

  if (!isInitialized) {
    return null; // Wait for initialization
  }

  return (
    <AuthTokenContext.Provider value={value}>
      {children}
    </AuthTokenContext.Provider>
  );
}

/**
 * useAuthToken - Hook to access authentication token context
 *
 * Usage:
 * ```
 * const { token, setToken, isTokenExpired } = useAuthToken();
 * ```
 */
export function useAuthToken(): AuthTokenContextType {
  const context = useContext(AuthTokenContext);
  if (!context) {
    throw new Error('useAuthToken must be used within AuthTokenProvider');
  }
  return context;
}
