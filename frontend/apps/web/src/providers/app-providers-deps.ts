import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AuthKitProvider, useAuth } from '@workos-inc/authkit-react';
import { Toaster } from 'sonner';

import { logger } from '@/lib/logger';

import { getWebSocketManager } from '../api/websocket';
import AuthKitSync from '../components/auth/auth-kit-sync';
import { initializeCSRF } from '../lib/csrf';
import { useAuthStore } from '../stores/auth-store';
import { useWebSocketStore } from '../stores/websocket-store';

const appProvidersDeps = {
  AuthKitProvider,
  AuthKitSync,
  ReactQueryDevtools,
  Toaster,
  getWebSocketManager,
  initializeCSRF,
  logger,
  useAuth,
  useAuthStore,
  useWebSocketStore,
};

export { appProvidersDeps };
